"""
Configuration for Speech-to-Text Server
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Server configuration
SERVER_HOST = os.getenv("SPEECH_TO_TEXT_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SPEECH_TO_TEXT_PORT", "8005"))

# CORS configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "chrome-extension://*",
    "*"  # Allow all origins for extension compatibility
]

# Model configuration (matching testing.py)
REPO_ID = "MERaLiON/MERaLiON-2-3B"
DEVICE = "cuda"  # Change to "cpu" if no GPU available
SAMPLE_RATE = 16000



