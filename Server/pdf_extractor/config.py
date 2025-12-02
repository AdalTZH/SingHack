"""
Configuration for PDF Text Extraction Server
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Server configuration
SERVER_HOST = os.getenv("PDF_EXTRACTOR_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("PDF_EXTRACTOR_PORT", "8007"))

# CORS configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "chrome-extension://*",
    "*"  # Allow all origins for extension compatibility
]

# File upload configuration
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB max file size
ALLOWED_FILE_TYPES = ["application/pdf"]

# PDF processing configuration
EXTRACT_IMAGES = False  # Set to True if you want to extract images from PDFs in future
OCR_ENABLED = False  # Set to True if you want OCR for scanned PDFs in future

# OpenAI configuration for summarization
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("PDF_SUMMARIZER_MODEL", "gpt-4o-mini")  # Model for PDF summarization
SUMMARIZE_BY_DEFAULT = os.getenv("PDF_SUMMARIZE_BY_DEFAULT", "false").lower() == "true"  # Auto-summarize on extraction

