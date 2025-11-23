#!/usr/bin/env python3
"""
ChatGPT Conversation History Compression and Analysis Tool

This script processes ChatGPT conversation exports and:
- Filters conversations from the last 12 months
- Groups messages by month
- Removes stopwords and cleans content
- Uses multiprocessing for parallel processing
- Tracks usage hours per month (accounting for idle time)
- Finds peak usage hours
- Estimates costs
- Outputs compressed JSON structure and analytics
- Creates conversations_with_msg_id.json with all raw messages + IDs
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

# Configuration
IDLE_THRESHOLD_MINUTES = 30
MIN_SESSION_DURATION_MINUTES = 0
LAST_MESSAGE_PADDING_MINUTES = 10

# GPU cost estimation
GPU_COST_PER_HOUR = 2.0
ELECTRICITY_COST_PER_HOUR = 0.50
DEVELOPMENT_COST_PER_HOUR = 10.0
TOTAL_INSTANCE_COST_PER_HOUR = GPU_COST_PER_HOUR + ELECTRICITY_COST_PER_HOUR + DEVELOPMENT_COST_PER_HOUR


def clean_content(text: str) -> List[str]:
    """
    Clean message content by:
    1. Removing stopwords
    2. Returning cleaned content as a single entry (the entire message)
    """
    if not text or not isinstance(text, str):
        return []
    
    # Tokenize and remove stopwords from entire message
    words = re.findall(r'\b[a-z]+\b', text.lower())
    filtered_words = [w for w in words if w not in STOPWORDS and len(w) > 2]
    
    if filtered_words:
        return [' '.join(filtered_words)]
    
    return []


def extract_messages_from_conversation(conv: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract all messages from a conversation mapping structure.
    Includes unique message IDs based on node IDs.
    """
    messages = []
    mapping = conv.get('mapping', {})
    conv_id = conv.get('id', 'unknown')
    
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
        
        # Create unique message ID: conv_id + node_id
        message_id = f"{conv_id}_{node_id}"
        
        messages.append({
            'id': message_id,
            'timestamp': create_time,
            'role': role,
            'content': text,
            'conversation_id': conv_id
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


def get_hour_of_day(ts: float) -> int:
    """Get hour of day (0-23) from timestamp."""
    try:
        dt = datetime.fromtimestamp(ts)
        return dt.hour
    except (ValueError, OSError):
        return 0


def calculate_active_duration(messages: List[Dict[str, Any]], idle_threshold_minutes: int = IDLE_THRESHOLD_MINUTES) -> float:
    """
    Calculate total active duration in hours for a list of messages.
    """
    if not messages:
        return 0.0
    
    if len(messages) == 1:
        return (MIN_SESSION_DURATION_MINUTES + LAST_MESSAGE_PADDING_MINUTES) / 60.0
    
    sorted_msgs = sorted(messages, key=lambda x: x['timestamp'])
    sessions = []
    current_session = [sorted_msgs[0]]
    idle_threshold_seconds = idle_threshold_minutes * 60
    
    for i in range(1, len(sorted_msgs)):
        time_diff = sorted_msgs[i]['timestamp'] - sorted_msgs[i - 1]['timestamp']
        
        if time_diff <= idle_threshold_seconds:
            current_session.append(sorted_msgs[i])
        else:
            sessions.append(current_session)
            current_session = [sorted_msgs[i]]
    
    sessions.append(current_session)
    
    total_duration_seconds = 0.0
    padding_seconds = LAST_MESSAGE_PADDING_MINUTES * 60
    
    for session in sessions:
        if len(session) == 1:
            total_duration_seconds += (MIN_SESSION_DURATION_MINUTES * 60) + padding_seconds
        else:
            session_duration = session[-1]['timestamp'] - session[0]['timestamp']
            total_duration_seconds += session_duration + padding_seconds
    
    return total_duration_seconds / 3600.0


def get_conversation_duration(messages: List[Dict[str, Any]]) -> float:
    """Get duration in hours for a conversation."""
    if not messages:
        return 0.0
    return calculate_active_duration(messages)


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


def process_month_data(args: Tuple[str, List[Tuple[str, List[Dict[str, Any]]]]]) -> Tuple[str, Dict[str, Any]]:
    """
    Process all conversations for a specific month.
    """
    month, conversations = args
    month_data = defaultdict(list)
    
    # Analytics for this month
    total_hours = 0.0
    message_count = 0
    hourly_distribution = defaultdict(int)
    longest_conv_duration = 0.0
    longest_conv_id = None
    
    for conv_id, messages in conversations:
        if not messages:
            continue
        
        conv_duration = get_conversation_duration(messages)
        total_hours += conv_duration
        
        if conv_duration > longest_conv_duration:
            longest_conv_duration = conv_duration
            longest_conv_id = conv_id
        
        for msg in messages:
            hour = get_hour_of_day(msg['timestamp'])
            hourly_distribution[hour] += 1
        
        # Process messages for this conversation
        conversation_messages = []
        for msg in messages:
            cleaned_content = clean_content(msg['content'])
            if cleaned_content:
                conversation_messages.append({
                    'id': msg['id'],  # Include message ID
                    'timestamp': format_timestamp(msg['timestamp']),
                    'role': msg['role'],
                    'content': msg['content'],  # Keep raw content
                    'cleaned_content': cleaned_content
                })
        
        if conversation_messages:
            message_count += len(conversation_messages)
            month_data[conv_id].append(conversation_messages)
    
    peak_hour = None
    peak_hour_count = 0
    if hourly_distribution:
        peak_hour_tuple = max(hourly_distribution.items(), key=lambda x: x[1])
        peak_hour = peak_hour_tuple[0]
        peak_hour_count = peak_hour_tuple[1]
    
    analytics = {
        'total_hours': round(total_hours, 2),
        'conversation_count': len(month_data),
        'message_count': message_count,
        'peak_hour': {
            'hour_of_day': peak_hour,
            'message_count': peak_hour_count
        },
        'hourly_distribution': dict(hourly_distribution),
        'longest_conversation_id': longest_conv_id,
        'longest_conversation_duration': round(longest_conv_duration, 2)
    }
    
    return (month, {
        'conversations': dict(month_data),
        'analytics': analytics
    })


def consolidate_analytics(month_results: List[Tuple[str, Dict[str, Any]]]) -> Dict[str, Any]:
    """Consolidate analytics from all monthly results."""
    analytics = {
        'monthly_stats': {},
        'yearly_totals': {
            'total_hours': 0.0,
            'total_conversations': 0,
            'total_messages': 0
        },
        'peak_usage': {
            'hour_of_day': None,
            'message_count': 0
        },
        'longest_conversation': {
            'conversation_id': None,
            'duration_hours': 0.0
        }
    }
    
    global_hourly_distribution = defaultdict(int)
    
    for month, data in month_results:
        month_analytics = data['analytics']
        analytics['monthly_stats'][month] = month_analytics
        analytics['yearly_totals']['total_hours'] += month_analytics['total_hours']
        analytics['yearly_totals']['total_conversations'] += month_analytics['conversation_count']
        analytics['yearly_totals']['total_messages'] += month_analytics['message_count']
        
        for hour, count in month_analytics['hourly_distribution'].items():
            global_hourly_distribution[int(hour)] += count
        
        if month_analytics['longest_conversation_duration'] > analytics['longest_conversation']['duration_hours']:
            analytics['longest_conversation']['conversation_id'] = month_analytics['longest_conversation_id']
            analytics['longest_conversation']['duration_hours'] = month_analytics['longest_conversation_duration']
    
    analytics['yearly_totals']['total_hours'] = round(analytics['yearly_totals']['total_hours'], 2)
    
    total_hours = analytics['yearly_totals']['total_hours']
    estimated_cost = total_hours * TOTAL_INSTANCE_COST_PER_HOUR
    analytics['yearly_totals']['estimated_cost_usd'] = round(estimated_cost, 2)
    analytics['yearly_totals']['cost_breakdown'] = {
        'gpu_cost_per_hour': GPU_COST_PER_HOUR,
        'electricity_cost_per_hour': ELECTRICITY_COST_PER_HOUR,
        'development_cost_per_hour': DEVELOPMENT_COST_PER_HOUR,
        'total_cost_per_hour': TOTAL_INSTANCE_COST_PER_HOUR,
        'note': 'Development cost includes amortized R&D, training, and infrastructure'
    }
    
    if global_hourly_distribution:
        peak_hour = max(global_hourly_distribution.items(), key=lambda x: x[1])
        analytics['peak_usage'] = {
            'hour_of_day': peak_hour[0],
            'message_count': peak_hour[1]
        }
    
    return analytics


def create_conversations_with_msg_id(all_conversation_data: List[Tuple[str, List[Dict[str, Any]]]]) -> Dict[str, Any]:
    """
    Create conversations_with_msg_id structure: messages grouped by month only (flattened).
    
    Structure:
    {
        '2024-01': [all messages from Jan],
        '2024-02': [all messages from Feb],
        ...
    }
    """
    messages_by_month = defaultdict(list)
    
    for conv_id, messages in all_conversation_data:
        for msg in messages:
            month = get_month_bucket(msg['timestamp'])
            messages_by_month[month].append({
                'id': msg['id'],
                'timestamp': format_timestamp(msg['timestamp']),
                'role': msg['role'],
                'content': msg['content'],
                'conversation_id': conv_id
            })
    
    # Sort messages within each month by timestamp
    for month in messages_by_month:
        messages_by_month[month].sort(key=lambda x: x['timestamp'])
    
    return dict(messages_by_month)


def main():
    print("ChatGPT Conversation History Compression & Analysis Tool")
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
    
    # Step 1: Extract and filter messages
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
    
    # Step 2: Create conversations_with_msg_id.json
    print("\nCreating conversations_with_msg_id structure...")
    messages_by_month = create_conversations_with_msg_id(all_conversation_data)
    
    msg_id_file = 'conversations_with_msg_id.json'
    print(f"Writing to {msg_id_file}...")
    
    # Count total messages
    total_messages = sum(len(msgs) for msgs in messages_by_month.values())
    
    with open(msg_id_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'cutoff_date': cutoff_date.strftime('%Y-%m-%d'),
                'total_messages': total_messages,
                'months_covered': len(messages_by_month),
                'note': 'All messages with IDs, flattened and grouped by month only'
            },
            'by_month': messages_by_month
        }, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved {msg_id_file} ({total_messages:,} messages)")
    
    # Step 3: Group by month for parallel processing
    print("\nGrouping messages by month for compression...")
    month_conversations = defaultdict(list)
    
    for conv_id, messages in all_conversation_data:
        month_messages = defaultdict(list)
        
        for msg in messages:
            month = get_month_bucket(msg['timestamp'])
            month_messages[month].append(msg)
        
        for month, msgs in month_messages.items():
            month_conversations[month].append((conv_id, msgs))
    
    print(f"Messages span {len(month_conversations)} months")
    
    # Step 4: Parallel process by month
    print("\nProcessing months in parallel (compression + analytics)...")
    num_workers = min(cpu_count(), len(month_conversations))
    print(f"Using {num_workers} workers")
    
    month_args = list(month_conversations.items())
    
    with Pool(num_workers) as pool:
        month_results = pool.map(process_month_data, month_args)
    
    # Step 5: Consolidate results
    print("\nConsolidating results...")
    by_month = {}
    for month, data in month_results:
        by_month[month] = data['conversations']
    
    analytics = consolidate_analytics(month_results)
    
    # Step 6: Create compressed output
    output = {
        'metadata': {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cutoff_date': cutoff_date.strftime('%Y-%m-%d'),
            'total_conversations': len(all_conversation_data),
            'months_covered': len(by_month),
            'idle_threshold_minutes': IDLE_THRESHOLD_MINUTES,
            'note': 'Compressed output with cleaned content and message IDs'
        },
        'by_month': by_month
    }
    
    # Step 7: Write compressed output
    output_file = 'compressed_conversations.json'
    print(f"\nWriting compressed output to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved {output_file}")
    
    # Step 8: Write analytics output
    analytics_file = 'conversation_analytics.json'
    print(f"Writing analytics to {analytics_file}...")
    
    with open(analytics_file, 'w', encoding='utf-8') as f:
        json.dump(analytics, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved {analytics_file}")
    
    # Step 9: Display summary
    print(f"\n✓ Successfully processed {len(all_conversation_data)} conversations")
    print(f"✓ Outputs created:")
    print(f"  - {msg_id_file} (all messages with IDs, grouped by month)")
    print(f"  - {output_file} (compressed with cleaned content and message IDs)")
    print(f"  - {analytics_file} (usage analytics)")
    
    print(f"\n{'=' * 60}")
    print("USAGE ANALYTICS SUMMARY")
    print(f"{'=' * 60}")
    print(f"\nTotal active hours (last 12 months): {analytics['yearly_totals']['total_hours']:.2f} hours")
    print(f"Total messages: {analytics['yearly_totals']['total_messages']:,}")
    print(f"Total conversations: {analytics['yearly_totals']['total_conversations']}")
    
    cost_breakdown = analytics['yearly_totals']['cost_breakdown']
    print(f"\nEstimated instance cost (including development):")
    print(f"  GPU cost: ${cost_breakdown['gpu_cost_per_hour']:.2f}/hour")
    print(f"  Electricity: ${cost_breakdown['electricity_cost_per_hour']:.2f}/hour")
    print(f"  Development (amortized): ${cost_breakdown['development_cost_per_hour']:.2f}/hour")
    print(f"  Total: ${cost_breakdown['total_cost_per_hour']:.2f}/hour")
    print(f"  Grand total: ${analytics['yearly_totals']['estimated_cost_usd']:,.2f}")
    
    if analytics['peak_usage']['hour_of_day'] is not None:
        peak_hour = analytics['peak_usage']['hour_of_day']
        print(f"\nPeak usage hour: {peak_hour:02d}:00 ({analytics['peak_usage']['message_count']:,} messages)")
    
    if analytics['longest_conversation']['conversation_id']:
        longest = analytics['longest_conversation']
        print(f"\nLongest conversation:")
        print(f"  ID: {longest['conversation_id']}")
        print(f"  Duration: {longest['duration_hours']:.2f} hours")
    
    print(f"\n{'=' * 60}")
    print("MONTHLY BREAKDOWN")
    print(f"{'=' * 60}")
    
    for month in sorted(analytics['monthly_stats'].keys()):
        stats = analytics['monthly_stats'][month]
        print(f"\n{month}:")
        print(f"  Hours: {stats['total_hours']:.2f}")
        print(f"  Conversations: {stats['conversation_count']}")
        print(f"  Messages: {stats['message_count']:,}")
        if stats['peak_hour']['hour_of_day'] is not None:
            print(f"  Peak hour: {stats['peak_hour']['hour_of_day']:02d}:00 ({stats['peak_hour']['message_count']:,} messages)")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()