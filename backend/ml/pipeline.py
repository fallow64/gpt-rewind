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
                    output_file=os.path.join(output_dir, 'embedded_conversations.json')
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
        'message': 'Welcome to GPT Rewind!'
    }
    
    # Page 0: Total hours
    insights[0] = {
        'type': 'total_hours',
        'value': yearly.get('total_hours', 0),
        'total_messages': yearly.get('total_messages', 0),
        'total_conversations': yearly.get('total_conversations', 0)
    }
    
    # Page 1: Hours by month
    insights[1] = {
        'type': 'hours_by_month',
        'data': {month: stats.get('total_hours', 0) for month, stats in monthly.items()},
        'peak_month': max(monthly.items(), key=lambda x: x[1].get('total_hours', 0))[0] if monthly else None
    }
    
    # Page 2: Hours by time of day
    # Aggregate hourly distribution across all months
    hourly_dist = {}
    for month_stats in monthly.values():
        for hour, count in month_stats.get('hourly_distribution', {}).items():
            hourly_dist[int(hour)] = hourly_dist.get(int(hour), 0) + count
    
    insights[2] = {
        'type': 'hours_by_time',
        'data': hourly_dist,
        'peak_hour': peak_usage.get('hour_of_day'),
        'peak_count': peak_usage.get('message_count', 0)
    }
    
    # Page 3: Longest conversation
    insights[3] = {
        'type': 'longest_conversation',
        'duration_hours': longest_conv.get('duration_hours', 0),
        'conversation_id': longest_conv.get('conversation_id')
    }
    
    # Page 4: Easiest question (if available)
    if analytics_result and analytics_result.get('easiest'):
        easiest = analytics_result['easiest']
        insights[4] = {
            'type': 'easiest_question',
            'text': easiest.get('text', ''),
            'score': easiest.get('score', 0),
            'metrics': easiest.get('metrics', {})
        }
    else:
        insights[4] = {
            'type': 'easiest_question',
            'text': 'Analysis not available',
            'note': 'Embedding-based analysis was not run'
        }
    
    # Page 5: Hardest question (if available)
    if analytics_result and analytics_result.get('hardest'):
        hardest = analytics_result['hardest']
        insights[5] = {
            'type': 'hardest_question',
            'text': hardest.get('text', ''),
            'score': hardest.get('score', 0),
            'metrics': hardest.get('metrics', {})
        }
    else:
        insights[5] = {
            'type': 'hardest_question',
            'text': 'Analysis not available',
            'note': 'Embedding-based analysis was not run'
        }
    
    # Page 6: Profession/field (placeholder - would need topic modeling)
    insights[6] = {
        'type': 'profession',
        'field': 'Technology',  # Placeholder
        'confidence': 0.0,
        'note': 'Advanced topic modeling not yet implemented'
    }
    
    # Page 7: Top 3 topics (placeholder - would need topic extraction)
    if analytics_result and analytics_result.get('all_topics'):
        # Group topics by their metrics to find most discussed
        all_topics = analytics_result['all_topics']
        # Sort by number of messages in topic (using difficulty as proxy for now)
        sorted_topics = sorted(all_topics, key=lambda x: x.get('metrics', {}).get('followup_count', 0), reverse=True)[:3]
        
        insights[7] = {
            'type': 'top_topics',
            'topics': [
                {
                    'rank': i + 1,
                    'description': f"Topic {i + 1}",
                    'message_count': topic.get('metrics', {}).get('followup_count', 0)
                }
                for i, topic in enumerate(sorted_topics)
            ]
        }
    else:
        insights[7] = {
            'type': 'top_topics',
            'topics': [],
            'note': 'Topic analysis not available'
        }
    
    # Page 8: Topics per month (placeholder)
    insights[8] = {
        'type': 'topics_per_month',
        'data': {},
        'note': 'Advanced topic tracking not yet implemented'
    }
    
    # Page 9: Topics per hour (placeholder)
    insights[9] = {
        'type': 'topics_per_hour',
        'data': {},
        'note': 'Advanced topic tracking not yet implemented'
    }
    
    # Page 10: Outro
    insights[10] = {
        'type': 'outro',
        'message': 'Thanks for using GPT Rewind!',
        'summary': {
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
        print("Usage: python -m ml.pipeline <conversation_file> [output_dir]")
        sys.exit(1)
    
    conversation_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './output'
    
    result = run_pipeline(conversation_file, output_dir)
    
    if result['success']:
        print("\n✓ Pipeline completed successfully!")
    else:
        print(f"\n✗ Pipeline failed: {result['error']}")
        sys.exit(1)
