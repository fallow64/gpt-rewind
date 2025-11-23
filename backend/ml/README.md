# ML Pipeline Documentation

This folder contains the machine learning pipeline for processing ChatGPT conversation exports and generating insights.

## Overview

The pipeline consists of three main stages:

1. **Conversation Compression** (`conversation_compression.py`)

   - Filters conversations from the last 12 months
   - Groups messages by month
   - Removes stopwords and cleans content
   - Tracks usage hours per month
   - Finds peak usage hours
   - Estimates costs

2. **Embedding Generation** (`embeddings.py`)

   - Generates embeddings using GTE-Large model
   - Optimized with GPU acceleration (CUDA)
   - Uses mixed precision (FP16) when available
   - Preserves message IDs throughout processing

3. **Question Analytics** (`question_analytics.py`)
   - Segments conversations by topic using embeddings
   - Analyzes question difficulty
   - Identifies hardest and easiest questions
   - Uses shared memory for efficient parallel processing

## Usage

### From FastAPI Backend

The pipeline is automatically called when a conversation file is uploaded through the web interface:

```python
from ml.pipeline import run_pipeline

result = run_pipeline(
    conversation_file='path/to/conversations.json',
    output_dir='path/to/output',
    enable_embeddings=False,  # Set to True to enable (requires GPU)
    enable_analytics=False     # Set to True to enable (requires embeddings)
)
```

### Standalone Usage

Each module can also be run independently:

```bash
# Compression only
python -m ml.conversation_compression input_files/user_id/user_id

# Embeddings (requires compressed file)
python -m ml.embeddings output_files/user_id/compressed_conversations.json

# Analytics (requires embedded file)
python -m ml.question_analytics output_files/user_id/embedded_conversations.json

# Full pipeline
python -m ml.pipeline input_files/user_id/user_id output_files/user_id
```

## Configuration

### Performance Settings

**Embeddings & Analytics Disabled (Default)**

- Fastest processing (~5-30 seconds)
- Only basic analytics available
- No GPU required
- Suitable for production with large user base

**Embeddings & Analytics Enabled**

- Slower processing (~5-30 minutes depending on data size)
- Full question difficulty analysis
- Requires GPU for reasonable performance
- Requires 4GB+ RAM for shared memory operations

### Enabling Advanced Features

To enable embeddings and analytics, modify `main.py`:

```python
result = run_pipeline(
    conversation_file=conversation_file_path,
    output_dir=output_file_folder,
    enable_embeddings=True,   # Enable for full analysis
    enable_analytics=True      # Enable for question difficulty
)
```

## Dependencies

Required packages (already in `requirements.txt`):

- `torch` - PyTorch for deep learning
- `transformers` - Hugging Face transformers for GTE-Large model
- `numpy` - Numerical computing

Optional:

- `faiss` - For optimized similarity search (recommended for large datasets)

## Output Files

The pipeline generates several output files in the specified output directory:

### Always Generated

- `insights/*.json` - One JSON file per page (-1 through 10) with frontend data
- `compressed_conversations.json` - Cleaned and structured conversation data
- `conversation_analytics.json` - Usage analytics and statistics
- `conversations_with_msg_id.json` - All messages with IDs, grouped by month

### Generated with Embeddings Enabled

- `embedded_conversations.json` - Conversations with embedding vectors

### Generated with Analytics Enabled

- `segmented_conversations.json` - Conversations segmented by topic
- `questions_analytics.json` - Hardest and easiest questions with metrics

## Insights Format

Each insight file contains structured data for the frontend:

```json
{
  "type": "total_hours",
  "value": 42.5,
  "total_messages": 1234,
  "total_conversations": 89
}
```

Insight types:

- `-1`: Introduction
- `0`: Total hours
- `1`: Hours by month
- `2`: Hours by time of day
- `3`: Longest conversation
- `4`: Easiest question
- `5`: Hardest question
- `6`: Profession/field (placeholder)
- `7`: Top 3 topics
- `8`: Topics per month (placeholder)
- `9`: Topics per hour (placeholder)
- `10`: Outro

## Testing

Run the integration test to verify everything is working:

```bash
python test_integration.py
```

This will:

1. Use an existing input file from `input_files/`
2. Run the pipeline
3. Verify all outputs are generated correctly
4. Display results

## Performance Notes

### Memory Usage

- Compression: ~100-500 MB
- Embeddings: ~2-4 GB (depends on model and batch size)
- Analytics: ~1-6 GB (shared memory for embeddings)

### Processing Time (approximate)

- Compression: 5-30 seconds
- Embeddings: 5-30 minutes (with GPU: ~2-5 minutes)
- Analytics: 1-5 minutes

### GPU Acceleration

The pipeline automatically detects and uses CUDA GPUs when available:

- Embeddings: 5-10x faster with GPU
- Uses FP16 precision on GPU for additional 2x speedup
- Fallback to CPU if GPU not available

## Troubleshooting

### Import Errors

Make sure you're running from the backend directory:

```bash
cd /path/to/gpt-rewind/backend
python test_integration.py
```

### Out of Memory

If you get OOM errors with embeddings/analytics enabled:

1. Reduce batch size in `embeddings.py`
2. Reduce number of workers in `question_analytics.py`
3. Disable analytics if only basic stats are needed

### Model Download

First run will download the GTE-Large model (~1.5 GB):

- Model will be cached in `~/.cache/huggingface/`
- Requires internet connection for first run
- Subsequent runs use cached model

## Architecture

```
main.py (FastAPI)
    ↓
ml/pipeline.py
    ↓
    ├─→ ml/conversation_compression.py
    │   └─→ compressed_conversations.json
    │       conversation_analytics.json
    │
    ├─→ ml/embeddings.py (optional)
    │   └─→ embedded_conversations.json
    │
    ├─→ ml/question_analytics.py (optional)
    │   └─→ segmented_conversations.json
    │       questions_analytics.json
    │
    └─→ extract_insights()
        └─→ insights/*.json
```

## Future Enhancements

Potential improvements:

- [ ] Topic modeling for profession detection
- [ ] Advanced topic tracking over time
- [ ] Sentiment analysis
- [ ] Conversation clustering
- [ ] Real-time processing with streaming
- [ ] Caching of embeddings across sessions
- [ ] Support for incremental updates

## Credits

ML components developed by team member working in the `ml/` folder.
Integration and refactoring for backend API usage.
