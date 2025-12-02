"""
Configuration file for the Decision Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Server configuration
SERVER_HOST = os.getenv('DECISION_AGENT_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('DECISION_AGENT_PORT', 8004))

# OpenAI configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4.1-nano')

# Decision Agent specific settings
TEMPERATURE = float(os.getenv('DECISION_TEMPERATURE', '0.3'))  # Lower temperature for more consistent decisions
MAX_TOKENS = int(os.getenv('DECISION_MAX_TOKENS', '500'))
CONFIDENCE_THRESHOLD = float(os.getenv('DECISION_CONFIDENCE_THRESHOLD', '0.7'))

# Travel-related keywords for quick filtering
TRAVEL_KEYWORDS = [
    'flight', 'hotel', 'travel', 'trip', 'vacation', 'holiday', 'booking',
    'airline', 'airport', 'destination', 'journey', 'cruise', 'tour',
    'ticket', 'reservation', 'itinerary', 'passport', 'visa', 'luggage',
    'suitcase', 'backpack', 'adventure', 'safari', 'beach', 'skiing',
    'hiking', 'traveling', 'visiting', 'departure', 'arrival', 'duty-free'
]

# Insurance-related keywords
INSURANCE_KEYWORDS = [
    'insurance', 'coverage', 'protection', 'claim', 'policy', 'premium',
    'deductible', 'benefits', 'accident', 'medical', 'emergency', 'cancel',
    'cancelation', 'trip insurance', 'travel insurance', 'medical insurance'
]

# CORS configuration
ALLOWED_ORIGINS = [
    "chrome-extension://*",
    "http://localhost:*",
    "http://127.0.0.1:*",
]

