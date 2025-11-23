#!/usr/bin/env python3
"""
Test script for ML pipeline integration

This script tests the ML pipeline with sample data to ensure everything is working.
"""

import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_pipeline():
    """Test the ML pipeline with a sample conversation file."""
    
    # Check if we have any input files to test with
    input_folders = os.listdir('input_files')
    
    if not input_folders:
        print("No input files found to test with.")
        print("To test the pipeline:")
        print("1. Upload a conversation file through the web interface")
        print("2. Or place a conversations.json file in input_files/test/")
        return False
    
    # Use the first available input file
    test_folder = input_folders[0]
    test_file = os.path.join('input_files', test_folder, test_folder)
    
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return False
    
    print(f"Testing with file: {test_file}")
    
    # Import the pipeline
    try:
        from ml.pipeline import run_pipeline
    except ImportError as e:
        print(f"Failed to import pipeline: {e}")
        return False
    
    # Create test output directory
    output_dir = 'test_output'
    os.makedirs(output_dir, exist_ok=True)
    
    # Run the pipeline
    print("\nRunning pipeline (without embeddings/analytics for speed)...")
    try:
        result = run_pipeline(
            conversation_file=test_file,
            output_dir=output_dir,
            enable_embeddings=False,
            enable_analytics=False
        )
    except Exception as e:
        print(f"Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Check results
    if not result['success']:
        print(f"Pipeline failed: {result['error']}")
        return False
    
    print("\n✓ Pipeline completed successfully!")
    
    # Verify outputs
    print("\nVerifying outputs...")
    
    # Check insights files
    insights_dir = os.path.join(output_dir, 'insights')
    if not os.path.exists(insights_dir):
        print("✗ Insights directory not created")
        return False
    
    print("✓ Insights directory created")
    
    # Check that all insight files were created
    missing_files = []
    for page_index in range(-1, 11):
        insight_file = os.path.join(insights_dir, f"{page_index}.json")
        if not os.path.exists(insight_file):
            missing_files.append(page_index)
        else:
            # Verify it's valid JSON
            try:
                with open(insight_file, 'r') as f:
                    data = json.load(f)
                print(f"✓ Page {page_index}: {data.get('type', 'unknown')}")
            except json.JSONDecodeError:
                print(f"✗ Page {page_index}: Invalid JSON")
                return False
    
    if missing_files:
        print(f"✗ Missing insight files for pages: {missing_files}")
        return False
    
    print("\n✓ All insight files created successfully!")
    
    # Check analytics files
    if result['compression_result']:
        analytics_file = result['compression_result']['analytics_file']
        if os.path.exists(analytics_file):
            print(f"✓ Analytics file created: {analytics_file}")
        else:
            print(f"✗ Analytics file missing: {analytics_file}")
    
    print("\n" + "=" * 60)
    print("TEST PASSED!")
    print("=" * 60)
    print(f"\nTest output directory: {output_dir}")
    print("You can inspect the generated files there.")
    
    return True


if __name__ == '__main__':
    success = test_pipeline()
    sys.exit(0 if success else 1)
