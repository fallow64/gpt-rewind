"""
ML package for GPT Rewind

Contains modules for:
- conversation_compression: Process and compress ChatGPT conversation exports
- embeddings: Generate embeddings using GTE-Large model
- question_analytics: Analyze question difficulty and topics
- pipeline: Unified interface for running the complete ML pipeline
"""

from .pipeline import run_pipeline, run_pipeline_async

__all__ = ['run_pipeline', 'run_pipeline_async']
