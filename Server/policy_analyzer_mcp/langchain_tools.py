"""
LangChain Tools for Policy Analyzer MCP
Wraps MCP client calls as LangChain tools for use with the master agent
"""
import httpx
from typing import Optional, Dict, Any, List
from langchain_core.tools import tool
import logging

from .config import POLICY_ANALYZER_API_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Direct API client (simpler than MCP for LangChain integration)
def _api_call(method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
    """Make API call to Policy Analyzer (synchronous for LangChain compatibility)"""
    url = f"{POLICY_ANALYZER_API_URL}{endpoint}"
    with httpx.Client(timeout=30.0) as client:
        if method == "GET":
            response = client.get(url)
        elif method == "POST":
            response = client.post(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()


@tool
def scan_policy_eligibility(product: str, user_data: Dict[str, Any]) -> str:
    """
    Scan policy eligibility for a given product and user data.
    
    Args:
        product: Product name ('Scootsurance', 'TravelEasy', or 'TravelEasy Pre-Ex')
        user_data: Dictionary with user data fields:
            - departure_location (required): string
            - return_location (optional, required for TravelEasy): string
            - age (required): number
            - trip_type (optional): 'single' or 'annual'
            - purchase_timing (required): string
    
    Returns:
        JSON string with eligibility results
    """
    try:
        result = _api_call("POST", "/scan_policy_eligibility", {
            "product": product,
            "user_data": user_data
        })
        return f"Eligibility Scan Results:\nProduct: {result.get('product')}\nEligible: {result.get('eligible')}\nConditions Checked: {len(result.get('conditions_checked', []))}\nConditions Skipped: {len(result.get('conditions_skipped', []))}\n\nDetails: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def show_policy_benefits(product: Optional[str] = None) -> str:
    """
    Get list of benefits for a specific product or all products.
    
    Args:
        product: Optional product name. If not provided, returns benefits for all products.
    
    Returns:
        JSON string with benefits list
    """
    try:
        if product:
            result = _api_call("GET", f"/show_policy_benefits/{product}")
        else:
            result = _api_call("GET", "/show_policy_benefits")
        return f"Policy Benefits:\n{result}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def show_policy_benefit_details(product: str, benefit_name: str) -> str:
    """
    Get detailed information for a specific policy benefit including layer 2 details and layer 3 eligibility/exclusion conditions.
    
    Args:
        product: Product name ('Scootsurance', 'TravelEasy', or 'TravelEasy Pre-Ex')
        benefit_name: Benefit name (must match exactly with layer_2_benefits benefit_name)
    
    Returns:
        JSON string with benefit details
    """
    try:
        result = _api_call("POST", "/show_policy_benefit_details", {
            "product": product,
            "benefit_name": benefit_name
        })
        return f"Benefit Details for {result.get('product')} - {result.get('benefit_name')}:\nLayer 2: {result.get('layer_2_details')}\nLayer 3 Eligibility: {len(result.get('layer_3_eligibility', []))} conditions\nLayer 3 Exclusion: {len(result.get('layer_3_exclusion', []))} conditions\n\nFull Details: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def show_policy_exclusion(product: str) -> str:
    """
    Get list of exclusions in layer 1 for a specific policy.
    
    Args:
        product: Product name ('Scootsurance', 'TravelEasy', or 'TravelEasy Pre-Ex')
    
    Returns:
        JSON string with exclusions list
    """
    try:
        result = _api_call("GET", f"/show_policy_exclusion/{product}")
        return f"Exclusions for {result.get('product')}:\nTotal: {result.get('total_count')}\n\nExclusions: {result.get('exclusions')}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def show_policy_exclusion_details(product: str, condition: str) -> str:
    """
    Get detailed information for a specific exclusion condition from layer 1.
    
    Args:
        product: Product name ('Scootsurance', 'TravelEasy', or 'TravelEasy Pre-Ex')
        condition: Exclusion condition name (e.g., 'pre_existing_conditions', 'travel_advisory_exclusion')
    
    Returns:
        JSON string with exclusion details
    """
    try:
        result = _api_call("POST", "/show_policy_exclusion_details", {
            "product": product,
            "condition": condition
        })
        return f"Exclusion Details for {result.get('product')} - {result.get('condition')}:\n{result.get('exclusion_details')}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def grade_policy(prioritized_benefits: List[Any]) -> str:
    """
    Grade all policies based on prioritized benefits using a point system.
    Returns scores and rankings to determine which policy is best for the client's scenario.
    
    Args:
        prioritized_benefits: List of prioritized benefits. Can be:
            - Simple strings (order = priority)
            - Objects with 'benefit_name', optional 'priority', and optional 'priority_score'
    
    Returns:
        JSON string with policy scores and rankings
    """
    try:
        result = _api_call("POST", "/grade_policy", {
            "prioritized_benefits": prioritized_benefits
        })
        rankings = result.get('rankings', [])
        scores = result.get('policy_scores', {})
        percentages = result.get('percentage_scores', {})
        
        ranking_text = "Policy Rankings:\n"
        for i, policy in enumerate(rankings, 1):
            score = scores.get(policy, 0)
            percentage = percentages.get(policy, 0)
            ranking_text += f"{i}. {policy}: {score:.1f} points ({percentage:.1f}%)\n"
        
        return f"{ranking_text}\n\nDetailed Scores: {result.get('detailed_scores')}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def get_products() -> str:
    """
    Get list of available products from the taxonomy.
    
    Returns:
        Comma-separated list of product names
    """
    try:
        result = _api_call("GET", "/products")
        # Handle both list and other types
        if isinstance(result, list):
            # Ensure all items are strings
            products = [str(item) for item in result]
            return f"Available Products: {', '.join(products)}"
        else:
            return f"Available Products: {str(result)}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def get_eligibility_conditions() -> str:
    """
    Get list of eligibility conditions from layer_1_general_conditions.
    
    Returns:
        JSON string with eligibility conditions
    """
    try:
        result = _api_call("GET", "/eligibility_conditions")
        return f"Eligibility Conditions: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


def get_policy_analyzer_tools():
    """
    Get all policy analyzer tools as a list for LangChain binding
    
    Returns:
        List of LangChain tools
    """
    return [
        scan_policy_eligibility,
        show_policy_benefits,
        show_policy_benefit_details,
        show_policy_exclusion,
        show_policy_exclusion_details,
        grade_policy,
        get_products,
        get_eligibility_conditions
    ]

