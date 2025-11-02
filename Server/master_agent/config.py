"""
Configuration file for the Master Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Server configuration
SERVER_HOST = os.getenv('MASTER_AGENT_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('MASTER_AGENT_PORT', 9000))

# OpenAI configuration (for master agent LLM orchestration)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

# Agent service URLs (for A2A communication)
# These are the endpoints for communicating with each specialized agent
AGENT_URLS = {
    'classifier': os.getenv('CLASSIFIER_AGENT_URL', 'http://localhost:8001'),
    'predict': os.getenv('PREDICT_AGENT_URL', 'http://localhost:8002'),
    'risk': os.getenv('RISK_AGENT_URL', 'http://localhost:8003'),
}

# Master Agent specific settings
TEMPERATURE = float(os.getenv('MASTER_TEMPERATURE', '0.7'))
MAX_TOKENS = int(os.getenv('MAX_TOKENS', '2000'))

# CORS configuration
ALLOWED_ORIGINS = [
    "chrome-extension://*",
    "http://localhost:*",
    "http://127.0.0.1:*",
]

