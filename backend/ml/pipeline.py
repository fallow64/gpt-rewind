#!/usr/bin/env python3
"""
ML Pipeline Integration Module

This module provides a unified interface to run the complete ML pipeline:
1. Conversation compression and analytics
2. Embedding generation
3. Question difficulty analysis
4. Insight extraction for frontend

Usage:
    from ml.pipeline import run_pipeline
    
    results = run_pipeline(
        conversation_file='path/to/conversations.json',
        output_dir='path/to/output'
    )
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

# Import processing functions from ML modules
from ml.conversation_compression import process_conversations
from ml.embeddings import generate_embeddings
from ml.question_analytics import analyze_questions


def run_pipeline(conversation_file: str, output_dir: str, 
                 enable_embeddings: bool = True,
                 enable_analytics: bool = True) -> Dict[str, Any]:
    """
    Run the complete ML pipeline on a conversation export file.
    
    Args:
        conversation_file: Path to the conversations.json export file
        output_dir: Directory to write all output files
        enable_embeddings: Whether to run embedding generation (requires GPU/large RAM)
        enable_analytics: Whether to run question analytics (requires embeddings)
    
    Returns:
        Dictionary containing:
        - success: bool
        - error: str (if failed)
        - compression_result: dict from compression step
        - embedding_result: dict from embedding step (if enabled)
        - analytics_result: dict from analytics step (if enabled)
        - insights: dict of extracted insights for frontend
    """
    
    result = {
        'success': False,
        'error': None,
        'compression_result': None,
        'embedding_result': None,
        'analytics_result': None,
        'insights': None
    }
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "=" * 80)
    print("STARTING ML PIPELINE")
    print("=" * 80)
    print(f"Input: {conversation_file}")
    print(f"Output: {output_dir}")
    print(f"Embeddings: {'ENABLED' if enable_embeddings else 'DISABLED'}")
    print(f"Analytics: {'ENABLED' if enable_analytics else 'DISABLED'}")
    print("=" * 80 + "\n")
    
    try:
        # STEP 1: Compression and basic analytics
        print("\n--- STEP 1: CONVERSATION COMPRESSION ---")
        compression_result = process_conversations(conversation_file, output_dir)
        result['compression_result'] = compression_result
        
        if not compression_result['compressed_file']:
            result['error'] = "No conversations found in time range"
            return result
        
        print(f"✓ Compression complete: {compression_result['compressed_file']}")
        
        # STEP 2: Embedding generation (optional, resource intensive)
        if enable_embeddings:
            print("\n--- STEP 2: EMBEDDING GENERATION ---")
            try:
                embedding_result = generate_embeddings(
                    compression_result['compressed_file'],
                    os.path.join(output_dir, 'embedded_conversations.json')
                )
                result['embedding_result'] = embedding_result
                print(f"✓ Embeddings complete: {embedding_result['output_file']}")
            except Exception as e:
                print(f"⚠ Warning: Embedding generation failed: {e}")
                print("⚠ Continuing without embeddings...")
                enable_embeddings = False
        
        # STEP 3: Question analytics (requires embeddings)
        if enable_analytics and enable_embeddings:
            print("\n--- STEP 3: QUESTION ANALYTICS ---")
            try:
                analytics_result = analyze_questions(
                    result['embedding_result']['output_file'],
                    output_dir=output_dir
                )
                result['analytics_result'] = analytics_result
                print(f"✓ Analytics complete: {analytics_result.get('questions_file')}")
            except Exception as e:
                print(f"⚠ Warning: Question analytics failed: {e}")
                print("⚠ Continuing without question analytics...")
        
        # STEP 4: Extract insights for frontend
        print("\n--- STEP 4: INSIGHT EXTRACTION ---")
        insights = extract_insights(
            compression_result=compression_result,
            analytics_result=result.get('analytics_result'),
            output_dir=output_dir
        )
        result['insights'] = insights
        print(f"✓ Extracted {len(insights)} insights")
        
        result['success'] = True
        
        print("\n" + "=" * 80)
        print("PIPELINE COMPLETE")
        print("=" * 80 + "\n")
        
    except Exception as e:
        result['error'] = str(e)
        print(f"\n✗ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
    
    return result


def extract_insights(compression_result: Dict[str, Any], 
                     analytics_result: Optional[Dict[str, Any]],
                     output_dir: str) -> Dict[str, Any]:
    """
    Extract insights from analysis results and format for frontend.
    
    Returns a dictionary with insights for pages -1 through 10.
    """
    
    insights = {}
    
    # Load analytics data
    analytics = compression_result.get('analytics', {})
    yearly = analytics.get('yearly_totals', {})
    monthly = analytics.get('monthly_stats', {})
    peak_usage = analytics.get('peak_usage', {})
    longest_conv = analytics.get('longest_conversation', {})
    
    # Page -1: Introduction / Welcome
    insights[-1] = {
        'type': 'intro',
    }
    
    # Page 0: Total hours
    insights[0] = {
        'type': 'total_hours',
        'data': yearly.get('total_hours', 0),
    }
    
    # Page 1: Hours by month
    insights[1] = {
        'type': 'hours_by_month',
        'data': {month: stats.get('total_hours', 0) for month, stats in monthly.items()},
    }
    
    # Page 2: Hours by time of day
    # Aggregate hourly distribution across all months
    hourly_dist = {}
    for month_stats in monthly.values():
        for hour, count in month_stats.get('hourly_distribution', {}).items():
            hourly_dist[int(hour)] = hourly_dist.get(int(hour), 0) + count
    
    insights[2] = {
        'type': 'hours_by_hour',
        'data': hourly_dist,
    }
    
    # Page 3: Longest conversation
    insights[3] = {
        'type': 'longest_conversation',
        'data': longest_conv.get('duration_hours', 0),
    }
    
    # Page 4: Easiest question (if available)
    if analytics_result and analytics_result.get('easiest'):
        easiest = analytics_result['easiest']
        insights[4] = {
            'type': 'easiest_question',
            'data': easiest.get('text', ''),
        }
    else:
        insights[4] = {
            'type': 'easiest_question',
            'data': 'Embedding-based analysis was not run'
        }
    
    # Page 5: Hardest question (if available)
    if analytics_result and analytics_result.get('hardest'):
        hardest = analytics_result['hardest']
        insights[5] = {
            'type': 'hardest_question',
            'data': hardest.get('text', ''),
        }
    else:
        insights[5] = {
            'type': 'hardest_question',
            'data': 'Analysis not available',
        }
    
    # Page 6: Top 3 topics by followup count
    if analytics_result and analytics_result.get('all_topics'):
        all_topics = analytics_result['all_topics']
        # Sort by followup count (number of back-and-forth exchanges)
        sorted_topics = sorted(all_topics, key=lambda x: x.get('metrics', {}).get('followup_count', 0), reverse=True)[:3]
        
        # Get the actual question text for each top topic
        top_topics_data = []
        for topic in sorted_topics:
            # Try to get the question text from the topic
            question_id = topic.get('question_id', '')
            topic_desc = f"Topic {topic.get('topic_id', '?')} (Score: {topic.get('difficulty_score', 0):.1f})"
            if question_id:
                topic_desc = f"{topic.get('conv_id', 'Unknown')[:8]}... - {topic.get('metrics', {}).get('followup_count', 0)} exchanges"
            top_topics_data.append(topic_desc)
        
        insights[6] = {
            'type': 'top_topics',
            'data': top_topics_data if top_topics_data else ['No topics', 'available', 'yet'],
        }
    else:
        insights[6] = {
            'type': 'top_topics',
            'data': ['Analysis not run', 'Enable embeddings', 'to see topics'],
        }
    
    # Page 7: Most discussed topic per month
    if analytics_result and analytics_result.get('all_topics'):
        all_topics = analytics_result['all_topics']
        
        # Group topics by month
        topics_by_month = {}
        for topic in all_topics:
            month = topic.get('month', 'Unknown')
            if month not in topics_by_month:
                topics_by_month[month] = []
            topics_by_month[month].append(topic)
        
        # Get the most discussed topic per month (highest followup count)
        most_discussed_per_month = {}
        for month, month_topics in topics_by_month.items():
            if month_topics:
                top_topic = max(month_topics, key=lambda t: t.get('metrics', {}).get('followup_count', 0))
                # Create a description of the topic
                followup_count = top_topic.get('metrics', {}).get('followup_count', 0)
                difficulty = top_topic.get('difficulty_score', 0)
                most_discussed_per_month[month] = f"Difficulty {difficulty:.0f} ({followup_count} exchanges)"
        
        insights[7] = {
            'type': 'topics_by_month',
            'data': most_discussed_per_month if most_discussed_per_month else {'No data': 'No topics found'},
        }
    else:
        insights[7] = {
            'type': 'topics_by_month',
            'data': {'No data': 'Analysis not run - enable embeddings'},
        }
    
    # Page 8: Average topic difficulty by hour of day
    if analytics_result and analytics_result.get('all_topics'):
        from datetime import datetime as dt
        from collections import defaultdict
        
        all_topics = analytics_result['all_topics']
        
        # Group topics by hour of day
        topics_by_hour = defaultdict(list)
        for topic in all_topics:
            timestamp = topic.get('timestamp', '')
            if timestamp:
                try:
                    ts = dt.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hour = ts.hour
                    topics_by_hour[hour].append(topic)
                except:
                    pass
        
        # Calculate average difficulty per hour
        avg_difficulty_by_hour = {}
        for hour in range(24):
            if hour in topics_by_hour and topics_by_hour[hour]:
                topics = topics_by_hour[hour]
                avg_diff = sum(t.get('difficulty_score', 0) for t in topics) / len(topics)
                avg_difficulty_by_hour[hour] = f"Avg difficulty: {avg_diff:.1f} ({len(topics)} topics)"
            else:
                avg_difficulty_by_hour[hour] = "No topics"
        
        insights[8] = {
            'type': 'topics_by_hour',
            'data': avg_difficulty_by_hour,
        }
    else:
        insights[8] = {
            'type': 'topics_by_hour',
            'data': {hour: 'Analysis not run' for hour in range(24)},
        }
    
    # Page 9: Outro
    insights[9] = {
        'type': 'outro',
        'data': {
            'total_hours': yearly.get('total_hours', 0),
            'total_messages': yearly.get('total_messages', 0)
        }
    }
    
    # Save insights to individual JSON files
    insights_dir = os.path.join(output_dir, 'insights')
    os.makedirs(insights_dir, exist_ok=True)
    
    for page_index, insight_data in insights.items():
        insight_file = os.path.join(insights_dir, f"{page_index}.json")
        with open(insight_file, 'w', encoding='utf-8') as f:
            json.dump(insight_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved {len(insights)} insight files to {insights_dir}")
    
    return insights


def run_pipeline_async(conversation_file: str, output_dir: str, 
                       enable_embeddings: bool = False,
                       enable_analytics: bool = False):
    """
    Async wrapper for running the pipeline (can be called from FastAPI).
    
    Note: By default, embeddings and analytics are disabled for faster processing.
    They can be enabled but require significant compute resources.
    """
    import asyncio
    
    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(
        None, 
        run_pipeline,
        conversation_file,
        output_dir,
        enable_embeddings,
        enable_analytics
    )


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m ml.pipeline <conversation_file> [output_dir] [--no-embeddings] [--no-analytics]")
        sys.exit(1)
    
    conversation_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else './output'
    
    # Parse flags
    enable_embeddings = '--no-embeddings' not in sys.argv
    enable_analytics = '--no-analytics' not in sys.argv
    
    result = run_pipeline(
        conversation_file, 
        output_dir,
        enable_embeddings=enable_embeddings,
        enable_analytics=enable_analytics
    )
    
    if result['success']:
        print("\n✓ Pipeline completed successfully!")
    else:
        print(f"\n✗ Pipeline failed: {result['error']}")
        sys.exit(1)
