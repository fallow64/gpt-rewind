#!/usr/bin/env python3
"""
ChatGPT Conversation Embedding Generator using GTE-Large (OPTIMIZED)

Optimizations:
- torch.inference_mode() for faster inference
- Mixed precision (float16) on GPU
- Reduced CPU/GPU synchronization
- Minimal printing and progress updates
- Pre-allocated tensors where possible
- Efficient batch processing
- Preserves message IDs throughout processing
"""

import json
import torch
import torch.nn.functional as F
from torch import Tensor
from transformers import AutoTokenizer, AutoModel
from typing import Dict, List, Any
import sys
from datetime import datetime


def average_pool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
    """Average pooling over token embeddings."""
    last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]


class GTELargeGenerator:
    """Wrapper for GTE-Large model with GPU acceleration and optimization."""
    
    def __init__(self, model_name: str = "thenlper/gte-large", max_length: int = 512):
        """Initialize GTE-Large model with optimizations."""
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.use_amp = self.device == 'cuda'  # Use mixed precision on GPU
        
        print(f"Device: {self.device}", end='')
        if self.device == 'cuda':
            print(f" ({torch.cuda.get_device_name(0)})")
        else:
            print()
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        
        if self.device == 'cuda':
            self.model = self.model.cuda()
            # Convert to float16 for faster inference
            self.model = self.model.half()
        
        self.model.eval()
        self.max_length = max_length
    
    def encode(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Encode texts with optimized inference.
        
        Args:
            texts: List of texts to encode
            batch_size: Batch size for processing
        
        Returns:
            List of normalized embedding vectors
        """
        if not texts:
            return []
        
        all_embeddings = []
        
        # Use inference_mode for optimal performance
        with torch.inference_mode():
            # Process in batches
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                # Tokenize
                batch_dict = self.tokenizer(
                    batch_texts,
                    max_length=self.max_length,
                    padding=True,
                    truncation=True,
                    return_tensors='pt'
                )
                
                # Move to device
                if self.device == 'cuda':
                    batch_dict = {k: v.cuda() for k, v in batch_dict.items()}
                
                # Generate embeddings with mixed precision
                if self.use_amp:
                    with torch.autocast(device_type='cuda', dtype=torch.float16):
                        outputs = self.model(**batch_dict)
                        embeddings = average_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
                else:
                    outputs = self.model(**batch_dict)
                    embeddings = average_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
                
                # Normalize embeddings (convert to float32 for precision)
                embeddings = F.normalize(embeddings.float(), p=2, dim=1)
                
                # Convert to list - minimize CPU/GPU sync by batching this operation
                batch_embeddings = embeddings.cpu().tolist()
                all_embeddings.extend(batch_embeddings)
        
        return all_embeddings


def collect_all_texts_and_locations(compressed_data: Dict[str, Any]) -> tuple:
    """Collect all text content and their locations in the data structure."""
    all_texts = []
    all_locations = []
    
    # Collect from by_month
    for month in compressed_data.get('by_month', {}).keys():
        convs = compressed_data['by_month'][month]
        for conv_id in convs.keys():
            msg_groups = convs[conv_id]
            for group_idx, msg_group in enumerate(msg_groups):
                for msg_idx, msg in enumerate(msg_group):
                    cleaned_content = msg.get('cleaned_content', [])
                    for content_idx, content in enumerate(cleaned_content):
                        if content:
                            all_texts.append(content)
                            all_locations.append({
                                'month': month,
                                'conv_id': conv_id,
                                'group_idx': group_idx,
                                'msg_idx': msg_idx,
                                'content_idx': content_idx
                            })
    
    return all_texts, all_locations


def apply_embeddings_to_data(compressed_data: Dict[str, Any], locations: List[Dict], embeddings: List[List[float]]) -> Dict[str, Any]:
    """
    Apply generated embeddings back to the original data structure.
    Preserves all existing message fields including 'id', 'content', 'cleaned_content', etc.
    """
    # Initialize embeddings field for all messages (preserve existing fields)
    for month in compressed_data.get('by_month', {}).keys():
        convs = compressed_data['by_month'][month]
        for conv_id in convs.keys():
            msg_groups = convs[conv_id]
            for group_idx, msg_group in enumerate(msg_groups):
                for msg_idx, msg in enumerate(msg_group):
                    # Only initialize if not already present
                    if 'embeddings' not in msg:
                        msg['embeddings'] = [[] for _ in msg.get('cleaned_content', [])]
    
    # Apply embeddings using location information
    for loc, embedding in zip(locations, embeddings):
        msg = compressed_data['by_month'][loc['month']][loc['conv_id']][loc['group_idx']][loc['msg_idx']]
        msg['embeddings'][loc['content_idx']] = embedding
    
    return compressed_data


def process_compressed_data(compressed_data: Dict[str, Any], embedder: GTELargeGenerator, batch_size: int = 32) -> Dict[str, Any]:
    """Process all compressed conversation data and add embeddings."""
    # Collect all texts
    all_texts, all_locations = collect_all_texts_and_locations(compressed_data)
    total_texts = len(all_texts)
    
    print(f"Text segments: {total_texts:,}")
    print(f"Batch size: {batch_size}")
    
    # Generate embeddings in batches with minimal progress output
    all_embeddings = []
    total_batches = (total_texts + batch_size - 1) // batch_size
    print_every = max(1, total_batches // 20)  # Print ~20 updates max
    
    print("Generating embeddings...", flush=True)
    
    for i in range(0, total_texts, batch_size):
        batch_texts = all_texts[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        # Generate embeddings for batch
        batch_embeddings = embedder.encode(batch_texts, batch_size=len(batch_texts))
        all_embeddings.extend(batch_embeddings)
        
        # Minimal progress updates
        if batch_num % print_every == 0 or batch_num == total_batches:
            progress = (min(i + batch_size, total_texts) / total_texts) * 100
            print(f"  {progress:.0f}% ({min(i + batch_size, total_texts):,}/{total_texts:,})", flush=True)
    
    # Apply embeddings back to data structure (preserves message IDs)
    compressed_data = apply_embeddings_to_data(compressed_data, all_locations, all_embeddings)
    
    return compressed_data


def main():
    print("=" * 60)
    print("Embedding Generator (GTE-Large) - OPTIMIZED")
    print("=" * 60)
    
    # Load compressed data
    input_file = 'compressed_conversations.json'
    print(f"Loading {input_file}...", flush=True)
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            compressed_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {input_file} not found!")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}")
        sys.exit(1)
    
    # Verify message IDs are present
    sample_checked = False
    for month in list(compressed_data.get('by_month', {}).keys())[:1]:
        for conv_id in list(compressed_data['by_month'][month].keys())[:1]:
            for msg_group in compressed_data['by_month'][month][conv_id][:1]:
                for msg in msg_group[:1]:
                    if 'id' in msg:
                        print(f"✓ Message IDs detected (sample: {msg['id'][:30]}...)")
                        sample_checked = True
                    else:
                        print("⚠ Warning: No message IDs found in data")
                    break
                if sample_checked:
                    break
            if sample_checked:
                break
        if sample_checked:
            break
    
    # Initialize embedder
    try:
        embedder = GTELargeGenerator(max_length=512)
    except Exception as e:
        print(f"Error initializing model: {e}")
        sys.exit(1)
    
    # Configure batch size
    batch_size = 256 if torch.cuda.is_available() else 32
    
    # Process data
    start_time = datetime.now()
    print(f"\nStarted: {start_time.strftime('%H:%M:%S')}")
    print("-" * 60)
    
    embedded_data = process_compressed_data(compressed_data, embedder, batch_size=batch_size)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("-" * 60)
    print(f"Completed: {end_time.strftime('%H:%M:%S')}")
    print(f"Duration: {duration:.1f}s ({duration/60:.1f} min)")
    
    # Add embedding metadata
    embedded_data['metadata']['embedding_model'] = 'thenlper/gte-large'
    embedded_data['metadata']['embedding_generated_at'] = end_time.strftime('%Y-%m-%d %H:%M:%S')
    embedded_data['metadata']['embedding_device'] = embedder.device
    embedded_data['metadata']['embedding_duration_seconds'] = duration
    embedded_data['metadata']['embedding_batch_size'] = batch_size
    embedded_data['metadata']['embedding_max_length'] = embedder.max_length
    embedded_data['metadata']['embedding_precision'] = 'float16' if embedder.use_amp else 'float32'
    
    # Save output
    output_file = 'embedded_conversations.json'
    print(f"\nSaving to {output_file}...", flush=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(embedded_data, f, indent=2, ensure_ascii=False)
    
    print("✓ Done")
    print("=" * 60)
    print(f"Model: GTE-Large | Device: {embedder.device}")
    print(f"Precision: {'FP16' if embedder.use_amp else 'FP32'} | Batch: {batch_size}")
    print(f"Time: {duration:.1f}s | Output: {output_file}")
    print(f"Message IDs: Preserved ✓")
    print("=" * 60)


if __name__ == '__main__':
    main()