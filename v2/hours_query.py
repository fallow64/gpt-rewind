#!/usr/bin/env python3
"""
Hourly Topic Discovery (Hour of Day Analysis)
Phase 1 (Parallel CPU): HDBSCAN Clustering + YAKE Candidate Generation
Phase 2 (Sequential GPU): GTE-Large Candidate Embedding + Label Selection

Analyzes top topics for each hour of the day (0-23) across the entire year.

Author: Topic Discovery Pipeline
Date: 2025-11-23
"""

import json
import numpy as np
from typing import Dict, List, Tuple, Any
from collections import Counter, defaultdict
from datetime import datetime

# Core libraries
from scipy.spatial.distance import cosine
import hdbscan
import yake
from joblib import Parallel, delayed

# For GTE-Large encoding
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel

# ============================================================================
# Configuration
# ============================================================================
MAX_TEXT_INPUT = 500_000  # Truncate text passed to YAKE to 50k chars
MIN_CLUSTER_SIZE = 5
TOP_K_CLUSTERS = 3
N_JOBS = 12  # Safe to use >1 now, as we only do CPU work in parallel

# ============================================================================
# GTE-Large Encoder (GPU Safe)
# ============================================================================

def average_pool(last_hidden_states: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

class GTELargeEncoder:
    def __init__(self, model_name: str = "thenlper/gte-large", max_length: int = 512):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"  > Initializing Encoder on {self.device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        
        if self.device == 'cuda':
            self.model = self.model.cuda()
            self.model = self.model.half() # FP16
        
        self.model.eval()
        self.max_length = max_length
    
    def encode(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.array([])
        
        # Batch processing to avoid OOM on large candidate lists
        batch_size = 16
        all_embeddings = []
        
        with torch.inference_mode():
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                encoded_input = self.tokenizer(
                    batch_texts,
                    max_length=self.max_length,
                    padding=True,
                    truncation=True,
                    return_tensors='pt'
                )
                
                if self.device == 'cuda':
                    encoded_input = {k: v.cuda() for k, v in encoded_input.items()}
                
                if self.device == 'cuda':
                    with torch.autocast(device_type='cuda', dtype=torch.float16):
                        outputs = self.model(**encoded_input)
                        embeddings = average_pool(outputs.last_hidden_state, encoded_input['attention_mask'])
                else:
                    outputs = self.model(**encoded_input)
                    embeddings = average_pool(outputs.last_hidden_state, encoded_input['attention_mask'])
                
                embeddings = F.normalize(embeddings.float(), p=2, dim=1)
                all_embeddings.append(embeddings.cpu().numpy())
                
        return np.concatenate(all_embeddings, axis=0) if all_embeddings else np.array([])

# ============================================================================
# Math Helpers
# ============================================================================

def normalize_vectors(vectors: np.ndarray) -> np.ndarray:
    """L2 Normalize numpy array (N, D)."""
    norm = np.linalg.norm(vectors, axis=1, keepdims=True)
    # Avoid division by zero
    return vectors / (norm + 1e-10)

def compute_centroid(embeddings: np.ndarray) -> np.ndarray:
    """Compute normalized centroid."""
    centroid = np.mean(embeddings, axis=0)
    return centroid / (np.linalg.norm(centroid) + 1e-10)

# ============================================================================
# Phase 1: CPU Parallel Processing (Clustering + Candidate Generation)
# ============================================================================

def extract_phrases_yake(text: str) -> List[str]:
    """Extract phrases from text using YAKE (CPU intensive)."""
    if not text.strip():
        return []
        
    kw_extractor = yake.KeywordExtractor(
        lan="en",
        n=3,              # Max ngram
        dedupLim=0.7,
        top=20,           # Number of candidates
        features=None
    )
    
    try:
        keywords = kw_extractor.extract_keywords(text)
        return [kw[0] for kw in keywords]
    except Exception as e:
        return []

def extract_candidates_cpu(
    hour: int,
    raw_embeddings: np.ndarray,
    msg_ids: List[str],
    msg_map: Dict[str, str],
    top_k: int
) -> Dict[str, Any]:
    """
    Run HDBSCAN and YAKE. Returns cluster data with string candidates (no GPU usage).
    """
    # 1. Normalize Embeddings
    norm_embeddings = normalize_vectors(raw_embeddings)
    
    # 2. Cluster
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=MIN_CLUSTER_SIZE,
        metric='euclidean', 
        cluster_selection_method='eom'
    )
    labels = clusterer.fit_predict(norm_embeddings)
    
    # 3. Filter Top Clusters
    counts = Counter(labels[labels >= 0])
    top_cluster_ids = [cid for cid, _ in counts.most_common(top_k)]
    
    clusters_data = []
    
    for cluster_id in top_cluster_ids:
        mask = labels == cluster_id
        indices = np.where(mask)[0]
        
        # Extract data for this cluster
        c_msg_ids = [msg_ids[i] for i in indices]
        c_embeds = norm_embeddings[indices]
        
        # Calculate Centroid
        centroid = compute_centroid(c_embeds)
        
        # Aggregate Text for YAKE
        # Optimization: Take text from top 50 messages closest to centroid
        dists = [cosine(emb, centroid) for emb in c_embeds]
        sorted_indices = np.argsort(dists)[:50]
        selected_ids = [c_msg_ids[i] for i in sorted_indices]
        
        raw_texts = [msg_map.get(mid, '') for mid in selected_ids]
        combined_text = ' '.join(raw_texts)
        
        # Truncate to protect YAKE
        if len(combined_text) > MAX_TEXT_INPUT:
            combined_text = combined_text[:MAX_TEXT_INPUT]
            
        candidates = extract_phrases_yake(combined_text)
        
        clusters_data.append({
            'cluster_id': int(cluster_id),
            'size': int(len(c_msg_ids)),
            'centroid': centroid,
            'candidates': candidates,
            'sample_msg_ids': c_msg_ids[:5]
        })
        
    return {
        'hour': hour,
        'clusters': clusters_data,
        'stats': {
            'total': len(msg_ids),
            'noise': int(np.sum(labels == -1))
        }
    }

# ============================================================================
# Phase 2: GPU Sequential Processing (Label Selection)
# ============================================================================

def resolve_labels_gpu(
    hourly_results: List[Dict[str, Any]], 
    encoder: GTELargeEncoder
) -> List[Dict[str, Any]]:
    """
    Iterate through pre-computed clusters, embed candidates, and find best label.
    """
    print(f"\nResolving labels for {len(hourly_results)} hours using GPU...")
    
    final_output = []
    
    for h_data in hourly_results:
        hour = h_data['hour']
        clusters = h_data['clusters']
        
        print(f"  Processing hour {hour:02d}:00 ({len(clusters)} clusters)...")
        
        for cluster in clusters:
            candidates = cluster['candidates']
            centroid = cluster['centroid']
            
            if not candidates:
                cluster['label'] = "unknown topic"
                continue
                
            cand_embeds = encoder.encode(candidates)
            
            dists = [cosine(emb, centroid) for emb in cand_embeds]
            best_idx = np.argmin(dists)
            cluster['label'] = candidates[best_idx]
            
            del cluster['centroid']
            
        final_output.append(h_data)
        
    return final_output

# ============================================================================
# Data Loading and Transformation
# ============================================================================

def extract_hour_from_timestamp(timestamp_str: str) -> int:
    """
    Extract hour of day from ISO timestamp.
    Returns: 0-23 representing hour of day
    """
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.hour
    except:
        return -1  # Invalid timestamp

def load_and_transform_to_hourly(embed_file: str, raw_file: str):
    """
    Loads monthly embeddings and transforms them to hourly grouping.
    Deletes monthly data from memory after transformation.
    """
    print("Loading data...")
    with open(embed_file, 'r', encoding='utf-8') as f:
        embed_data = json.load(f)
    with open(raw_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
        
    # 1. Build message map and timestamp map
    print("  Mapping raw content and timestamps...")
    msg_map = {}
    msg_timestamps = {}
    
    for m_list in raw_data.get('by_month', {}).values():
        for msg in m_list:
            msg_id = msg.get('id')
            if msg_id and msg.get('content'):
                msg_map[msg_id] = msg['content']
                if msg.get('timestamp'):
                    msg_timestamps[msg_id] = msg['timestamp']
    
    # Delete raw_data to free memory
    del raw_data
    print(f"  Mapped {len(msg_map)} messages with content")
                
    # 2. Transform embeddings from monthly to hourly grouping
    print("  Transforming monthly to hourly grouping...")
    hourly_data = defaultdict(lambda: {'embeddings': [], 'msg_ids': []})
    total_processed = 0
    skipped_no_timestamp = 0
    
    for month, convs in embed_data.get('by_month', {}).items():
        for _, msg_groups in convs.items():
            for group in msg_groups:
                for msg in group:
                    msg_id = msg.get('id')
                    embeds = msg.get('embeddings')
                    
                    # Check if we have all required data
                    if msg_id and embeds and (msg_id in msg_map) and (msg_id in msg_timestamps):
                        hour = extract_hour_from_timestamp(msg_timestamps[msg_id])
                        
                        if hour >= 0:  # Valid hour
                            hourly_data[hour]['embeddings'].append(embeds[0])
                            hourly_data[hour]['msg_ids'].append(msg_id)
                            total_processed += 1
                        else:
                            skipped_no_timestamp += 1
                    elif msg_id and embeds and (msg_id in msg_map):
                        skipped_no_timestamp += 1
    
    # Delete embed_data to free memory
    del embed_data
    print(f"  Transformed {total_processed} messages into {len(hourly_data)} hours")
    print(f"  Skipped {skipped_no_timestamp} messages without valid timestamps")
    
    # 3. Convert to final format
    hourly_inputs = {}
    for hour in range(24):  # Ensure all 24 hours are represented
        if hour in hourly_data and hourly_data[hour]['embeddings']:
            embeddings = np.array(hourly_data[hour]['embeddings'], dtype=np.float32)
            msg_ids = hourly_data[hour]['msg_ids']
            hourly_inputs[hour] = (embeddings, msg_ids)
            print(f"    Hour {hour:02d}:00 - {len(msg_ids)} messages")
        else:
            print(f"    Hour {hour:02d}:00 - 0 messages (skipped)")
    
    # Delete hourly_data to free memory
    del hourly_data
    
    return hourly_inputs, msg_map

def aggregate_hourly_topics(hourly_results: List[Dict[str, Any]], top_k: int = 3) -> Dict[str, Any]:
    """
    Aggregate cluster labels by hour to identify top topics for each hour of day.
    Weighted by cluster size.
    """
    hourly_labels = defaultdict(list)
    
    # Collect all cluster labels by hour
    for hour_result in hourly_results:
        hour = hour_result['hour']
        
        for cluster in hour_result.get('clusters', []):
            label = cluster.get('label', 'unknown')
            size = cluster.get('size', 0)
            hourly_labels[hour].append((label, size))
    
    # Aggregate and rank topics by hour
    hourly_topics = {}
    for hour in range(24):
        if hour in hourly_labels:
            labels = hourly_labels[hour]
            
            # Count label frequencies weighted by cluster size
            label_weights = defaultdict(int)
            for label, size in labels:
                label_weights[label] += size
            
            # Get top K topics
            top_topics = sorted(label_weights.items(), key=lambda x: x[1], reverse=True)[:top_k]
            
            hourly_topics[f"{hour:02d}:00"] = [
                {'topic': label, 'total_messages': weight}
                for label, weight in top_topics
            ]
        else:
            hourly_topics[f"{hour:02d}:00"] = []
        
    return hourly_topics

# ============================================================================
# Main
# ============================================================================

def main():
    EMBED_FILE = 'embedded_conversations.json'
    RAW_FILE = 'conversations_with_msg_id.json'
    OUT_FILE = 'hourly_topics.json'
    
    # 1. Load and Transform Data (monthly -> hourly)
    hourly_inputs, msg_map = load_and_transform_to_hourly(EMBED_FILE, RAW_FILE)
    
    if not hourly_inputs:
        print("\nERROR: No hourly data to process. Check if timestamps exist in your data.")
        return
    
    # 2. Phase 1: CPU Parallel
    print(f"\nPhase 1: Generating candidates (Parallel CPU, n_jobs={N_JOBS})...")
    start_cpu = datetime.now()
    
    cpu_results = Parallel(n_jobs=N_JOBS)(
        delayed(extract_candidates_cpu)(hour, embs, ids, msg_map, TOP_K_CLUSTERS)
        for hour, (embs, ids) in sorted(hourly_inputs.items())
    )
    
    print(f"Phase 1 complete in {(datetime.now() - start_cpu).total_seconds():.1f}s")
    
    # Delete msg_map to free memory
    del msg_map
    
    # 3. Phase 2: GPU Sequential
    print("\nPhase 2: Initializing GTE-Large...")
    encoder = GTELargeEncoder()
    
    hourly_results = resolve_labels_gpu(cpu_results, encoder)

    # 4. Aggregation: Hourly Top Topics
    print("\nAggregating Hourly Topics...")
    hourly_topics = aggregate_hourly_topics(hourly_results, top_k=3)
    
    # Print summary to console
    print("\n" + "="*60)
    print("TOP TOPICS BY HOUR OF DAY")
    print("="*60)
    for hour_str, topics in sorted(hourly_topics.items()):
        print(f"\n⏰ {hour_str}")
        if topics:
            for i, t in enumerate(topics, 1):
                print(f"   {i}. {t['topic']} ({t['total_messages']} msgs)")
        else:
            print("   (No data)")
    
    # 5. Save
    print(f"\nSaving to {OUT_FILE}...")
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'generated_at': str(datetime.now()),
                'description': 'Top topics for each hour of the day (0-23) across entire year'
            },
            'hourly_summary': hourly_topics,
            'hourly_details': hourly_results
        }, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Hourly topic discovery complete!")

if __name__ == '__main__':
    main()