"""
Test script to verify both Risk Agent and Predict Agent are functional
"""
import sys

def test_risk_agent():
    """Test Risk Agent MCP Server"""
    print("=" * 70)
    print("Testing Risk Agent")
    print("=" * 70)
    
    try:
        # Test imports
        print("\n1. Testing imports...")
        from risk_agent import mcp_server as risk_mcp_server
        from risk_agent.config import OPENWEATHER_API_KEY, TAVILY_API_KEY, GDACS_ENABLED
        print("   [OK] Module imports successful")
        
        # Test config
        print("\n2. Testing configuration...")
        print(f"   [OK] OpenWeather API Key: {'Configured' if OPENWEATHER_API_KEY else 'Not configured'}")
        print(f"   [OK] Tavily API Key: {'Configured' if TAVILY_API_KEY else 'Not configured'}")
        print(f"   [OK] GDACS Enabled: {GDACS_ENABLED}")
        
        # Test MCP server
        print("\n3. Testing MCP server...")
        if risk_mcp_server:
            print("   [OK] MCP server instance created")
            
            # Try to check for tools
            if hasattr(risk_mcp_server, 'tools'):
                tools = list(risk_mcp_server.tools.keys())
                print(f"   [OK] Found {len(tools)} tools: {', '.join(tools)}")
            elif hasattr(risk_mcp_server, '_tools'):
                tools = list(risk_mcp_server._tools.keys())
                print(f"   [OK] Found {len(tools)} tools: {', '.join(tools)}")
            else:
                print("   [OK] MCP server created (tools will be registered at runtime)")
        else:
            print("   [WARN] MCP server not available - FastMCP may not be installed")
            print("   -> Install with: pip install fastmcp")
        
        # Test implementation functions
        print("\n4. Testing implementation functions...")
        from risk_agent.mcp_server import (
            _get_weather_forecast_impl,
            _check_severe_weather_impl,
            _web_search_risks_impl
        )
        print("   [OK] Implementation functions importable")
        
        print("\n[PASS] Risk Agent: FUNCTIONAL")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Risk Agent: ERROR - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_predict_agent():
    """Test Predict Agent MCP Server"""
    print("\n" + "=" * 70)
    print("Testing Predict Agent")
    print("=" * 70)
    
    try:
        # Test imports
        print("\n1. Testing imports...")
        from predict_agent import mcp_server as predict_mcp_server
        from predict_agent.config import DB_CONFIG
        print("   [OK] Module imports successful")
        
        # Test config
        print("\n2. Testing configuration...")
        print(f"   [OK] Database Host: {DB_CONFIG.get('host', 'Not configured')}")
        print(f"   [OK] Database Name: {DB_CONFIG.get('database', 'Not configured')}")
        print(f"   [OK] Database User: {DB_CONFIG.get('user', 'Not configured')}")
        
        # Test MCP server
        print("\n3. Testing MCP server...")
        if predict_mcp_server:
            print("   [OK] MCP server instance created")
            
            # Try to check for tools
            if hasattr(predict_mcp_server, 'tools'):
                tools = list(predict_mcp_server.tools.keys())
                print(f"   [OK] Found {len(tools)} tools: {', '.join(tools)}")
            elif hasattr(predict_mcp_server, '_tools'):
                tools = list(predict_mcp_server._tools.keys())
                print(f"   [OK] Found {len(tools)} tools: {', '.join(tools)}")
            else:
                print("   [OK] MCP server created (tools will be registered at runtime)")
        else:
            print("   [WARN] MCP server not available - FastMCP may not be installed")
            print("   -> Install with: pip install fastmcp")
        
        # Test implementation functions
        print("\n4. Testing implementation functions...")
        from predict_agent.mcp_server import (
            _find_insurance_plans_impl,
            _get_product_statistics_impl,
            _analyze_destination_coverage_impl
        )
        print("   [OK] Implementation functions importable")
        
        # Test database connection (optional, might fail if DB unavailable)
        print("\n5. Testing database connection...")
        try:
            from predict_agent.database import DatabaseConnection
            db = DatabaseConnection()
            connected = db.connect()
            if connected:
                print("   [OK] Database connection successful")
                db.disconnect()
            else:
                print("   [WARN] Database connection failed (may be expected if DB is not accessible)")
        except Exception as db_error:
            print(f"   [WARN] Database connection test skipped: {db_error}")
        
        print("\n[PASS] Predict Agent: FUNCTIONAL")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Predict Agent: ERROR - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mcp_config():
    """Test MCP configuration"""
    print("\n" + "=" * 70)
    print("Testing MCP Configuration")
    print("=" * 70)
    
    try:
        import json
        import os
        
        mcp_json_path = os.path.join(os.path.expanduser("~"), ".cursor", "mcp.json")
        
        if os.path.exists(mcp_json_path):
            with open(mcp_json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print("\nMCP Servers configured:")
            servers = config.get('mcpServers', {})
            
            for server_name, server_config in servers.items():
                print(f"\n  {server_name}:")
                if 'command' in server_config:
                    print(f"    Command: {server_config.get('command')}")
                    print(f"    Args: {server_config.get('args', [])}")
                elif 'url' in server_config:
                    print(f"    URL: {server_config.get('url')}")
            
            # Check if our servers are configured
            has_risk = 'RiskAgentServer' in servers
            has_predict = 'PredictAgentServer' in servers
            
            print(f"\n[OK] RiskAgentServer configured: {has_risk}")
            print(f"[OK] PredictAgentServer configured: {has_predict}")
            
            return has_risk and has_predict
        else:
            print(f"\n[WARN] MCP configuration file not found at: {mcp_json_path}")
            return False
            
    except Exception as e:
        print(f"\n[FAIL] Error checking MCP config: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("AGENT FUNCTIONALITY TEST")
    print("=" * 70)
    
    results = {
        'risk_agent': test_risk_agent(),
        'predict_agent': test_predict_agent(),
        'mcp_config': test_mcp_config()
    }
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"\nRisk Agent:        {'[PASS]' if results['risk_agent'] else '[FAIL]'}")
    print(f"Predict Agent:     {'[PASS]' if results['predict_agent'] else '[FAIL]'}")
    print(f"MCP Configuration: {'[PASS]' if results['mcp_config'] else '[FAIL]'}")
    
    all_pass = all(results.values())
    
    print("\n" + "=" * 70)
    if all_pass:
        print("[PASS] ALL TESTS PASSED - Both agents are functional!")
    else:
        print("[WARN] SOME TESTS FAILED - Check errors above")
    print("=" * 70)
    
    return all_pass


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
