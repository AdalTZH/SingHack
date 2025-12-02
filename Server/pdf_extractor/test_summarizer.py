"""
Quick test script to verify OpenAI API key is configured correctly
"""
import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from pdf_extractor.config import OPENAI_API_KEY, OPENAI_MODEL

print("=" * 60)
print("PDF Summarizer Configuration Test")
print("=" * 60)

if OPENAI_API_KEY:
    print(f"✓ OPENAI_API_KEY: Found (length: {len(OPENAI_API_KEY)} characters)")
    print(f"✓ Model: {OPENAI_MODEL}")
    print("\nConfiguration looks good! Summarization should work.")
    
    # Try to initialize summarizer
    try:
        from pdf_extractor.summarizer import PDFSummarizer
        summarizer = PDFSummarizer(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)
        print("✓ Summarizer initialized successfully!")
        
        # Test with a simple text
        test_text = "This is a test document. It contains multiple sentences. We want to see if summarization works."
        print("\nTesting summarization with sample text...")
        result = summarizer.summarize(test_text, detail_level="brief")
        
        if result["success"]:
            print("✓ Summarization test successful!")
            print(f"  Summary: {result['summary'][:100]}...")
        else:
            print(f"✗ Summarization test failed: {result.get('error')}")
            
    except Exception as e:
        print(f"✗ Failed to initialize summarizer: {e}")
        print("\nPlease check:")
        print("  1. OpenAI API key is valid")
        print("  2. 'openai' package is installed: pip install openai")
        print("  3. You have API credits/quota")
else:
    print("✗ OPENAI_API_KEY: Not found")
    print("\nPlease ensure:")
    print("  1. .env file exists in Server/ directory")
    print("  2. OPENAI_API_KEY is set in .env file")
    print("  3. File is named exactly '.env' (not 'env' or '.env.txt')")

print("=" * 60)


