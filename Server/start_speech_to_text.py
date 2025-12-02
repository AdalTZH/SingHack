"""
Startup script for Speech-to-Text Server
"""
import sys
import os

# Add current directory to path so we can import speech_to_text
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Change to Server directory for proper imports
os.chdir(current_dir)

# Import and run
if __name__ == "__main__":
    from speech_to_text.server import main
    print("Starting Speech-to-Text Server...")
    print(f"Server will be available at http://localhost:8005")
    print("Loading model (this may take a while on first run)...")
    main()

