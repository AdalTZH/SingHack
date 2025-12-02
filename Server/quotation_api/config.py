"""
Configuration file for the Quotation API Server
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Server configuration
SERVER_HOST = os.getenv('QUOTATION_API_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('QUOTATION_API_PORT', 8009))

# CORS configuration
ALLOWED_ORIGINS = [
    "chrome-extension://*",
    "http://localhost:*",
    "http://127.0.0.1:*",
]

