"""
Configuration file for Policy Analyzer MCP Server
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Policy Analyzer API configuration
POLICY_ANALYZER_API_URL = os.getenv(
    'POLICY_ANALYZER_API_URL',
    'http://localhost:8006'
)

# MCP Server configuration
MCP_SERVER_NAME = "policy-analyzer-mcp"
MCP_SERVER_VERSION = "1.0.0"


