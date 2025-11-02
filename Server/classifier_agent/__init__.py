"""
Classifier Agent Package
Classifies user queries into Comparison, Explanation, Eligibility, or Scenario Analysis
"""

from .api import ClassifierAgentAPI, classify_query, classify_query_detailed
from .classifier_agent import ClassifierAgent

try:
    from .mcp_server import mcp_server
    __all__ = [
        'ClassifierAgentAPI',
        'classify_query',
        'classify_query_detailed',
        'ClassifierAgent',
        'mcp_server'
    ]
except ImportError:
    __all__ = [
        'ClassifierAgentAPI',
        'classify_query',
        'classify_query_detailed',
        'ClassifierAgent'
    ]


