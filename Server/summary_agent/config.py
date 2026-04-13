"""
Configuration file for the Summary Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Server configuration
SERVER_HOST = os.getenv('SUMMARY_AGENT_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('SUMMARY_AGENT_PORT', 8020))

# OpenAI configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

# Summary Agent specific settings
TEMPERATURE = float(os.getenv('SUMMARY_TEMPERATURE', '0.3'))
MAX_TOKENS = int(os.getenv('SUMMARY_MAX_TOKENS', '300'))

# CORS configuration
ALLOWED_ORIGINS = [
    "chrome-extension://*",
    "http://localhost:*",
    "http://127.0.0.1:*",
]

