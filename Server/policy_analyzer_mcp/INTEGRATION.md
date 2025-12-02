# Policy Analyzer MCP Integration Guide

## Overview

The Policy Analyzer MCP server provides two integration methods:

1. **Standalone MCP Server** (`mcp_server.py`) - For direct MCP protocol usage
2. **LangChain Tools** (`langchain_tools.py`) - For master agent integration (automatically loaded)

## Master Agent Integration

The master agent automatically loads and binds Policy Analyzer tools when available. The integration works as follows:

### How It Works

1. **Tool Loading**: On initialization, the master agent attempts to import `policy_analyzer_mcp.langchain_tools`
2. **Tool Binding**: If successful, tools are bound to the LLM using `bind_tools()`
3. **Automatic Execution**: When the LLM determines a tool call is needed, it's executed automatically
4. **Response Generation**: Tool results are fed back to the LLM for final response generation

### Available Tools

The following tools are available to the master agent:

- `scan_policy_eligibility` - Check if a user is eligible for a policy
- `show_policy_benefits` - List benefits for a product
- `show_policy_benefit_details` - Get detailed benefit information
- `show_policy_exclusion` - List exclusions for a product
- `show_policy_exclusion_details` - Get detailed exclusion information
- `grade_policy` - Compare and rank policies based on prioritized benefits
- `get_products` - Get list of available products
- `get_eligibility_conditions` - Get list of eligibility conditions

### Configuration

Set environment variable:
```bash
POLICY_ANALYZER_API_URL=http://localhost:8006
```

### Prerequisites

1. Policy Analyzer API must be running on port 8006 (or configured URL)
2. Master agent must have `policy_analyzer_mcp` package in Python path
3. Required dependencies installed (see requirements.txt)

### Example Usage

When a user asks the master agent:
- "Am I eligible for Scootsurance?" → Agent calls `scan_policy_eligibility`
- "What benefits does TravelEasy offer?" → Agent calls `show_policy_benefits`
- "Compare policies for me" → Agent calls `grade_policy` (may ask for priorities first)

The agent will automatically use the appropriate tools based on the conversation context.

## Standalone MCP Server

For direct MCP protocol usage (not via master agent):

```bash
python -m policy_analyzer_mcp.mcp_server
```

This starts an MCP server that communicates via stdio and can be connected to any MCP-compatible client.


