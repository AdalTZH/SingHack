"""
MCP Server for Policy Analyzer
Provides MCP tools that call the Policy Analyzer API endpoints
"""
import asyncio
import httpx
import logging
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .config import POLICY_ANALYZER_API_URL, MCP_SERVER_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
server = Server(MCP_SERVER_NAME)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available tools for policy analysis
    """
    return [
        Tool(
            name="scan_policy_eligibility",
            description="Scan policy eligibility for a given product and user data. Checks eligibility conditions from layer 1.",
            inputSchema={
                "type": "object",
                "properties": {
                    "product": {
                        "type": "string",
                        "description": "Product name: 'Scootsurance', 'TravelEasy', or 'TravelEasy Pre-Ex'"
                    },
                    "user_data": {
                        "type": "object",
                        "description": "User-provided data fields",
                        "properties": {
                            "departure_location": {"type": "string"},
                            "return_location": {"type": "string"},
                            "age": {"type": "number"},
                            "trip_type": {"type": "string", "enum": ["single", "annual"]},
                            "purchase_timing": {"type": "string"}
                        },
                        "required": ["departure_location", "age", "purchase_timing"]
                    }
                },
                "required": ["product", "user_data"]
            }
        ),
        Tool(
            name="show_policy_benefits",
            description="Get list of benefits for a specific product or all products from layer 2.",
            inputSchema={
                "type": "object",
                "properties": {
                    "product": {
                        "type": "string",
                        "description": "Optional product name. If not provided, returns benefits for all products."
                    }
                }
            }
        ),
        Tool(
            name="show_policy_benefit_details",
            description="Get detailed information for a specific policy benefit including layer 2 details and layer 3 eligibility/exclusion conditions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "product": {
                        "type": "string",
                        "description": "Product name: 'Scootsurance', 'TravelEasy', or 'TravelEasy Pre-Ex'"
                    },
                    "benefit_name": {
                        "type": "string",
                        "description": "Benefit name (must match exactly with layer_2_benefits benefit_name)"
                    }
                },
                "required": ["product", "benefit_name"]
            }
        ),
        Tool(
            name="show_policy_exclusion",
            description="Get list of exclusions in layer 1 for a specific policy.",
            inputSchema={
                "type": "object",
                "properties": {
                    "product": {
                        "type": "string",
                        "description": "Product name: 'Scootsurance', 'TravelEasy', or 'TravelEasy Pre-Ex'"
                    }
                },
                "required": ["product"]
            }
        ),
        Tool(
            name="show_policy_exclusion_details",
            description="Get detailed information for a specific exclusion condition from layer 1.",
            inputSchema={
                "type": "object",
                "properties": {
                    "product": {
                        "type": "string",
                        "description": "Product name: 'Scootsurance', 'TravelEasy', or 'TravelEasy Pre-Ex'"
                    },
                    "condition": {
                        "type": "string",
                        "description": "Exclusion condition name (e.g., 'pre_existing_conditions', 'travel_advisory_exclusion')"
                    }
                },
                "required": ["product", "condition"]
            }
        ),
        Tool(
            name="grade_policy",
            description="Grade all policies based on prioritized benefits using a point system. Returns scores and rankings to determine which policy is best for the client's scenario.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prioritized_benefits": {
                        "type": "array",
                        "description": "List of prioritized benefits. Can be simple strings (order = priority) or objects with benefit_name, priority, and optional priority_score.",
                        "items": {
                            "oneOf": [
                                {"type": "string"},
                                {
                                    "type": "object",
                                    "properties": {
                                        "benefit_name": {"type": "string"},
                                        "priority": {"type": "integer"},
                                        "priority_score": {"type": "number", "minimum": 0, "maximum": 100}
                                    },
                                    "required": ["benefit_name"]
                                }
                            ]
                        }
                    }
                },
                "required": ["prioritized_benefits"]
            }
        ),
        Tool(
            name="get_products",
            description="Get list of available products from the taxonomy.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_eligibility_conditions",
            description="Get list of eligibility conditions from layer_1_general_conditions.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    """
    Handle tool calls by making API requests to Policy Analyzer
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            if name == "scan_policy_eligibility":
                response = await client.post(
                    f"{POLICY_ANALYZER_API_URL}/scan_policy_eligibility",
                    json=arguments
                )
                response.raise_for_status()
                result = response.json()
                return [TextContent(
                    type="text",
                    text=f"Eligibility Scan Results:\nProduct: {result.get('product')}\nEligible: {result.get('eligible')}\nConditions Checked: {len(result.get('conditions_checked', []))}\nConditions Skipped: {len(result.get('conditions_skipped', []))}\n\nFull Response: {result}"
                )]
            
            elif name == "show_policy_benefits":
                product = arguments.get("product")
                if product:
                    url = f"{POLICY_ANALYZER_API_URL}/show_policy_benefits/{product}"
                    response = await client.get(url)
                else:
                    response = await client.get(f"{POLICY_ANALYZER_API_URL}/show_policy_benefits")
                response.raise_for_status()
                result = response.json()
                return [TextContent(
                    type="text",
                    text=f"Policy Benefits:\n{result}"
                )]
            
            elif name == "show_policy_benefit_details":
                response = await client.post(
                    f"{POLICY_ANALYZER_API_URL}/show_policy_benefit_details",
                    json=arguments
                )
                response.raise_for_status()
                result = response.json()
                return [TextContent(
                    type="text",
                    text=f"Benefit Details for {result.get('product')} - {result.get('benefit_name')}:\nLayer 2 Details: {result.get('layer_2_details')}\nLayer 3 Eligibility Conditions: {len(result.get('layer_3_eligibility', []))}\nLayer 3 Exclusion Conditions: {len(result.get('layer_3_exclusion', []))}\n\nFull Response: {result}"
                )]
            
            elif name == "show_policy_exclusion":
                product = arguments.get("product")
                response = await client.get(
                    f"{POLICY_ANALYZER_API_URL}/show_policy_exclusion/{product}"
                )
                response.raise_for_status()
                result = response.json()
                return [TextContent(
                    type="text",
                    text=f"Exclusions for {result.get('product')}:\nTotal Count: {result.get('total_count')}\n\nExclusions: {result.get('exclusions')}"
                )]
            
            elif name == "show_policy_exclusion_details":
                response = await client.post(
                    f"{POLICY_ANALYZER_API_URL}/show_policy_exclusion_details",
                    json=arguments
                )
                response.raise_for_status()
                result = response.json()
                return [TextContent(
                    type="text",
                    text=f"Exclusion Details for {result.get('product')} - {result.get('condition')}:\n{result.get('exclusion_details')}"
                )]
            
            elif name == "grade_policy":
                response = await client.post(
                    f"{POLICY_ANALYZER_API_URL}/grade_policy",
                    json=arguments
                )
                response.raise_for_status()
                result = response.json()
                rankings = result.get('rankings', [])
                scores = result.get('policy_scores', {})
                percentages = result.get('percentage_scores', {})
                
                ranking_text = "Policy Rankings:\n"
                for i, policy in enumerate(rankings, 1):
                    score = scores.get(policy, 0)
                    percentage = percentages.get(policy, 0)
                    ranking_text += f"{i}. {policy}: {score:.1f} points ({percentage:.1f}%)\n"
                
                return [TextContent(
                    type="text",
                    text=f"{ranking_text}\n\nDetailed Scores: {result.get('detailed_scores')}\n\nFull Response: {result}"
                )]
            
            elif name == "get_products":
                response = await client.get(f"{POLICY_ANALYZER_API_URL}/products")
                response.raise_for_status()
                result = response.json()
                # Handle both list and other types
                if isinstance(result, list):
                    products = [str(item) for item in result]
                    return [TextContent(
                        type="text",
                        text=f"Available Products: {', '.join(products)}"
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"Available Products: {str(result)}"
                    )]
            
            elif name == "get_eligibility_conditions":
                response = await client.get(f"{POLICY_ANALYZER_API_URL}/eligibility_conditions")
                response.raise_for_status()
                result = response.json()
                return [TextContent(
                    type="text",
                    text=f"Eligibility Conditions: {result}"
                )]
            
            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]
        
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
            logger.error(error_msg)
            return [TextContent(
                type="text",
                text=f"Error calling {name}: {error_msg}"
            )]
        
        except httpx.RequestError as e:
            error_msg = f"Request Error: {str(e)}"
            logger.error(error_msg)
            return [TextContent(
                type="text",
                text=f"Error connecting to Policy Analyzer API at {POLICY_ANALYZER_API_URL}: {error_msg}"
            )]
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return [TextContent(
                type="text",
                text=f"Error calling {name}: {error_msg}"
            )]


async def main():
    """
    Main entry point for the MCP server
    """
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

