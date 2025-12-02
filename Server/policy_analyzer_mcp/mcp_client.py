"""
MCP Client for Policy Analyzer
Client wrapper that connects to the MCP server and provides tools for the master agent
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .config import POLICY_ANALYZER_API_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PolicyAnalyzerMCPClient:
    """
    MCP Client for Policy Analyzer tools
    Provides async methods to call MCP tools
    """
    
    def __init__(self, mcp_server_path: Optional[str] = None):
        """
        Initialize MCP client
        
        Args:
            mcp_server_path: Path to MCP server script (default: uses stdio)
        """
        self.mcp_server_path = mcp_server_path
        self.session: Optional[ClientSession] = None
    
    async def connect(self):
        """Connect to MCP server"""
        if self.mcp_server_path:
            server_params = StdioServerParameters(
                command="python",
                args=[self.mcp_server_path]
            )
        else:
            # Use local server
            import os
            server_script = os.path.join(
                os.path.dirname(__file__),
                "mcp_server.py"
            )
            server_params = StdioServerParameters(
                command="python",
                args=[server_script]
            )
        
        self.session = await stdio_client(server_params)
        await self.session.initialize()
        logger.info("Connected to Policy Analyzer MCP server")
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.session:
            await self.session.__aexit__(None, None, None)
            self.session = None
    
    async def scan_policy_eligibility(self, product: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Scan policy eligibility"""
        if not self.session:
            await self.connect()
        
        result = await self.session.call_tool(
            "scan_policy_eligibility",
            {"product": product, "user_data": user_data}
        )
        return result
    
    async def show_policy_benefits(self, product: Optional[str] = None) -> Dict[str, Any]:
        """Show policy benefits"""
        if not self.session:
            await self.connect()
        
        args = {}
        if product:
            args["product"] = product
        
        result = await self.session.call_tool("show_policy_benefits", args)
        return result
    
    async def show_policy_benefit_details(self, product: str, benefit_name: str) -> Dict[str, Any]:
        """Show policy benefit details"""
        if not self.session:
            await self.connect()
        
        result = await self.session.call_tool(
            "show_policy_benefit_details",
            {"product": product, "benefit_name": benefit_name}
        )
        return result
    
    async def show_policy_exclusion(self, product: str) -> Dict[str, Any]:
        """Show policy exclusions"""
        if not self.session:
            await self.connect()
        
        result = await self.session.call_tool(
            "show_policy_exclusion",
            {"product": product}
        )
        return result
    
    async def show_policy_exclusion_details(self, product: str, condition: str) -> Dict[str, Any]:
        """Show policy exclusion details"""
        if not self.session:
            await self.connect()
        
        result = await self.session.call_tool(
            "show_policy_exclusion_details",
            {"product": product, "condition": condition}
        )
        return result
    
    async def grade_policy(self, prioritized_benefits: List[Any]) -> Dict[str, Any]:
        """Grade policies"""
        if not self.session:
            await self.connect()
        
        result = await self.session.call_tool(
            "grade_policy",
            {"prioritized_benefits": prioritized_benefits}
        )
        return result
    
    async def get_products(self) -> List[str]:
        """Get available products"""
        if not self.session:
            await self.connect()
        
        result = await self.session.call_tool("get_products", {})
        return result
    
    async def get_eligibility_conditions(self) -> List[Dict[str, Any]]:
        """Get eligibility conditions"""
        if not self.session:
            await self.connect()
        
        result = await self.session.call_tool("get_eligibility_conditions", {})
        return result


