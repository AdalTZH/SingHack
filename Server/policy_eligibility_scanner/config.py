"""
Configuration file for the Policy Eligibility Scanner
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Server configuration
SERVER_HOST = os.getenv('POLICY_ELIGIBILITY_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('POLICY_ELIGIBILITY_PORT', 8006))

# Taxonomy file path
TAXONOMY_FILE_PATH = os.getenv(
    'TAXONOMY_FILE_PATH',
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Taxonomy_Hackathon.json')
)

# CORS configuration
ALLOWED_ORIGINS = [
    "chrome-extension://*",
    "http://localhost:*",
    "http://127.0.0.1:*",
]


