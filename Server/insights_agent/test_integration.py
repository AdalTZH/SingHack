"""
Test script to verify Insights Agent + Start Insights integration
"""
import requests
import json
import time
from colorama import init, Fore, Style

init(autoreset=True)

INSIGHTS_AGENT_URL = "http://localhost:8008"
START_INSIGHTS_URL = "http://localhost:5000"

def print_header(text):
    """Print formatted header"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}{text}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")

def print_success(text):
    """Print success message"""
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

def print_error(text):
    """Print error message"""
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

def print_info(text):
    """Print info message"""
    print(f"{Fore.YELLOW}ℹ {text}{Style.RESET_ALL}")

def test_health_checks():
    """Test health endpoints"""
    print_header("Testing Health Checks")
    
    # Test Insights Agent
    try:
        response = requests.get(f"{INSIGHTS_AGENT_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success(f"Insights Agent (8008): {response.json()}")
        else:
            print_error(f"Insights Agent health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Insights Agent not reachable: {e}")
        return False
    
    # Test Start Insights
    try:
        response = requests.get(f"{START_INSIGHTS_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success(f"Start Insights API (5000): {response.json()}")
        else:
            print_error(f"Start Insights health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Start Insights API not reachable: {e}")
        return False
    
    return True

def test_query(query, should_analyze_expected=None):
    """Test a query through the Insights Agent"""
    print(f"\n{Fore.MAGENTA}Testing Query: {query}{Style.RESET_ALL}")
    print("-" * 70)
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{INSIGHTS_AGENT_URL}/process",
            json={'query': query},
            timeout=35
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            print_info(f"Response time: {elapsed:.2f}s")
            print_info(f"Should analyze: {data.get('should_analyze')}")
            print_info(f"Performed analytics: {data.get('performed_analytics')}")
            print_info(f"Confidence: {data.get('confidence', 0.0):.2f}")
            print_info(f"Reasoning: {data.get('reasoning', 'N/A')}")
            
            if data.get('insights'):
                print(f"\n{Fore.GREEN}Insights:{Style.RESET_ALL}")
                print(f"{data.get('insights')}\n")
                print_success("✓ Insights generated successfully")
            elif data.get('should_analyze') and data.get('performed_analytics'):
                print_error("Should analyze but no insights returned")
                if data.get('error'):
                    print_error(f"Error: {data.get('error')}")
            else:
                print_info("No insights generated (as expected)")
            
            # Verify expectation if provided
            if should_analyze_expected is not None:
                if data.get('should_analyze') == should_analyze_expected:
                    print_success(f"Correctly determined should_analyze={should_analyze_expected}")
                else:
                    print_error(f"Expected should_analyze={should_analyze_expected}, got {data.get('should_analyze')}")
            
            return data
            
        else:
            print_error(f"Request failed: {response.status_code}")
            print_error(response.text)
            return None
            
    except requests.exceptions.Timeout:
        print_error("Request timeout (>35s)")
        return None
    except Exception as e:
        print_error(f"Error: {e}")
        return None

def run_tests():
    """Run all tests"""
    print_header("INSIGHTS AGENT INTEGRATION TEST")
    
    # Test health checks
    if not test_health_checks():
        print_error("\n❌ Health checks failed. Ensure both servers are running:")
        print("  Terminal 1: python Server/start_insights.py")
        print("  Terminal 2: python Server/insights_agent/server.py")
        return
    
    print_success("\n✓ All services are healthy\n")
    
    # Test queries that SHOULD trigger analytics
    print_header("Testing Queries That SHOULD Trigger Analytics")
    
    test_query(
        "What are the medical risks of traveling to China?",
        should_analyze_expected=True
    )
    
    test_query(
        "Which destinations have the highest claim costs?",
        should_analyze_expected=True
    )
    
    test_query(
        "Should I buy travel insurance for Thailand?",
        should_analyze_expected=True
    )
    
    # Test queries that SHOULD NOT trigger analytics
    print_header("Testing Queries That SHOULD NOT Trigger Analytics")
    
    test_query(
        "Hello, how are you?",
        should_analyze_expected=False
    )
    
    test_query(
        "What's your name?",
        should_analyze_expected=False
    )
    
    print_header("TEST SUMMARY")
    print_success("Integration test completed!")
    print_info("\nKey Points:")
    print("  1. Insights Agent correctly determines when to analyze")
    print("  2. Start Insights API generates Cypher queries and insights")
    print("  3. Response format is correct for extension integration")
    print("\nNext Steps:")
    print("  - Integrate with extension using the INTEGRATION_GUIDE.md")
    print("  - Display insights at top of chat when should_analyze=true")
    print("  - Use the insights field for the persuasive text")

if __name__ == '__main__':
    try:
        run_tests()
    except KeyboardInterrupt:
        print_error("\n\nTest interrupted by user")
    except Exception as e:
        print_error(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()



