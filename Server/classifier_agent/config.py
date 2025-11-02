"""
Configuration file for the Classifier Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

# Path to taxonomy JSON file
TAXONOMY_JSON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'Taxonomy_Hackathon.json'
)

# Query classification types
CLASSIFICATION_TYPES = [
    'comparison',
    'explanation',
    'eligibility',
    'scenario_analysis'
]

# Product name mappings
PRODUCT_NAMES = {
    'Product A': 'Scootsurance',
    'Product B': 'TravelEasy Policy',
    'Product C': 'TravelEasy Pre-Ex Policy'
}

# Classification keywords and patterns
CLASSIFICATION_KEYWORDS = {
    'comparison': [
        'which', 'better', 'best', 'compare', 'comparison', 'difference', 
        'different', 'vs', 'versus', 'advantage', 'disadvantage',
        'which plan', 'better coverage', 'which product'
    ],
    'explanation': [
        'what', 'what is', 'explain', 'how', 'how does', 'describe',
        'tell me about', 'meaning', 'definition', 'covered',
        'what does', 'what are', 'details', 'information'
    ],
    'eligibility': [
        'am i covered', 'eligible', 'can i', 'qualified', 'pre-existing',
        'covered for', 'apply', 'claim', 'receive', 'age limit',
        'conditions', 'requirements', 'qualify', 'am i able to'
    ],
    'scenario_analysis': [
        'what happens if', 'what if', 'in case of', 'scenario',
        'if i', 'when', 'what would happen', 'outcome', 'result',
        'break my leg', 'skiing', 'get sick', 'injury', 'emergency'
    ]
}

# Confidence threshold for classification
CONFIDENCE_THRESHOLD = 0.7

# Maximum tokens for LLM responses
MAX_TOKENS = 2000


