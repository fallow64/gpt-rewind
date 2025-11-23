#!/usr/bin/env python3
"""
Question Difficulty Analyzer - OPTIMIZED WITH REAL SHARED MEMORY

Critical optimizations to prevent crashes and maximize speed:
1. Shared Memory Persistence: Workers attach to memory ONCE (via initializer), not per message.
2. Global Buffer: Uses global state in workers to avoid passing large objects.
3. Safe Cleanup: Ensures shared memory is unlinked even on errors.
"""

import json
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import re
import os
import gc
from multiprocessing import Pool, cpu_count
from multiprocessing.shared_memory import SharedMemory
from functools import partial
import warnings

# Try to import FAISS for optimized similarity search (optional)
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

# --- GLOBAL WORKER STATE ---
# These variables are only populated inside worker processes
_worker_shm = None
_worker_array = None

def init_worker(shm_name: str, shape: Tuple[int, int], dtype):
    """
    Initialize the worker process.
    Attaches to the shared memory block ONCE when the worker starts.
    """
    global _worker_shm, _worker_array
    try:
        _worker_shm = SharedMemory(name=shm_name)
        _worker_array = np.ndarray(shape, dtype=dtype, buffer=_worker_shm.buf)
    except Exception as e:
        print(f"Worker initialization failed: {e}")

# --- MATH HELPER FUNCTIONS ---

def cosine_similarity_vectorized(emb: np.ndarray, centroid: np.ndarray) -> float:
    """Compute cosine similarity between two normalized embeddings."""
    # Assuming inputs are already normalized
    return float(np.dot(emb, centroid))

def cosine_similarity_batch(embeddings: np.ndarray, centroid: np.ndarray) -> np.ndarray:
    """Compute cosine similarities between multiple embeddings and a centroid."""
    return np.dot(embeddings, centroid)

def compute_centroid(embeddings: np.ndarray) -> np.ndarray:
    """Compute the average (centroid) of multiple embeddings and normalize."""
    if len(embeddings) == 0:
        return np.array([])
    
    centroid = np.mean(embeddings, axis=0)
    norm = np.linalg.norm(centroid)
    if norm > 0:
        centroid = centroid / norm
    return centroid

def normalize_embedding(emb: List[float]) -> np.ndarray:
    """Normalize a single embedding to unit length."""
    arr = np.array(emb, dtype=np.float32)
    norm = np.linalg.norm(arr)
    if norm > 0:
        return arr / norm
    return arr

# --- TEXT ANALYSIS HELPER FUNCTIONS ---

def extract_frustration_signals(text: str) -> bool:
    """Detect frustration indicators in text."""
    if not text:
        return False
    
    text_lower = text.lower()
    frustration_patterns = [
        r"\bdoesn't work\b", r"\bdoesn'?t work\b",
        r"\bstill (confused|stuck|don'?t understand|having trouble)\b",
        r"\bnot working\b", r"\bisn'?t working\b",
        r"\bdidn'?t work\b", r"\bfailed\b",
        r"\berror\b", r"\bwrong\b",
        r"\bstill (not|doesn'?t)\b",
        r"\bhelp[!?]+\b", r"\bwhy (won'?t|doesn'?t|isn'?t)\b",
        r"\bkeep(s)? (getting|failing)\b",
        r"\bcan'?t (figure|get|make)\b"
    ]
    
    return any(re.search(pattern, text_lower) for pattern in frustration_patterns)

def extract_resolution_signals(text: str) -> bool:
    """Detect resolution/satisfaction indicators in text."""
    if not text:
        return False
    
    text_lower = text.lower()
    resolution_patterns = [
        r"\bthank(s| you)\b", r"\bthanks\b",
        r"\bgot it\b", r"\bperfect\b",
        r"\bworks?\b", r"\bworked\b",
        r"\bsolve?d\b", r"\bfixed\b",
        r"\bthat('s| is) (great|perfect|helpful|exactly|right)\b",
        r"\bmakes sense\b", r"\bunderstood?\b",
        r"\bamazing\b", r"\bawesome\b",
        r"\bappreciate\b"
    ]
    
    return any(re.search(pattern, text_lower) for pattern in resolution_patterns)

def parse_timestamp(ts_str: str) -> datetime:
    """Parse timestamp string to datetime object."""
    try:
        return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
    except:
        try:
            return datetime.fromtimestamp(float(ts_str))
        except:
            return datetime.now()

# --- SHARED MEMORY MANAGEMENT ---

def create_shared_embeddings(embedded_data: Dict[str, Any]) -> Tuple[Dict[str, int], SharedMemory, int, Tuple[int, int]]:
    """
    Create REAL shared memory for all normalized embeddings.
    
    Returns:
        - embeddings_index: Dict mapping message_id -> row_index in shared array
        - shared_mem: SharedMemory object
        - embedding_dim: Dimension of embeddings
        - shape: Tuple (num_embeddings, embedding_dim)
    """
    print("Creating shared memory for embeddings...")
    
    # First pass: collect all embeddings and determine size
    all_embeddings = []
    message_ids = []
    embedding_dim = None
    
    for month, convs in embedded_data.get('by_month', {}).items():
        for conv_id, msg_groups in convs.items():
            for group in msg_groups:
                for msg in group:
                    msg_id = msg.get('id', '')
                    if not msg_id:
                        continue
                    
                    # Extract and normalize first valid embedding
                    if msg.get('embeddings'):
                        for emb in msg['embeddings']:
                            if emb and len(emb) > 0:
                                normalized = normalize_embedding(emb)
                                if embedding_dim is None:
                                    embedding_dim = len(normalized)
                                all_embeddings.append(normalized)
                                message_ids.append(msg_id)
                                break
    
    if not all_embeddings:
        print("  No embeddings found!")
        return {}, None, 0, (0, 0)
    
    # Create shared memory
    num_embeddings = len(all_embeddings)
    shape = (num_embeddings, embedding_dim)
    # Calculate bytes: rows * cols * 4 bytes (float32)
    total_size = num_embeddings * embedding_dim * 4
    
    print(f"  Allocating shared memory: {num_embeddings:,} embeddings x {embedding_dim} dims = {total_size / 1024 / 1024:.2f} MB")
    
    try:
        shm = SharedMemory(create=True, size=total_size)
    except Exception as e:
        print(f"Failed to allocate shared memory. Ensure you have enough RAM. Error: {e}")
        return {}, None, 0, (0, 0)

    # Create numpy array backed by shared memory
    shared_array = np.ndarray(shape, dtype=np.float32, buffer=shm.buf)
    
    # Copy embeddings to shared memory
    print("  Populating shared memory...")
    for i, emb in enumerate(all_embeddings):
        shared_array[i] = emb
    
    # Create index mapping message_id -> row_index
    # We don't need to store size/dim per message since it's uniform
    embeddings_index = {msg_id: i for i, msg_id in enumerate(message_ids)}
    
    print(f"  ✓ Shared memory created: {len(embeddings_index):,} embeddings indexed")
    
    return embeddings_index, shm, embedding_dim, shape

def get_embedding_fast(msg_id: str, embeddings_index: Dict[str, int]) -> Optional[np.ndarray]:
    """
    Retrieve embedding from the GLOBAL worker array.
    This replaces the slow open/close method.
    """
    if _worker_array is None:
        # Fallback if not running in worker pool or initialization failed
        return None
        
    idx = embeddings_index.get(msg_id)
    if idx is None:
        return None
        
    # Return a copy to ensure thread safety if modified later (though we treat them as immutable here)
    # Accessing _worker_array is nearly as fast as accessing local memory
    return _worker_array[idx].copy()

# --- CORE LOGIC CLASSES ---

class Topic:
    """
    Topic representation - stores FULL message objects (including embeddings).
    """
    
    def __init__(self, first_message: Dict[str, Any]):
        self.messages: List[Dict[str, Any]] = [first_message]
        self.centroid_embeddings: List[np.ndarray] = []
        self.centroid = None 
    
    def _compute_centroid(self) -> Optional[np.ndarray]:
        """Compute centroid from stored embeddings."""
        if len(self.centroid_embeddings) == 0:
            return None
        
        stacked = np.stack(self.centroid_embeddings, axis=0)
        return compute_centroid(stacked)
    
    def add_message(self, message: Dict[str, Any]):
        """Add a message to this topic."""
        self.messages.append(message)
    
    def add_embedding(self, embedding: np.ndarray):
        """Add an embedding and update centroid."""
        if embedding is not None:
            self.centroid_embeddings.append(embedding)
            self.centroid = self._compute_centroid()
    
    def get_centroid_message_pair(self) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Get the question/response pair closest to the topic centroid.
        """
        if self.centroid is None:
            return None, None
        
        # Find user message closest to centroid
        user_messages = [(i, msg) for i, msg in enumerate(self.messages) if msg.get('role') == 'user']
        
        if not user_messages:
            return None, None
        
        user_embeddings = []
        valid_user_messages = []
        
        for msg_idx, msg in user_messages:
            # Check if we have embedding for this message index
            if msg_idx < len(self.centroid_embeddings):
                user_embeddings.append(self.centroid_embeddings[msg_idx])
                valid_user_messages.append((msg_idx, msg))
        
        if not user_embeddings:
            return None, None
        
        # Vectorized similarity computation
        stacked = np.stack(user_embeddings, axis=0)
        similarities = cosine_similarity_batch(stacked, self.centroid)
        best_idx = np.argmax(similarities)
        best_user_idx, best_user_msg = valid_user_messages[best_idx]
        
        # Find corresponding assistant response
        best_assistant_msg = None
        for i in range(best_user_idx + 1, len(self.messages)):
            if self.messages[i].get('role') == 'assistant':
                best_assistant_msg = self.messages[i]
                break
        
        return best_user_msg, best_assistant_msg
    
    def compute_metrics(self) -> Dict[str, Any]:
        """Compute all metrics for this topic."""
        user_messages = [m for m in self.messages if m.get('role') == 'user']
        assistant_messages = [m for m in self.messages if m.get('role') == 'assistant']
        
        repeat_count = len(user_messages)
        followup_count = len(assistant_messages)
        
        # Compute mean lengths
        user_lengths = []
        assistant_lengths = []
        
        for msg in user_messages:
            content = msg.get('cleaned_content', []) or msg.get('content', '')
            if isinstance(content, list):
                total_len = sum(len(str(c)) for c in content if c)
            else:
                total_len = len(str(content))
            user_lengths.append(total_len)
        
        for msg in assistant_messages:
            content = msg.get('cleaned_content', []) or msg.get('content', '')
            if isinstance(content, list):
                total_len = sum(len(str(c)) for c in content if c)
            else:
                total_len = len(str(content))
            assistant_lengths.append(total_len)
        
        mean_question_len = np.mean(user_lengths) if user_lengths else 0
        mean_answer_len = np.mean(assistant_lengths) if assistant_lengths else 0
        
        # Compute duration
        timestamps = []
        for msg in self.messages:
            if msg.get('timestamp'):
                timestamps.append(parse_timestamp(msg['timestamp']))
        
        duration_seconds = 0
        if len(timestamps) >= 2:
            duration_seconds = (max(timestamps) - min(timestamps)).total_seconds()
        
        # Check for frustration and resolution
        frustration_flag = False
        resolution_flag = False
        
        for msg in user_messages:
            content = msg.get('cleaned_content', []) or msg.get('content', '')
            if isinstance(content, list):
                text = ' '.join(str(c) for c in content)
            else:
                text = str(content)
            if extract_frustration_signals(text):
                frustration_flag = True
            if extract_resolution_signals(text):
                resolution_flag = True
        
        return {
            'repeat_count': repeat_count,
            'followup_count': followup_count,
            'mean_question_len': mean_question_len,
            'mean_answer_len': mean_answer_len,
            'duration_seconds': duration_seconds,
            'frustration_flag': frustration_flag,
            'resolution_flag': resolution_flag
        }
    
    def compute_difficulty_score(self) -> float:
        """Compute difficulty score based on multiple factors."""
        metrics = self.compute_metrics()
        
        score = 0.0
        score += metrics['repeat_count'] * 15
        score += metrics['followup_count'] * 10
        score += metrics['duration_seconds'] * 0.01
        score += metrics['mean_answer_len'] * 0.05
        if metrics['frustration_flag']:
            score += 50
        if metrics['resolution_flag']:
            score -= 30
        score += metrics['mean_question_len'] * 0.03
        
        return score

# --- PROCESSING FUNCTIONS ---

def segment_conversation_by_topic(messages: List[Dict[str, Any]], 
                                   embeddings_index: Dict[str, int],
                                   similarity_threshold: float = 0.65) -> List[Topic]:
    """
    Segment a conversation into topics using fast shared memory lookups.
    """
    topics = []
    current_topic = None
    
    for message in messages:
        msg_id = message.get('id', '')
        role = message.get('role', '')
        
        # Get embedding from GLOBAL shared memory (Instant access)
        message_emb = get_embedding_fast(msg_id, embeddings_index)
        
        # Only segment on user messages
        if role != 'user':
            if current_topic:
                current_topic.add_message(message)
                if message_emb is not None:
                    current_topic.add_embedding(message_emb)
            continue
        
        should_create_new_topic = False
        
        if current_topic is None:
            should_create_new_topic = True
        elif current_topic.centroid is None or message_emb is None:
            # Cannot compare without embeddings, assume same topic
            current_topic.add_message(message)
            if message_emb is not None:
                current_topic.add_embedding(message_emb)
            continue
        else:
            similarity = cosine_similarity_vectorized(message_emb, current_topic.centroid)
            if similarity < similarity_threshold:
                should_create_new_topic = True
        
        if should_create_new_topic:
            current_topic = Topic(message)
            if message_emb is not None:
                current_topic.add_embedding(message_emb)
            topics.append(current_topic)
        else:
            current_topic.add_message(message)
            if message_emb is not None:
                current_topic.add_embedding(message_emb)
    
    return topics

def process_month_conversations(month_data: Tuple[str, Dict[str, Any]], 
                                embeddings_index: Dict[str, int],
                                similarity_threshold: float = 0.65) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Worker function. Processes a specific month.
    """
    month, convs = month_data
    segmented_convs = {} 
    month_topics = []
    
    for conv_id, msg_groups in convs.items():
        # Flatten message groups
        messages = []
        for group in msg_groups:
            messages.extend(group)
        
        # Sort by timestamp
        messages.sort(key=lambda m: parse_timestamp(m.get('timestamp', '0')))
        
        # Segment this conversation
        topics = segment_conversation_by_topic(messages, embeddings_index, similarity_threshold)
        
        segmented_convs[conv_id] = {
            'num_topics': len(topics),
            'topics': []
        }
        
        for i, topic in enumerate(topics):
            metrics = topic.compute_metrics()
            difficulty = topic.compute_difficulty_score()
            question_msg, response_msg = topic.get_centroid_message_pair()
            
            question_id = question_msg.get('id', '') if question_msg else ''
            response_id = response_msg.get('id', '') if response_msg else ''
            
            topic_data = {
                'topic_id': i,
                'num_messages': len(topic.messages),
                'metrics': metrics,
                'difficulty_score': difficulty,
                'representative_question_id': question_id,
                'representative_response_id': response_id,
                'timestamp': topic.messages[0].get('timestamp', '') if topic.messages else '',
                'messages': topic.messages
            }
            
            segmented_convs[conv_id]['topics'].append(topic_data)
            
            month_topics.append({
                'month': month,
                'conv_id': conv_id,
                'topic_id': i,
                'difficulty_score': difficulty,
                'question_id': question_id,
                'response_id': response_id,
                'timestamp': topic.messages[0].get('timestamp', '') if topic.messages else '',
                'metrics': metrics
            })
    
    return month, segmented_convs, month_topics

def process_all_conversations(embedded_data: Dict[str, Any], 
                               embeddings_index: Dict[str, int],
                               shm_name: str,
                               shape: Tuple[int, int],
                               similarity_threshold: float = 0.65,
                               num_workers: Optional[int] = None) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Process all conversations using Pool with Initializer.
    """
    if num_workers is None:
        num_workers = min(12, max(1, cpu_count() // 2))
    else:
        num_workers = min(num_workers, 12)
    
    month_data_list = [(month, convs) for month, convs in embedded_data.get('by_month', {}).items()]
    
    if not month_data_list:
        return {'metadata': embedded_data.get('metadata', {}), 'segmented_conversations': {}}, []
    
    num_workers = min(num_workers, len(month_data_list))
    
    print(f"Processing {len(month_data_list)} months with {num_workers} workers...")
    
    if num_workers > 1:
        # Pass shm_name and shape to initializer so workers attach once
        with Pool(processes=num_workers, 
                  initializer=init_worker, 
                  initargs=(shm_name, shape, np.float32)) as pool:
            
            worker_func = partial(process_month_conversations, 
                                  embeddings_index=embeddings_index,
                                  similarity_threshold=similarity_threshold)
            
            results = pool.map(worker_func, month_data_list)
    else:
        # Fallback for single thread (mostly for debugging)
        print("(Using single-threaded processing)")
        # Manually init globals for single thread
        init_worker(shm_name, shape, np.float32)
        results = [process_month_conversations(md, embeddings_index, similarity_threshold) 
                   for md in month_data_list]
    
    segmented_conversations = {}
    all_topics = []
    
    for month, month_segmented_convs, month_topics in results:
        segmented_conversations[month] = month_segmented_convs
        all_topics.extend(month_topics)
    
    segmented_data = {
        'metadata': embedded_data.get('metadata', {}),
        'segmented_conversations': segmented_conversations
    }
    
    return segmented_data, all_topics

def find_hardest_and_easiest(all_topics: List[Dict[str, Any]]) -> Tuple[Optional[Dict], Optional[Dict]]:
    if not all_topics:
        return None, None
    
    scores = np.array([t['difficulty_score'] for t in all_topics])
    easiest_idx = np.argmin(scores)
    hardest_idx = np.argmax(scores)
    
    return all_topics[hardest_idx], all_topics[easiest_idx]

def search_message_by_id(embedded_data: Dict[str, Any], message_id: str) -> Optional[Dict[str, Any]]:
    if not message_id:
        return None
    
    for month, convs in embedded_data.get('by_month', {}).items():
        for conv_id, msg_groups in convs.items():
            for group in msg_groups:
                for msg in group:
                    if msg.get('id') == message_id:
                        return msg
    return None

def extract_raw_content(message: Dict[str, Any]) -> str:
    if not message:
        return ""
    
    if 'content' in message:
        content = message['content']
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            return ' '.join(str(c) for c in content if c)
            
    if 'cleaned_content' in message:
        content = message['cleaned_content']
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            return ' '.join(str(c) for c in content if c)
            
    return ""

def analyze_questions(embedded_file: str, output_dir: str = '.', similarity_threshold: float = 0.65, num_workers: int = None):
    """
    Analyze question difficulty from embedded conversations.
    
    Args:
        embedded_file: Path to embedded_conversations.json
        output_dir: Directory to write output files to
        similarity_threshold: Threshold for topic segmentation
        num_workers: Number of worker processes (None for auto)
    
    Returns:
        dict with output files and analysis results
    """
    print("=" * 70)
    print("Question Difficulty Analyzer - WITH REAL SHARED MEMORY")
    print("=" * 70)
    print(f"CPUs available: {cpu_count()}")
    
    if not os.path.exists(embedded_file):
        print(f"Error: {embedded_file} not found!")
        raise FileNotFoundError(embedded_file)
        
    try:
        with open(embedded_file, 'r', encoding='utf-8') as f:
            embedded_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}")
        raise

    # PHASE 1: Create Shared Memory
    embeddings_index, shm, embedding_dim, shape = create_shared_embeddings(embedded_data)
    
    if shm is None:
        raise RuntimeError("Failed to create shared memory for embeddings")

    try:
        # PHASE 2: Segment Conversations
        start_time = datetime.now()
        segmented_data, all_topics = process_all_conversations(
            embedded_data,
            embeddings_index,
            shm.name,
            shape,
            similarity_threshold=similarity_threshold,
            num_workers=num_workers if num_workers else 12
        )
        processing_time = (datetime.now() - start_time).total_seconds()
        
        print(f"✓ Processing completed in {processing_time:.2f}s")
        print(f"✓ Total topics identified: {len(all_topics):,}")

        # PHASE 3: Rank
        hardest, easiest = find_hardest_and_easiest(all_topics)
        print(f"✓ Hardest score: {hardest['difficulty_score']:.2f}" if hardest else "✗ No hardest found")
        print(f"✓ Easiest score: {easiest['difficulty_score']:.2f}" if easiest else "✗ No easiest found")

        # Save results
        segmented_file = os.path.join(output_dir, 'segmented_conversations.json')
        with open(segmented_file, 'w', encoding='utf-8') as f:
            json.dump(segmented_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved {segmented_file}")

    finally:
        # PHASE 4: Cleanup (Guaranteed execution)
        print("\nCleaning up shared memory...")
        shm.close()
        shm.unlink()
        print("✓ Shared memory released.")
        gc.collect()

    # PHASE 5: Retrieve Raw Messages (Post-cleanup)
    print("\n" + "=" * 70)
    print("PHASE 5: Sample Results & Export")
    print("=" * 70)
    
    extremes_data = {}

    if hardest:
        raw_msg = search_message_by_id(embedded_data, hardest['question_id'])
        q_text = extract_raw_content(raw_msg)
        print(f"\n[HARDEST QUESTION]\n{q_text[:200]}...")
        
        extremes_data['hardest'] = {
            'score': hardest['difficulty_score'],
            'metrics': hardest['metrics'],
            'question_id': hardest['question_id'],
            'text': q_text,
            'full_message': raw_msg
        }
        
    if easiest:
        raw_msg = search_message_by_id(embedded_data, easiest['question_id'])
        q_text = extract_raw_content(raw_msg)
        print(f"\n[EASIEST QUESTION]\n{q_text[:200]}...")

        extremes_data['easiest'] = {
            'score': easiest['difficulty_score'],
            'metrics': easiest['metrics'],
            'question_id': easiest['question_id'],
            'text': q_text,
            'full_message': raw_msg
        }

    # Save to new JSON file
    if extremes_data:
        output_file = os.path.join(output_dir, 'questions_analytics.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extremes_data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved hardest and easiest questions to {output_file}")
    
    return {
        'segmented_file': segmented_file,
        'questions_file': output_file if extremes_data else None,
        'hardest': hardest,
        'easiest': easiest,
        'all_topics': all_topics
    }


def main():
    """Main entry point for command-line usage."""
    import sys
    
    if len(sys.argv) > 1:
        embedded_file = sys.argv[1]
    else:
        embedded_file = 'embedded_conversations.json'
    
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
    
    result = analyze_questions(embedded_file, output_dir)
    print(f"✓ Analysis complete")
    if result['questions_file']:
        print(f"✓ Questions file: {result['questions_file']}")

if __name__ == "__main__":
    main()