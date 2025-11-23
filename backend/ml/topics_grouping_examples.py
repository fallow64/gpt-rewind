#!/usr/bin/env python3
"""
Examples of how to group and analyze topics from question_analytics results.
"""

import json
from collections import defaultdict
from typing import List, Dict, Any


def group_topics_by_month(all_topics: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
    """Group all topics by month."""
    by_month = defaultdict(list)
    for topic in all_topics:
        by_month[topic['month']].append(topic)
    return dict(by_month)


def group_topics_by_conversation(all_topics: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
    """Group all topics by conversation ID."""
    by_conv = defaultdict(list)
    for topic in all_topics:
        by_conv[topic['conv_id']].append(topic)
    return dict(by_conv)


def group_topics_by_difficulty_range(all_topics: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
    """Group topics by difficulty score ranges."""
    ranges = {
        'very_easy': [],    # < 0
        'easy': [],         # 0-50
        'medium': [],       # 50-100
        'hard': [],         # 100-200
        'very_hard': []     # > 200
    }
    
    for topic in all_topics:
        score = topic['difficulty_score']
        if score < 0:
            ranges['very_easy'].append(topic)
        elif score < 50:
            ranges['easy'].append(topic)
        elif score < 100:
            ranges['medium'].append(topic)
        elif score < 200:
            ranges['hard'].append(topic)
        else:
            ranges['very_hard'].append(topic)
    
    return ranges


def get_top_n_hardest_topics(all_topics: List[Dict[str, Any]], n: int = 10) -> List[Dict]:
    """Get the N hardest topics."""
    return sorted(all_topics, key=lambda x: x['difficulty_score'], reverse=True)[:n]


def get_topics_with_frustration(all_topics: List[Dict[str, Any]]) -> List[Dict]:
    """Get all topics that had frustration signals."""
    return [t for t in all_topics if t['metrics'].get('frustration_flag', False)]


def group_topics_by_hour_of_day(all_topics: List[Dict[str, Any]]) -> Dict[int, List[Dict]]:
    """Group topics by hour of day (0-23)."""
    from datetime import datetime
    
    by_hour = defaultdict(list)
    for topic in all_topics:
        if topic.get('timestamp'):
            try:
                # Parse timestamp and extract hour
                ts = datetime.fromisoformat(topic['timestamp'].replace('Z', '+00:00'))
                hour = ts.hour
                by_hour[hour].append(topic)
            except:
                pass
    
    return dict(by_hour)


def get_topic_statistics(all_topics: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Get overall statistics about topics."""
    if not all_topics:
        return {}
    
    difficulty_scores = [t['difficulty_score'] for t in all_topics]
    
    return {
        'total_topics': len(all_topics),
        'avg_difficulty': sum(difficulty_scores) / len(difficulty_scores),
        'min_difficulty': min(difficulty_scores),
        'max_difficulty': max(difficulty_scores),
        'topics_with_frustration': sum(1 for t in all_topics if t['metrics'].get('frustration_flag')),
        'topics_with_resolution': sum(1 for t in all_topics if t['metrics'].get('resolution_flag')),
        'avg_followups': sum(t['metrics'].get('followup_count', 0) for t in all_topics) / len(all_topics),
        'avg_duration_minutes': sum(t['metrics'].get('duration_seconds', 0) for t in all_topics) / len(all_topics) / 60,
    }


def load_segmented_topics(segmented_file: str = 'segmented_conversations.json') -> Dict[str, Any]:
    """
    Load the detailed segmented conversations with full message content.
    This gives you access to the actual messages in each topic.
    """
    with open(segmented_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_topics_with_messages(segmented_file: str = 'segmented_conversations.json') -> List[Dict]:
    """
    Extract all topics with their full messages from segmented file.
    Returns a flat list of topic dicts with messages.
    """
    segmented = load_segmented_topics(segmented_file)
    all_topics_with_messages = []
    
    for month, convs in segmented.get('segmented_conversations', {}).items():
        for conv_id, conv_data in convs.items():
            for topic in conv_data['topics']:
                topic_info = {
                    'month': month,
                    'conv_id': conv_id,
                    'topic_id': topic['topic_id'],
                    'difficulty_score': topic['difficulty_score'],
                    'metrics': topic['metrics'],
                    'messages': topic['messages'],  # Full message content!
                    'num_messages': topic['num_messages'],
                    'timestamp': topic['timestamp']
                }
                all_topics_with_messages.append(topic_info)
    
    return all_topics_with_messages


# Example usage
if __name__ == '__main__':
    # Load analytics results
    with open('questions_analytics.json', 'r') as f:
        analytics = json.load(f)
    
    # If you ran analyze_questions, you can also get all_topics from the return value
    # But for this example, we'll work with what's already saved
    
    # Load segmented data to get all topics
    segmented = load_segmented_topics()
    
    # Extract all topics into a flat list
    all_topics = []
    for month, convs in segmented.get('segmented_conversations', {}).items():
        for conv_id, conv_data in convs.items():
            for topic in conv_data['topics']:
                all_topics.append({
                    'month': month,
                    'conv_id': conv_id,
                    'topic_id': topic['topic_id'],
                    'difficulty_score': topic['difficulty_score'],
                    'metrics': topic['metrics'],
                    'question_id': topic['representative_question_id'],
                    'response_id': topic['representative_response_id'],
                    'timestamp': topic['timestamp']
                })
    
    print(f"Total topics found: {len(all_topics)}")
    
    # Group by month
    by_month = group_topics_by_month(all_topics)
    print(f"\nTopics by month:")
    for month, topics in sorted(by_month.items()):
        print(f"  {month}: {len(topics)} topics")
    
    # Group by difficulty
    by_difficulty = group_topics_by_difficulty_range(all_topics)
    print(f"\nTopics by difficulty:")
    for range_name, topics in by_difficulty.items():
        print(f"  {range_name}: {len(topics)} topics")
    
    # Get statistics
    stats = get_topic_statistics(all_topics)
    print(f"\nOverall statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")
    
    # Get top 5 hardest
    hardest = get_top_n_hardest_topics(all_topics, 5)
    print(f"\nTop 5 hardest topics:")
    for i, topic in enumerate(hardest, 1):
        print(f"  {i}. Score: {topic['difficulty_score']:.2f} (Month: {topic['month']}, Conv: {topic['conv_id'][:8]}...)")
    
    # Topics with frustration
    frustrated = get_topics_with_frustration(all_topics)
    print(f"\nTopics with frustration: {len(frustrated)}")
