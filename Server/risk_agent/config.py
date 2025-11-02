"""
Configuration for Risk Agent MCP Server
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Weather API Configuration
WEATHER_API_PROVIDER = os.getenv('WEATHER_API_PROVIDER', 'openweather')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '5d83e5b696a65bb48df7954bb1cf69fd')

# Tavily API (for web search)
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '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')

# Natural Disaster/Weather Alert APIs
GDACS_ENABLED = os.getenv('GDACS_ENABLED', 'true').lower() == 'true'

# Risk Assessment Settings
RISK_ASSESSMENT_SETTINGS = {
    'check_weather': True,
    'check_natural_disasters': True,
    'check_travel_advisories': True,
}
