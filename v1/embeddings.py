#!/usr/bin/env python3
"""
ChatGPT Conversation Embedding Generator using GTE-Large

This script processes compressed conversation data and generates embeddings for each message object.
Uses GPU acceleration with gte-large model via transformers.
Processes sequentially with batch processing for GPU efficiency.
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
    """
    Average pooling over token embeddings.
    
    Args:
        last_hidden_states: Last hidden states from model
        attention_mask: Attention mask
    
    Returns:
        Pooled embeddings
    """
    last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]


class GTELargeGenerator:
    """Wrapper for GTE-Large model with GPU acceleration."""
    
    def __init__(self, model_name: str = "thenlper/gte-large", max_length: int = 512):
        """
        Initialize GTE-Large model using transformers.
        
        Args:
            model_name: HuggingFace model identifier
            max_length: Maximum sequence length
        """
        print(f"Initializing GTE-Large model: {model_name}")
        
        # Check device
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {self.device}")
        
        if self.device == 'cuda':
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        
        # Load tokenizer and model
        print("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        print("Loading model...")
        self.model = AutoModel.from_pretrained(model_name)
        if self.device == 'cuda':
            self.model = self.model.cuda()
        
        self.model.eval()
        self.max_length = max_length
        
        print("Model loaded successfully!\n")
    
    def encode(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Encode texts using GTE-Large with average pooling.
        
        Args:
            texts: List of texts to encode
            batch_size: Batch size for processing
        
        Returns:
            List of normalized embedding vectors
        """
        if not texts:
            return []
        
        all_embeddings = []
        
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
            
            # Generate embeddings
            with torch.no_grad():
                outputs = self.model(**batch_dict)
                embeddings = average_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
                
                # Normalize embeddings
                embeddings = F.normalize(embeddings, p=2, dim=1)
            
            # Convert to list and collect
            batch_embeddings = embeddings.cpu().tolist()
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings


def collect_all_texts_and_locations(compressed_data: Dict[str, Any]) -> tuple:
    """
    Collect all text content and their locations in the data structure.
    
    Returns:
        Tuple of (texts_list, locations_list) where locations track where each text belongs
    """
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
                                'section': 'by_month',
                                'month': month,
                                'conv_id': conv_id,
                                'group_idx': group_idx,
                                'msg_idx': msg_idx,
                                'content_idx': content_idx
                            })
    
    # Collect from by_hour
    for hour in compressed_data.get('by_hour', {}).keys():
        convs = compressed_data['by_hour'][hour]
        for conv_id in convs.keys():
            msg_groups = convs[conv_id]
            for group_idx, msg_group in enumerate(msg_groups):
                for msg_idx, msg in enumerate(msg_group):
                    cleaned_content = msg.get('cleaned_content', [])
                    for content_idx, content in enumerate(cleaned_content):
                        if content:
                            all_texts.append(content)
                            all_locations.append({
                                'section': 'by_hour',
                                'hour': hour,
                                'conv_id': conv_id,
                                'group_idx': group_idx,
                                'msg_idx': msg_idx,
                                'content_idx': content_idx
                            })
    
    return all_texts, all_locations


def apply_embeddings_to_data(compressed_data: Dict[str, Any], locations: List[Dict], embeddings: List[List[float]]) -> Dict[str, Any]:
    """
    Apply generated embeddings back to the original data structure.
    
    Args:
        compressed_data: Original data structure
        locations: Location information for each embedding
        embeddings: Generated embeddings
    
    Returns:
        Data structure with embeddings added
    """
    # Initialize embeddings field for all messages
    for month in compressed_data.get('by_month', {}).keys():
        convs = compressed_data['by_month'][month]
        for conv_id in convs.keys():
            msg_groups = convs[conv_id]
            for group_idx, msg_group in enumerate(msg_groups):
                for msg_idx, msg in enumerate(msg_group):
                    msg['embeddings'] = [[] for _ in msg.get('cleaned_content', [])]
    
    for hour in compressed_data.get('by_hour', {}).keys():
        convs = compressed_data['by_hour'][hour]
        for conv_id in convs.keys():
            msg_groups = convs[conv_id]
            for group_idx, msg_group in enumerate(msg_groups):
                for msg_idx, msg in enumerate(msg_group):
                    msg['embeddings'] = [[] for _ in msg.get('cleaned_content', [])]
    
    # Apply embeddings using location information
    for loc, embedding in zip(locations, embeddings):
        if loc['section'] == 'by_month':
            msg = compressed_data['by_month'][loc['month']][loc['conv_id']][loc['group_idx']][loc['msg_idx']]
            msg['embeddings'][loc['content_idx']] = embedding
        elif loc['section'] == 'by_hour':
            msg = compressed_data['by_hour'][loc['hour']][loc['conv_id']][loc['group_idx']][loc['msg_idx']]
            msg['embeddings'][loc['content_idx']] = embedding
    
    return compressed_data


def process_compressed_data(compressed_data: Dict[str, Any], embedder: GTELargeGenerator, batch_size: int = 32) -> Dict[str, Any]:
    """
    Process all compressed conversation data and add embeddings using batch processing.
    
    Args:
        compressed_data: Loaded compressed conversations data
        embedder: GTELargeGenerator instance
        batch_size: Number of texts to process per batch
    
    Returns:
        Data with embeddings added
    """
    print("Collecting all text content...")
    all_texts, all_locations = collect_all_texts_and_locations(compressed_data)
    total_texts = len(all_texts)
    
    print(f"Total text segments to embed: {total_texts}")
    print(f"Batch size: {batch_size}\n")
    
    # Generate embeddings in batches
    print("Generating embeddings in batches...")
    all_embeddings = []
    
    for i in range(0, total_texts, batch_size):
        batch_texts = all_texts[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_texts + batch_size - 1) // batch_size
        
        print(f"  Processing batch {batch_num}/{total_batches} ({len(batch_texts)} texts)...")
        
        # Generate embeddings for batch
        batch_embeddings = embedder.encode(batch_texts, batch_size=len(batch_texts))
        all_embeddings.extend(batch_embeddings)
        
        # Progress indicator
        processed = min(i + batch_size, total_texts)
        progress = (processed / total_texts) * 100
        print(f"    Progress: {processed}/{total_texts} ({progress:.1f}%)")
    
    print(f"\n✓ Generated {len(all_embeddings)} embeddings\n")
    
    # Apply embeddings back to data structure
    print("Applying embeddings to data structure...")
    compressed_data = apply_embeddings_to_data(compressed_data, all_locations, all_embeddings)
    
    print("✓ Embeddings applied successfully\n")
    
    return compressed_data


def main():
    print("=" * 80)
    print("ChatGPT Conversation Embedding Generator (GTE-Large)")
    print("=" * 80)
    print()
    
    # Check for GPU
    if not torch.cuda.is_available():
        print("WARNING: CUDA is not available. This script is designed to use GPU.")
        response = input("Continue with CPU? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(0)
    
    # Load compressed data
    input_file = 'compressed_conversations.json'
    print(f"Loading {input_file}...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            compressed_data = json.load(f)
        print(f"✓ Loaded compressed data\n")
    except FileNotFoundError:
        print(f"Error: {input_file} not found!")
        print("Please run compression.py first to generate the compressed data.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {input_file}: {e}")
        sys.exit(1)
    
    # Initialize embedder
    print("Initializing GTE-Large model...")
    print("-" * 80)
    
    try:
        embedder = GTELargeGenerator(max_length=512)
    except Exception as e:
        print(f"Error initializing model: {e}")
        print("\nNote: Make sure you have the required packages installed:")
        print("  pip install torch transformers")
        sys.exit(1)
    
    print("-" * 80)
    print()
    
    # Configure batch size based on GPU availability
    if torch.cuda.is_available():
        batch_size = 128
        print(f"Using CPU with batch size: {batch_size}\n")
    
    # Process data
    start_time = datetime.now()
    print(f"Starting embedding generation at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    print()
    
    embedded_data = process_compressed_data(compressed_data, embedder, batch_size=batch_size)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("-" * 80)
    print(f"Embedding generation completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total time: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    print()
    
    # Add embedding metadata
    embedded_data['metadata']['embedding_model'] = 'thenlper/gte-large'
    embedded_data['metadata']['embedding_generated_at'] = end_time.strftime('%Y-%m-%d %H:%M:%S')
    embedded_data['metadata']['embedding_device'] = embedder.device
    embedded_data['metadata']['embedding_duration_seconds'] = duration
    embedded_data['metadata']['embedding_batch_size'] = batch_size
    embedded_data['metadata']['embedding_max_length'] = embedder.max_length
    
    # Save output
    output_file = 'embedded_conversations.json'
    print(f"Writing embedded data to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(embedded_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Successfully saved to {output_file}")
    print()
    print("=" * 80)
    print("Summary:")
    print(f"  - Model: GTE-Large (thenlper/gte-large)")
    print(f"  - Device: {embedder.device}")
    print(f"  - Max length: {embedder.max_length}")
    print(f"  - Batch size: {batch_size}")
    print(f"  - Processing time: {duration:.2f}s ({duration/60:.2f} min)")
    print(f"  - Output file: {output_file}")
    print("=" * 80)


if __name__ == '__main__':
    main()



def collect_all_texts_and_locations(compressed_data: Dict[str, Any]) -> tuple:
    """
    Collect all text content and their locations in the data structure.
    
    Returns:
        Tuple of (texts_list, locations_list) where locations track where each text belongs
    """
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
                                'section': 'by_month',
                                'month': month,
                                'conv_id': conv_id,
                                'group_idx': group_idx,
                                'msg_idx': msg_idx,
                                'content_idx': content_idx
                            })
    
    # Collect from by_hour
    for hour in compressed_data.get('by_hour', {}).keys():
        convs = compressed_data['by_hour'][hour]
        for conv_id in convs.keys():
            msg_groups = convs[conv_id]
            for group_idx, msg_group in enumerate(msg_groups):
                for msg_idx, msg in enumerate(msg_group):
                    cleaned_content = msg.get('cleaned_content', [])
                    for content_idx, content in enumerate(cleaned_content):
                        if content:
                            all_texts.append(content)
                            all_locations.append({
                                'section': 'by_hour',
                                'hour': hour,
                                'conv_id': conv_id,
                                'group_idx': group_idx,
                                'msg_idx': msg_idx,
                                'content_idx': content_idx
                            })
    
    return all_texts, all_locations


def apply_embeddings_to_data(compressed_data: Dict[str, Any], locations: List[Dict], embeddings: List[List[float]]) -> Dict[str, Any]:
    """
    Apply generated embeddings back to the original data structure.
    
    Args:
        compressed_data: Original data structure
        locations: Location information for each embedding
        embeddings: Generated embeddings
    
    Returns:
        Data structure with embeddings added
    """
    # Initialize embeddings field for all messages
    for month in compressed_data.get('by_month', {}).keys():
        convs = compressed_data['by_month'][month]
        for conv_id in convs.keys():
            msg_groups = convs[conv_id]
            for group_idx, msg_group in enumerate(msg_groups):
                for msg_idx, msg in enumerate(msg_group):
                    msg['embeddings'] = [[] for _ in msg.get('cleaned_content', [])]
    
    for hour in compressed_data.get('by_hour', {}).keys():
        convs = compressed_data['by_hour'][hour]
        for conv_id in convs.keys():
            msg_groups = convs[conv_id]
            for group_idx, msg_group in enumerate(msg_groups):
                for msg_idx, msg in enumerate(msg_group):
                    msg['embeddings'] = [[] for _ in msg.get('cleaned_content', [])]
    
    # Apply embeddings using location information
    for loc, embedding in zip(locations, embeddings):
        if loc['section'] == 'by_month':
            msg = compressed_data['by_month'][loc['month']][loc['conv_id']][loc['group_idx']][loc['msg_idx']]
            msg['embeddings'][loc['content_idx']] = embedding
        elif loc['section'] == 'by_hour':
            msg = compressed_data['by_hour'][loc['hour']][loc['conv_id']][loc['group_idx']][loc['msg_idx']]
            msg['embeddings'][loc['content_idx']] = embedding
    
    return compressed_data


def process_compressed_data(compressed_data: Dict[str, Any], embedder: GTELargeGenerator, batch_size: int = 32) -> Dict[str, Any]:
    """
    Process all compressed conversation data and add embeddings using batch processing.
    
    Args:
        compressed_data: Loaded compressed conversations data
        embedder: NVEmbedV2Generator instance
        batch_size: Number of texts to process per batch
    
    Returns:
        Data with embeddings added
    """
    print("Collecting all text content...")
    all_texts, all_locations = collect_all_texts_and_locations(compressed_data)
    total_texts = len(all_texts)
    
    print(f"Total text segments to embed: {total_texts}")
    print(f"Batch size: {batch_size}\n")
    
    # Generate all embeddings at once using model's batching
    print("Generating embeddings...")
    all_embeddings = embedder.encode(all_texts, batch_size=batch_size)
    
    print(f"✓ Generated {len(all_embeddings)} embeddings\n")
    
    # Apply embeddings back to data structure
    print("Applying embeddings to data structure...")
    compressed_data = apply_embeddings_to_data(compressed_data, all_locations, all_embeddings)
    
    print("✓ Embeddings applied successfully\n")
    
    return compressed_data


def main():
    print("=" * 80)
    print("ChatGPT Conversation Embedding Generator (NV-Embed-v2)")
    print("=" * 80)
    print()
    
    # Check for GPU
    if not torch.cuda.is_available():
        print("WARNING: CUDA is not available. This script is designed to use GPU.")
        response = input("Continue with CPU? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(0)
    
    # Load compressed data
    input_file = 'compressed_conversations.json'
    print(f"Loading {input_file}...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            compressed_data = json.load(f)
        print(f"✓ Loaded compressed data\n")
    except FileNotFoundError:
        print(f"Error: {input_file} not found!")
        print("Please run compression.py first to generate the compressed data.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {input_file}: {e}")
        sys.exit(1)
    
    # Initialize embedder
    print("Initializing NV-Embed-v2 model...")
    print("-" * 80)
    
    try:
        embedder = NVEmbedV2Generator(max_length=512)
    except Exception as e:
        print(f"Error initializing model: {e}")
        print("\nNote: Make sure you have the required packages installed:")
        print("  pip install torch transformers")
        sys.exit(1)
    
    print("-" * 80)
    print()
    
    # Configure batch size based on GPU availability
    if torch.cuda.is_available():
        # Get GPU memory and set appropriate batch size
        gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
        if gpu_memory_gb >= 24:
            batch_size = 64
        elif gpu_memory_gb >= 16:
            batch_size = 48
        elif gpu_memory_gb >= 12:
            batch_size = 32
        elif gpu_memory_gb >= 8:
            batch_size = 24
        else:
            batch_size = 16
        print(f"GPU Memory: {gpu_memory_gb:.2f} GB")
        print(f"Using batch size: {batch_size}\n")
    else:
        batch_size = 8
        print(f"Using CPU with batch size: {batch_size}\n")
    
    # Process data
    start_time = datetime.now()
    print(f"Starting embedding generation at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    print()
    
    embedded_data = process_compressed_data(compressed_data, embedder, batch_size=batch_size)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("-" * 80)
    print(f"Embedding generation completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total time: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    print()
    
    # Add embedding metadata
    embedded_data['metadata']['embedding_model'] = 'nvidia/NV-Embed-v2'
    embedded_data['metadata']['embedding_generated_at'] = end_time.strftime('%Y-%m-%d %H:%M:%S')
    embedded_data['metadata']['embedding_device'] = embedder.device
    embedded_data['metadata']['embedding_duration_seconds'] = duration
    embedded_data['metadata']['embedding_batch_size'] = batch_size
    embedded_data['metadata']['embedding_max_length'] = embedder.max_length
    
    # Save output
    output_file = 'embedded_conversations.json'
    print(f"Writing embedded data to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(embedded_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Successfully saved to {output_file}")
    print()
    print("=" * 80)
    print("Summary:")
    print(f"  - Model: NV-Embed-v2")
    print(f"  - Device: {embedder.device}")
    print(f"  - Max length: {embedder.max_length}")
    print(f"  - Batch size: {batch_size}")
    print(f"  - Processing time: {duration:.2f}s ({duration/60:.2f} min)")
    print(f"  - Output file: {output_file}")
    print("=" * 80)


if __name__ == '__main__':
    main()



def collect_all_texts_and_locations(compressed_data: Dict[str, Any]) -> tuple:
    """
    Collect all text content and their locations in the data structure.
    
    Returns:
        Tuple of (texts_list, locations_list) where locations track where each text belongs
    """
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
                                'section': 'by_month',
                                'month': month,
                                'conv_id': conv_id,
                                'group_idx': group_idx,
                                'msg_idx': msg_idx,
                                'content_idx': content_idx
                            })
    
    # Collect from by_hour
    for hour in compressed_data.get('by_hour', {}).keys():
        convs = compressed_data['by_hour'][hour]
        for conv_id in convs.keys():
            msg_groups = convs[conv_id]
            for group_idx, msg_group in enumerate(msg_groups):
                for msg_idx, msg in enumerate(msg_group):
                    cleaned_content = msg.get('cleaned_content', [])
                    for content_idx, content in enumerate(cleaned_content):
                        if content:
                            all_texts.append(content)
                            all_locations.append({
                                'section': 'by_hour',
                                'hour': hour,
                                'conv_id': conv_id,
                                'group_idx': group_idx,
                                'msg_idx': msg_idx,
                                'content_idx': content_idx
                            })
    
    return all_texts, all_locations


def apply_embeddings_to_data(compressed_data: Dict[str, Any], locations: List[Dict], embeddings: List[List[float]]) -> Dict[str, Any]:
    """
    Apply generated embeddings back to the original data structure.
    
    Args:
        compressed_data: Original data structure
        locations: Location information for each embedding
        embeddings: Generated embeddings
    
    Returns:
        Data structure with embeddings added
    """
    # Initialize embeddings field for all messages
    for month in compressed_data.get('by_month', {}).keys():
        convs = compressed_data['by_month'][month]
        for conv_id in convs.keys():
            msg_groups = convs[conv_id]
            for group_idx, msg_group in enumerate(msg_groups):
                for msg_idx, msg in enumerate(msg_group):
                    msg['embeddings'] = [[] for _ in msg.get('cleaned_content', [])]
    
    for hour in compressed_data.get('by_hour', {}).keys():
        convs = compressed_data['by_hour'][hour]
        for conv_id in convs.keys():
            msg_groups = convs[conv_id]
            for group_idx, msg_group in enumerate(msg_groups):
                for msg_idx, msg in enumerate(msg_group):
                    msg['embeddings'] = [[] for _ in msg.get('cleaned_content', [])]
    
    # Apply embeddings using location information
    for loc, embedding in zip(locations, embeddings):
        if loc['section'] == 'by_month':
            msg = compressed_data['by_month'][loc['month']][loc['conv_id']][loc['group_idx']][loc['msg_idx']]
            msg['embeddings'][loc['content_idx']] = embedding
        elif loc['section'] == 'by_hour':
            msg = compressed_data['by_hour'][loc['hour']][loc['conv_id']][loc['group_idx']][loc['msg_idx']]
            msg['embeddings'][loc['content_idx']] = embedding
    
    return compressed_data


def process_compressed_data(compressed_data: Dict[str, Any], embedder: NVEmbedV2Generator, batch_size: int = 32) -> Dict[str, Any]:
    """
    Process all compressed conversation data and add embeddings using batch processing.
    
    Args:
        compressed_data: Loaded compressed conversations data
        embedder: NVEmbedV2Generator instance
        batch_size: Number of texts to process per batch
    
    Returns:
        Data with embeddings added
    """
    print("Collecting all text content...")
    all_texts, all_locations = collect_all_texts_and_locations(compressed_data)
    total_texts = len(all_texts)
    
    print(f"Total text segments to embed: {total_texts}")
    print(f"Batch size: {batch_size}\n")
    
    # Generate embeddings in batches
    print("Generating embeddings in batches...")
    all_embeddings = []
    
    for i in range(0, total_texts, batch_size):
        batch_texts = all_texts[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_texts + batch_size - 1) // batch_size
        
        print(f"  Processing batch {batch_num}/{total_batches} ({len(batch_texts)} texts)...")
        
        # Generate embeddings for batch
        batch_embeddings = embedder.encode(batch_texts, batch_size=len(batch_texts))
        all_embeddings.extend(batch_embeddings)
        
        # Progress indicator
        processed = min(i + batch_size, total_texts)
        progress = (processed / total_texts) * 100
        print(f"    Progress: {processed}/{total_texts} ({progress:.1f}%)")
    
    print(f"\n✓ Generated {len(all_embeddings)} embeddings\n")
    
    # Apply embeddings back to data structure
    print("Applying embeddings to data structure...")
    compressed_data = apply_embeddings_to_data(compressed_data, all_locations, all_embeddings)
    
    print("✓ Embeddings applied successfully\n")
    
    return compressed_data


def main():
    print("=" * 80)
    print("ChatGPT Conversation Embedding Generator (NV-Embed-v2)")
    print("=" * 80)
    print()
    
    # Check for GPU
    if not torch.cuda.is_available():
        print("WARNING: CUDA is not available. This script is designed to use GPU.")
        response = input("Continue with CPU? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(0)
    
    # Load compressed data
    input_file = 'compressed_conversations.json'
    print(f"Loading {input_file}...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            compressed_data = json.load(f)
        print(f"✓ Loaded compressed data\n")
    except FileNotFoundError:
        print(f"Error: {input_file} not found!")
        print("Please run compression.py first to generate the compressed data.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {input_file}: {e}")
        sys.exit(1)
    
    # Initialize embedder
    print("Initializing NV-Embed-v2 model...")
    print("-" * 80)
    
    try:
        embedder = NVEmbedV2Generator()
    except Exception as e:
        print(f"Error initializing model: {e}")
        print("\nNote: Make sure you have the required packages installed:")
        print("  pip install sentence-transformers")
        sys.exit(1)
    
    print("-" * 80)
    print()
    
    # Configure batch size based on GPU availability
    if torch.cuda.is_available():
        # Get GPU memory and set appropriate batch size
        gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
        if gpu_memory_gb >= 24:
            batch_size = 64
        elif gpu_memory_gb >= 16:
            batch_size = 48
        elif gpu_memory_gb >= 12:
            batch_size = 32
        elif gpu_memory_gb >= 8:
            batch_size = 24
        else:
            batch_size = 16
        print(f"GPU Memory: {gpu_memory_gb:.2f} GB")
        print(f"Using batch size: {batch_size}\n")
    else:
        batch_size = 8
        print(f"Using CPU with batch size: {batch_size}\n")
    
    # Process data
    start_time = datetime.now()
    print(f"Starting embedding generation at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    print()
    
    embedded_data = process_compressed_data(compressed_data, embedder, batch_size=batch_size)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("-" * 80)
    print(f"Embedding generation completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total time: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    print()
    
    # Add embedding metadata
    embedded_data['metadata']['embedding_model'] = 'nvidia/NV-Embed-v2'
    embedded_data['metadata']['embedding_generated_at'] = end_time.strftime('%Y-%m-%d %H:%M:%S')
    embedded_data['metadata']['embedding_device'] = embedder.device
    embedded_data['metadata']['embedding_duration_seconds'] = duration
    embedded_data['metadata']['embedding_batch_size'] = batch_size
    
    # Save output
    output_file = 'embedded_conversations.json'
    print(f"Writing embedded data to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(embedded_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Successfully saved to {output_file}")
    print()
    print("=" * 80)
    print("Summary:")
    print(f"  - Model: NV-Embed-v2")
    print(f"  - Device: {embedder.device}")
    print(f"  - Batch size: {batch_size}")
    print(f"  - Processing time: {duration:.2f}s ({duration/60:.2f} min)")
    print(f"  - Output file: {output_file}")
    print("=" * 80)


if __name__ == '__main__':
    main()



def collect_all_texts_and_locations(compressed_data: Dict[str, Any]) -> tuple:
    """
    Collect all text content and their locations in the data structure.
    
    Returns:
        Tuple of (texts_list, locations_list) where locations track where each text belongs
    """
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
                                'section': 'by_month',
                                'month': month,
                                'conv_id': conv_id,
                                'group_idx': group_idx,
                                'msg_idx': msg_idx,
                                'content_idx': content_idx
                            })
    
    # Collect from by_hour
    for hour in compressed_data.get('by_hour', {}).keys():
        convs = compressed_data['by_hour'][hour]
        for conv_id in convs.keys():
            msg_groups = convs[conv_id]
            for group_idx, msg_group in enumerate(msg_groups):
                for msg_idx, msg in enumerate(msg_group):
                    cleaned_content = msg.get('cleaned_content', [])
                    for content_idx, content in enumerate(cleaned_content):
                        if content:
                            all_texts.append(content)
                            all_locations.append({
                                'section': 'by_hour',
                                'hour': hour,
                                'conv_id': conv_id,
                                'group_idx': group_idx,
                                'msg_idx': msg_idx,
                                'content_idx': content_idx
                            })
    
    return all_texts, all_locations


def apply_embeddings_to_data(compressed_data: Dict[str, Any], locations: List[Dict], embeddings: List[List[float]]) -> Dict[str, Any]:
    """
    Apply generated embeddings back to the original data structure.
    
    Args:
        compressed_data: Original data structure
        locations: Location information for each embedding
        embeddings: Generated embeddings
    
    Returns:
        Data structure with embeddings added
    """
    # Initialize embeddings field for all messages
    for month in compressed_data.get('by_month', {}).keys():
        convs = compressed_data['by_month'][month]
        for conv_id in convs.keys():
            msg_groups = convs[conv_id]
            for group_idx, msg_group in enumerate(msg_groups):
                for msg_idx, msg in enumerate(msg_group):
                    msg['embeddings'] = [[] for _ in msg.get('cleaned_content', [])]
    
    for hour in compressed_data.get('by_hour', {}).keys():
        convs = compressed_data['by_hour'][hour]
        for conv_id in convs.keys():
            msg_groups = convs[conv_id]
            for group_idx, msg_group in enumerate(msg_groups):
                for msg_idx, msg in enumerate(msg_group):
                    msg['embeddings'] = [[] for _ in msg.get('cleaned_content', [])]
    
    # Apply embeddings using location information
    for loc, embedding in zip(locations, embeddings):
        if loc['section'] == 'by_month':
            msg = compressed_data['by_month'][loc['month']][loc['conv_id']][loc['group_idx']][loc['msg_idx']]
            msg['embeddings'][loc['content_idx']] = embedding
        elif loc['section'] == 'by_hour':
            msg = compressed_data['by_hour'][loc['hour']][loc['conv_id']][loc['group_idx']][loc['msg_idx']]
            msg['embeddings'][loc['content_idx']] = embedding
    
    return compressed_data


def process_compressed_data(compressed_data: Dict[str, Any], embedder: NVEmbedV2Generator, batch_size: int = 32) -> Dict[str, Any]:
    """
    Process all compressed conversation data and add embeddings using batch processing.
    
    Args:
        compressed_data: Loaded compressed conversations data
        embedder: NVEmbedV2Generator instance
        batch_size: Number of texts to process per batch
    
    Returns:
        Data with embeddings added
    """
    print("Collecting all text content...")
    all_texts, all_locations = collect_all_texts_and_locations(compressed_data)
    total_texts = len(all_texts)
    
    print(f"Total text segments to embed: {total_texts}")
    print(f"Batch size: {batch_size}\n")
    
    # Generate embeddings in batches
    print("Generating embeddings in batches...")
    all_embeddings = []
    
    for i in range(0, total_texts, batch_size):
        batch_texts = all_texts[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_texts + batch_size - 1) // batch_size
        
        print(f"  Processing batch {batch_num}/{total_batches} ({len(batch_texts)} texts)...")
        
        # Generate embeddings for batch
        batch_embeddings = embedder.get_batch_embeddings(batch_texts, batch_size=len(batch_texts))
        all_embeddings.extend(batch_embeddings)
        
        # Progress indicator
        processed = min(i + batch_size, total_texts)
        progress = (processed / total_texts) * 100
        print(f"    Progress: {processed}/{total_texts} ({progress:.1f}%)")
    
    print(f"\n✓ Generated {len(all_embeddings)} embeddings\n")
    
    # Apply embeddings back to data structure
    print("Applying embeddings to data structure...")
    compressed_data = apply_embeddings_to_data(compressed_data, all_locations, all_embeddings)
    
    print("✓ Embeddings applied successfully\n")
    
    return compressed_data


def main():
    print("=" * 80)
    print("ChatGPT Conversation Embedding Generator (NV-Embed-v2)")
    print("=" * 80)
    print()
    
    # Check for GPU
    if not torch.cuda.is_available():
        print("WARNING: CUDA is not available. This script is designed to use GPU.")
        response = input("Continue with CPU? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(0)
    
    # Load compressed data
    input_file = 'compressed_conversations.json'
    print(f"Loading {input_file}...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            compressed_data = json.load(f)
        print(f"✓ Loaded compressed data\n")
    except FileNotFoundError:
        print(f"Error: {input_file} not found!")
        print("Please run compression.py first to generate the compressed data.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {input_file}: {e}")
        sys.exit(1)
    
    # Initialize embedder
    print("Initializing NV-Embed-v2 model...")
    print("-" * 80)
    
    try:
        embedder = NVEmbedV2Generator()
    except Exception as e:
        print(f"Error initializing model: {e}")
        print("\nNote: Make sure you have the required packages installed:")
        print("  pip install torch transformers accelerate")
        sys.exit(1)
    
    print("-" * 80)
    print()
    
    # Configure batch size based on GPU availability
    if embedder.device == 'cuda':
        # Get GPU memory and set appropriate batch size
        gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
        if gpu_memory_gb >= 24:
            batch_size = 64
        elif gpu_memory_gb >= 16:
            batch_size = 48
        elif gpu_memory_gb >= 12:
            batch_size = 32
        elif gpu_memory_gb >= 8:
            batch_size = 24
        else:
            batch_size = 16
        print(f"GPU Memory: {gpu_memory_gb:.2f} GB")
        print(f"Using batch size: {batch_size}\n")
    else:
        batch_size = 8
        print(f"Using CPU with batch size: {batch_size}\n")
    
    # Process data
    start_time = datetime.now()
    print(f"Starting embedding generation at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    print()
    
    embedded_data = process_compressed_data(compressed_data, embedder, batch_size=batch_size)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("-" * 80)
    print(f"Embedding generation completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total time: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    print()
    
    # Add embedding metadata
    embedded_data['metadata']['embedding_model'] = 'nvidia/NV-Embed-v2'
    embedded_data['metadata']['embedding_generated_at'] = end_time.strftime('%Y-%m-%d %H:%M:%S')
    embedded_data['metadata']['embedding_device'] = embedder.device
    embedded_data['metadata']['embedding_duration_seconds'] = duration
    embedded_data['metadata']['embedding_batch_size'] = batch_size
    
    # Save output
    output_file = 'embedded_conversations.json'
    print(f"Writing embedded data to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(embedded_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Successfully saved to {output_file}")
    print()
    print("=" * 80)
    print("Summary:")
    print(f"  - Model: GTE-Large")
    print(f"  - Device: {embedder.device}")
    print(f"  - Batch size: {batch_size}")
    print(f"  - Processing time: {duration:.2f}s ({duration/60:.2f} min)")
    print(f"  - Output file: {output_file}")
    print("=" * 80)


if __name__ == '__main__':
    main()