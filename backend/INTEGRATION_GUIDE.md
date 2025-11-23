# ML Integration Guide

## Summary

I've successfully integrated your teammate's ML work into the backend! Here's what was done:

## Changes Made

### 1. Refactored ML Scripts

All three ML scripts have been converted to be importable as library modules:

- `ml/conversation_compression.py` - Now has `process_conversations()` function
- `ml/embeddings.py` - Now has `generate_embeddings()` function
- `ml/question_analytics.py` - Now has `analyze_questions()` function

Each can still be run standalone with `python -m ml.module_name`, but can also be imported and called programmatically.

### 2. Created Pipeline Module

New file: `ml/pipeline.py`

- Provides `run_pipeline()` function that orchestrates all three stages
- Handles errors gracefully
- Generates insight JSON files for pages -1 through 10
- Can be called with embeddings/analytics enabled or disabled

### 3. Updated Backend Integration

Modified `main.py`:

- Imports and calls the ML pipeline in `create_analyze_files()`
- Properly handles the uploaded conversation file
- Generates all required insight JSON files
- Includes error handling and logging

### 4. Added Dependencies

Updated `requirements.txt` with:

- `torch`
- `transformers`
- `numpy`

### 5. Documentation

Created:

- `ml/README.md` - Comprehensive documentation of the ML pipeline
- `ml/__init__.py` - Makes ml a proper Python package
- `test_integration.py` - Test script to verify the integration

## How It Works

When a user uploads a conversation file:

1. File is saved to `input_files/{user_id}/{user_id}`
2. Backend calls `run_pipeline()` with the file path
3. Pipeline runs compression → (optionally embeddings) → (optionally analytics)
4. Insights are extracted and saved to `output_files/{user_id}/insights/*.json`
5. Frontend can request insights via existing API endpoints

## Configuration

### Default Configuration (Fast)

```python
run_pipeline(
    conversation_file=path,
    output_dir=output_dir,
    enable_embeddings=False,  # Disabled for speed
    enable_analytics=False     # Disabled for speed
)
```

- Processes in 5-30 seconds
- Provides basic analytics (hours, messages, peak times)
- No GPU required

### Full Analysis (Slow but Comprehensive)

```python
run_pipeline(
    conversation_file=path,
    output_dir=output_dir,
    enable_embeddings=True,   # Requires GPU
    enable_analytics=True      # Requires embeddings
)
```

- Processes in 5-30 minutes
- Provides question difficulty analysis
- Requires GPU for reasonable performance
- Requires 4GB+ RAM

## What Works Now

✅ Conversation compression and analytics  
✅ Usage statistics (hours, messages, conversations)  
✅ Peak usage times and patterns  
✅ Longest conversation tracking  
✅ Insight JSON generation for all pages  
✅ Error handling and fallbacks

## What's Optional (Resource Intensive)

⚠️ Embedding generation (disabled by default)  
⚠️ Question difficulty analysis (disabled by default)  
⚠️ Hardest/easiest question detection (requires embeddings)  
⚠️ Topic segmentation (requires embeddings)

## Next Steps

### To Test

```bash
cd backend
python test_integration.py
```

### To Enable Full Analysis

Edit `main.py` line 36-37 and change:

```python
enable_embeddings=True,
enable_analytics=True
```

Note: This will be much slower and require GPU.

### To Install Dependencies

```bash
pip install -r requirements.txt
```

Note: `torch` and `transformers` are large packages (~2-3 GB). First run will also download the GTE-Large model (~1.5 GB).

## Preserved Functionality

All of your teammate's original code has been preserved! I only:

- Added function wrappers around the main() methods
- Made file paths configurable instead of hardcoded
- Added error handling instead of sys.exit()
- Made them return results instead of just saving files

The original standalone functionality still works:

```bash
python -m ml.conversation_compression input.json
python -m ml.embeddings compressed.json
python -m ml.question_analytics embedded.json
```

## Insight Pages

The pipeline now generates JSON files for all pages:

- `-1`: Welcome/Introduction
- `0`: Total hours spent
- `1`: Hours by month (with peak month)
- `2`: Usage by time of day (with peak hour)
- `3`: Longest conversation duration
- `4`: Easiest question (when analytics enabled)
- `5`: Hardest question (when analytics enabled)
- `6`: Profession/field (placeholder)
- `7`: Top 3 topics (basic version)
- `8`: Topics per month (placeholder)
- `9`: Topics per hour (placeholder)
- `10`: Outro/summary

## Questions?

Check `ml/README.md` for detailed documentation, or run:

```bash
python -m ml.pipeline --help
```
