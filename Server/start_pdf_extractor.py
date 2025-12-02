"""
Startup script for PDF Text Extraction Server
"""
import sys
import os

# Add current directory to path so we can import pdf_extractor
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Change to Server directory for proper imports
os.chdir(current_dir)

# Import and run
if __name__ == "__main__":
    from pdf_extractor.server import main
    print("Starting PDF Text Extraction Server...")
    print(f"Server will be available at http://localhost:8007")
    print("Ready to extract text from PDF documents!")
    main()

