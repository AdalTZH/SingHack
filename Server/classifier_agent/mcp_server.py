"""
Classifier Agent MCP Server
Exposes tools for query classification via Model Context Protocol

Tools provided:
- classify_insurance_query: Classify a user query into one of four types
- get_classification_details: Get detailed classification with next steps
- classify_batch: Classify multiple queries at once
"""
import sys
from typing import Dict, List, Optional, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import FastMCP
try:
    from fastmcp import FastMCP
    FASTMCP_AVAILABLE = True
except ImportError:
    logger.error("FastMCP not available. Install with: pip install fastmcp")
    FASTMCP_AVAILABLE = False
    FastMCP = None

# Import classifier agent components
from .api import ClassifierAgentAPI, classify_query_detailed, classify_batch
from .classifier_agent import ClassifierAgent

# Create MCP server instance
if FASTMCP_AVAILABLE:
    mcp_server = FastMCP(name="ClassifierAgentServer")
else:
    mcp_server = None


# ============================================================================
# IMPLEMENTATION FUNCTIONS
# ============================================================================

def _classify_insurance_query_impl(query: str, include_reasoning: Optional[bool] = True) -> Dict:
    """Implementation for classifying an insurance query"""
    try:
        api = ClassifierAgentAPI()
        result = api.get_classification_details(api.classify(query, detailed=True))
        
        return {
            'success': True,
            'query': query,
            'classification': result['classification'],
            'confidence': result['confidence'],
            'reasoning': result['reasoning'] if include_reasoning else None,
            'type_name': result['type_details']['name'],
            'description': result['type_details']['description'],
            'next_steps': result['type_details']['next_steps'],
            'entities': result['entities']
        }
    
    except Exception as e:
        logger.error(f"Error classifying query: {e}")
        return {
            'success': False,
            'error': str(e),
            'classification': 'explanation',
            'confidence': 0.0
        }


def _get_classification_details_impl(result: Dict) -> Dict:
    """Implementation for getting detailed classification information"""
    try:
        api = ClassifierAgentAPI()
        details = api.get_classification_details(result)
        
        return {
            'success': True,
            **details
        }
    
    except Exception as e:
        logger.error(f"Error getting classification details: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def _classify_batch_impl(queries: List[str]) -> Dict:
    """Implementation for batch classification"""
    try:
        results = classify_batch(queries)
        
        return {
            'success': True,
            'total_queries': len(queries),
            'results': results,
            'summary': _generate_batch_summary(results)
        }
    
    except Exception as e:
        logger.error(f"Error in batch classification: {e}")
        return {
            'success': False,
            'error': str(e),
            'results': []
        }


def _generate_batch_summary(results: List[Dict]) -> Dict:
    """Generate summary statistics for batch classification"""
    if not results:
        return {}
    
    classification_counts = {}
    total_confidence = 0.0
    valid_results = 0
    
    for result in results:
        classification = result.get('classification', 'unknown')
        classification_counts[classification] = classification_counts.get(classification, 0) + 1
        
        confidence = result.get('confidence', 0.0)
        if isinstance(confidence, (int, float)):
            total_confidence += confidence
            valid_results += 1
    
    avg_confidence = total_confidence / valid_results if valid_results > 0 else 0.0
    
    return {
        'classification_distribution': classification_counts,
        'average_confidence': round(avg_confidence, 3),
        'total_classified': valid_results
    }


# ============================================================================
# REGISTER MCP TOOLS
# ============================================================================

if mcp_server:
    @mcp_server.tool(
        name="classify_insurance_query",
        description="Classify a user's insurance query into one of four types: Comparison, Explanation, Eligibility, or Scenario Analysis. Returns classification type, confidence score, reasoning, and recommended next steps for processing the query."
    )
    def classify_insurance_query(
        query: str,
        include_reasoning: Optional[bool] = True
    ) -> Dict:
        """Classify an insurance query"""
        return _classify_insurance_query_impl(query, include_reasoning)
    
    @mcp_server.tool(
        name="get_classification_details",
        description="Get detailed information about a classification result, including type description, next steps, and entity extraction. Use this to understand how to process a classified query."
    )
    def get_classification_details(
        classification_result: Dict
    ) -> Dict:
        """Get classification details"""
        return _get_classification_details_impl(classification_result)
    
    @mcp_server.tool(
        name="classify_batch_queries",
        description="Classify multiple insurance queries in batch. Returns individual classifications plus summary statistics including distribution of query types and average confidence."
    )
    def classify_batch_queries(
        queries: List[str]
    ) -> Dict:
        """Classify multiple queries"""
        return _classify_batch_impl(queries)
    
    logger.info("MCP server tools registered successfully")
else:
    logger.warning("MCP server not available - tools cannot be registered")


# ============================================================================
# SERVER ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    if mcp_server:
        # Run the MCP server
        try:
            mcp_server.run()
        except Exception as e:
            logger.error(f"Error running MCP server: {e}")
            sys.exit(1)
    else:
        print("Error: FastMCP not available. Install with: pip install fastmcp")
        sys.exit(1)

