"""
Configuration file for database connection and application settings
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'hackathon-db.ceqjfmi6jhdd.ap-southeast-1.rds.amazonaws.com'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'hackathon_db'),
    'user': os.getenv('DB_USER', 'hackathon_user'),
    'password': os.getenv('DB_PASSWORD', 'Hackathon2025!'),
    'schema': 'hackathon'
}

# OpenAI configuration (if needed for AI-enhanced predictions)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Scoring Weights Configuration
# These weights determine the importance of each factor in the composite score calculation
# Values should sum to 1.0 for proper normalization
SCORING_WEIGHTS = {
    'destination_match': float(os.getenv('WEIGHT_DESTINATION_MATCH', 0.30)),      # 30% - Most important: products proven in user's destination
    'claim_type_match': float(os.getenv('WEIGHT_CLAIM_TYPE_MATCH', 0.25)),        # 25% - Important: matches user's coverage priorities
    'claim_frequency': float(os.getenv('WEIGHT_CLAIM_FREQUENCY', 0.15)),          # 15% - Moderate: indicates trusted/used products
    'claim_severity': float(os.getenv('WEIGHT_CLAIM_SEVERITY', 0.15)),            # 15% - Moderate: lower severity = better for users
    'processing_efficiency': float(os.getenv('WEIGHT_PROCESSING_EFFICIENCY', 0.15))  # 15% - Moderate: faster processing = better UX
}

# Validate weights sum to approximately 1.0
_weight_sum = sum(SCORING_WEIGHTS.values())
if abs(_weight_sum - 1.0) > 0.01:
    import warnings
    warnings.warn(f"Scoring weights sum to {_weight_sum}, not 1.0. This may affect score normalization.")

