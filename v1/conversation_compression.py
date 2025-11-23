#!/usr/bin/env python3
"""
ChatGPT Conversation History Compression and Analysis Tool

This script processes ChatGPT conversation exports and:
- Filters conversations from the last 12 months
- Groups messages by month and hour of day
- Removes stopwords and cleans content
- Uses multiprocessing for parallel processing
- Outputs compressed JSON structure
"""

import json
import re
from datetime import datetime, timedelta
from collections import defaultdict
from multiprocessing import Pool, cpu_count
from typing import Dict, List, Tuple, Any
import sys

# Common English stopwords
STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
    "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he',
    'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's",
    'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are',
    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do',
    'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because',
    'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
    'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
    'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
    'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
    'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
    'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can',
    'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm',
    'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn',
    "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven',
    "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't",
    'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't",
    'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
}


def clean_content(text: str) -> List[str]:
    """
    Clean message content by:
    1. Splitting by paragraphs
    2. Removing first paragraph
    3. Removing stopwords
    4. Returning cleaned content entries
    """
    if not text or not isinstance(text, str):
        return []
    
    # Split by paragraphs (one or more newlines)
    paragraphs = [p.strip() for p in re.split(r'\n+', text) if p.strip()]
    
    # Remove first paragraph
    if len(paragraphs) > 1:
        paragraphs = paragraphs[1:]
    elif len(paragraphs) == 1:
        # If only one paragraph, keep it but process it
        pass
    else:
        return []
    
    cleaned_entries = []
    for paragraph in paragraphs:
        # Tokenize and remove stopwords
        words = re.findall(r'\b[a-z]+\b', paragraph.lower())
        filtered_words = [w for w in words if w not in STOPWORDS and len(w) > 2]
        
        if filtered_words:
            cleaned_entries.append(' '.join(filtered_words))
    
    return cleaned_entries


def extract_messages_from_conversation(conv: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract all messages from a conversation mapping structure.
    """
    messages = []
    mapping = conv.get('mapping', {})
    
    for node_id, node_data in mapping.items():
        message = node_data.get('message')
        if not message:
            continue
        
        # Get timestamp
        create_time = message.get('create_time')
        if not create_time:
            continue
        
        # Get content
        content = message.get('content', {})
        if isinstance(content, dict):
            parts = content.get('parts', [])
            if parts and isinstance(parts, list):
                text = ' '.join(str(p) for p in parts if p)
            else:
                text = ''
        else:
            text = str(content) if content else ''
        
        # Get role
        author = message.get('author', {})
        role = author.get('role', 'unknown')
        
        messages.append({
            'timestamp': create_time,
            'role': role,
            'content': text,
            'conversation_id': conv.get('id', 'unknown')
        })
    
    return messages


def format_timestamp(ts: float) -> str:
    """Convert Unix timestamp to YYYY-MM-DD HH:MM:SS format."""
    try:
        dt = datetime.fromtimestamp(ts)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, OSError):
        return '1970-01-01 00:00:00'


def get_month_bucket(ts: float) -> str:
    """Get month bucket in YYYY-MM format."""
    try:
        dt = datetime.fromtimestamp(ts)
        return dt.strftime('%Y-%m')
    except (ValueError, OSError):
        return '1970-01'


def get_hour_bucket(ts: float) -> str:
    """Get hour bucket in HH format (00-23)."""
    try:
        dt = datetime.fromtimestamp(ts)
        return dt.strftime('%H')
    except (ValueError, OSError):
        return '00'


def process_conversation(conv: Dict[str, Any], cutoff_date: datetime) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Process a single conversation and return its ID and filtered messages.
    Returns (conv_id, messages_list)
    """
    conv_id = conv.get('id', 'unknown')
    messages = extract_messages_from_conversation(conv)
    
    # Filter messages within the last 12 months
    filtered_messages = []
    for msg in messages:
        try:
            msg_dt = datetime.fromtimestamp(msg['timestamp'])
            if msg_dt >= cutoff_date:
                filtered_messages.append(msg)
        except (ValueError, OSError):
            continue
    
    return (conv_id, filtered_messages)


def process_month_data(args: Tuple[str, List[Tuple[str, List[Dict[str, Any]]]]]) -> Tuple[str, Dict[str, List[List[Dict[str, Any]]]]]:
    """
    Process all conversations for a specific month.
    Groups messages from the same conversation together.
    Returns (month, {conv_id: [[message_dicts]]})
    """
    month, conversations = args
    month_data = defaultdict(list)
    
    for conv_id, messages in conversations:
        if not messages:
            continue
        
        # Process messages for this conversation
        conversation_messages = []
        for msg in messages:
            cleaned_content = clean_content(msg['content'])
            if cleaned_content:
                conversation_messages.append({
                    'timestamp': format_timestamp(msg['timestamp']),
                    'role': msg['role'],
                    'cleaned_content': cleaned_content
                })
        
        if conversation_messages:
            # All messages from same conversation go in one subarray
            month_data[conv_id].append(conversation_messages)
    
    return (month, dict(month_data))


def main():
    print("ChatGPT Conversation History Compression Tool")
    print("=" * 60)
    
    # Load conversations.json
    input_file = 'conversations.json'
    try:
        print(f"\nLoading {input_file}...")
        with open(input_file, 'r', encoding='utf-8') as f:
            conversations = json.load(f)
        print(f"Loaded {len(conversations)} conversations")
    except FileNotFoundError:
        print(f"Error: {input_file} not found!")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {input_file}: {e}")
        sys.exit(1)
    
    # Calculate cutoff date (12 months ago)
    cutoff_date = datetime.now() - timedelta(days=365)
    print(f"Filtering conversations from {cutoff_date.strftime('%Y-%m-%d')} onwards...")
    
    # Step 1: Extract and filter messages from all conversations
    print("\nExtracting messages from conversations...")
    all_conversation_data = []
    
    for conv in conversations:
        conv_id, messages = process_conversation(conv, cutoff_date)
        if messages:
            all_conversation_data.append((conv_id, messages))
    
    print(f"Found {len(all_conversation_data)} conversations with messages in the last 12 months")
    
    if not all_conversation_data:
        print("No conversations found in the specified time range!")
        sys.exit(0)
    
    # Step 2: Group by month for parallel processing
    print("\nGrouping messages by month...")
    month_conversations = defaultdict(list)
    hour_conversations = defaultdict(list)
    
    for conv_id, messages in all_conversation_data:
        # Group by month
        month_messages = defaultdict(list)
        hour_messages = defaultdict(list)
        
        for msg in messages:
            month = get_month_bucket(msg['timestamp'])
            hour = get_hour_bucket(msg['timestamp'])
            
            month_messages[month].append(msg)
            hour_messages[hour].append(msg)
        
        # Store conversation data for each month it appears in
        for month, msgs in month_messages.items():
            month_conversations[month].append((conv_id, msgs))
        
        # Store conversation data for each hour it appears in
        for hour, msgs in hour_messages.items():
            hour_conversations[hour].append((conv_id, msgs))
    
    print(f"Messages span {len(month_conversations)} months")
    print(f"Messages span {len(hour_conversations)} hours of the day")
    
    # Step 3: Parallel process by month
    print("\nProcessing months in parallel...")
    num_workers = min(cpu_count(), len(month_conversations))
    print(f"Using {num_workers} workers")
    
    month_args = list(month_conversations.items())
    
    with Pool(num_workers) as pool:
        month_results = pool.map(process_month_data, month_args)
    
    # Collect month results
    by_month = {}
    for month, data in month_results:
        by_month[month] = data
    
    # Step 4: Process hour data (single-threaded as it's typically less data)
    print("\nProcessing hourly groupings...")
    by_hour = {}
    
    for hour in sorted(hour_conversations.keys()):
        hour_data = defaultdict(list)
        
        for conv_id, messages in hour_conversations[hour]:
            conversation_messages = []
            for msg in messages:
                cleaned_content = clean_content(msg['content'])
                if cleaned_content:
                    conversation_messages.append({
                        'timestamp': format_timestamp(msg['timestamp']),
                        'role': msg['role'],
                        'cleaned_content': cleaned_content
                    })
            
            if conversation_messages:
                hour_data[conv_id].append(conversation_messages)
        
        if hour_data:
            by_hour[hour] = dict(hour_data)
    
    # Step 5: Create final output structure
    output = {
        'metadata': {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cutoff_date': cutoff_date.strftime('%Y-%m-%d'),
            'total_conversations': len(all_conversation_data),
            'months_covered': len(by_month),
            'hours_covered': len(by_hour)
        },
        'by_month': by_month,
        'by_hour': by_hour
    }
    
    # Step 6: Write output
    output_file = 'compressed_conversations.json'
    print(f"\nWriting compressed output to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Successfully compressed {len(all_conversation_data)} conversations")
    print(f"✓ Output written to {output_file}")
    print(f"\nStatistics:")
    print(f"  - Months with data: {len(by_month)}")
    print(f"  - Hours with data: {len(by_hour)}")
    print(f"  - Time range: {cutoff_date.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}")
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()