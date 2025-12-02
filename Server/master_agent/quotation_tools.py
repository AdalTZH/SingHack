"""
LangChain Tools for Quotation API
Wraps quotation API calls as LangChain tools for use with the master agent
"""
import httpx
from typing import Optional
from langchain_core.tools import tool
import logging

from .config import QUOTATION_API_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Direct API client (synchronous for LangChain compatibility)
def _api_call(method: str, endpoint: str, data: Optional[dict] = None) -> dict:
    """Make API call to Quotation API"""
    url = f"{QUOTATION_API_URL}{endpoint}"
    try:
        with httpx.Client(timeout=30.0) as client:
            if method == "GET":
                response = client.get(url)
            elif method == "POST":
                response = client.post(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error calling quotation API: {e}")
        raise
    except Exception as e:
        logger.error(f"Error calling quotation API: {e}")
        raise


@tool
def get_insurance_quotation(
    policy_type: str,
    age: int,
    days: int,
    continent: str
) -> str:
    """
    Get insurance policy quotation with three coverage tiers (Basic, Standard, Premium).
    
    This tool generates a quotation for travel insurance policies including:
    - Scootsurance: Standard travel insurance
    - TravelEasy: Enhanced travel insurance
    - TravelEasy Pre-Ex: Travel insurance with pre-existing conditions coverage
    
    Each quotation includes three tiers with different coverage levels and premiums.
    
    Args:
        policy_type: Policy type - must be one of: 'Scootsurance', 'TravelEasy', or 'TravelEasy Pre-Ex'
        age: Age of the insured person (0-100)
        days: Number of days travelling (minimum 1)
        continent: Destination continent - must be one of: 'Asia', 'Europe', 'North America', 'South America', 'Africa', 'Oceania', or 'Antarctica'
    
    Returns:
        Formatted string with quotation details including all three tiers with premiums and coverage features
    """
    try:
        result = _api_call("POST", "/quote", {
            "policy_type": policy_type,
            "age": age,
            "days": days,
            "continent": continent
        })
        
        if not result.get("success"):
            return f"Error: Quotation request failed"
        
        # Format the response nicely
        quotation_text = f"Insurance Quotation for {result.get('policy_type')}\n"
        quotation_text += f"Age: {result.get('age')} | Days: {result.get('days')} | Continent: {result.get('continent')}\n"
        quotation_text += f"Calculation Date: {result.get('calculation_date')}\n\n"
        quotation_text += "=" * 60 + "\n"
        
        tiers = result.get('tiers', [])
        for tier in tiers:
            quotation_text += f"\n{tier.get('tier')} Tier\n"
            quotation_text += f"Premium: {tier.get('currency')} ${tier.get('premium'):.2f}\n"
            quotation_text += f"Description: {tier.get('description')}\n"
            quotation_text += "Coverage Features:\n"
            for feature in tier.get('coverage_features', []):
                quotation_text += f"  • {feature}\n"
            quotation_text += "-" * 60 + "\n"
        
        return quotation_text
    except Exception as e:
        logger.error(f"Error getting quotation: {e}")
        return f"Error getting quotation: {str(e)}"


@tool
def get_supported_policies() -> str:
    """
    Get list of supported insurance policy types for quotation.
    
    Returns:
        Comma-separated list of available policy types
    """
    try:
        result = _api_call("GET", "/policies")
        if isinstance(result, list):
            policies = [str(item) for item in result]
            return f"Supported Policy Types: {', '.join(policies)}"
        else:
            return f"Supported Policy Types: {str(result)}"
    except Exception as e:
        logger.error(f"Error getting supported policies: {e}")
        return f"Error: {str(e)}"


@tool
def get_supported_continents() -> str:
    """
    Get list of supported continents for travel insurance quotations.
    
    Returns:
        Comma-separated list of available continents
    """
    try:
        result = _api_call("GET", "/continents")
        if isinstance(result, list):
            continents = [str(item) for item in result]
            return f"Supported Continents: {', '.join(continents)}"
        else:
            return f"Supported Continents: {str(result)}"
    except Exception as e:
        logger.error(f"Error getting supported continents: {e}")
        return f"Error: {str(e)}"


def get_quotation_tools():
    """
    Get all quotation tools as a list for LangChain binding
    
    Returns:
        List of LangChain tools
    """
    return [
        get_insurance_quotation,
        get_supported_policies,
        get_supported_continents
    ]

