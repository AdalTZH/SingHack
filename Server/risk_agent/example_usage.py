"""
Example usage of Risk Agent MCP Server tools
This demonstrates how to use the tools programmatically
"""
from datetime import date
from .mcp_server import (
    _get_weather_forecast_impl,
    _check_severe_weather_impl,
    _check_natural_disasters_impl,
    _web_search_risks_impl,
    _comprehensive_risk_search_impl
)


def example_weather_forecast():
    """Example: Get weather forecast"""
    print("=" * 60)
    print("Example: Weather Forecast")
    print("=" * 60)
    
    result = _get_weather_forecast_impl(
        location="Tokyo, Japan",
        departure_date="2025-03-15",
        return_date="2025-03-25"
    )
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Location: {result.get('location')}")
        print(f"Coordinates: {result.get('coordinates')}")
        if result.get('current'):
            current = result['current']
            weather = current.get('weather', [{}])[0]
            main = current.get('main', {})
            print(f"Current: {weather.get('description')}, {main.get('temp')}°C")


def example_severe_weather():
    """Example: Check for severe weather"""
    print("\n" + "=" * 60)
    print("Example: Severe Weather Check")
    print("=" * 60)
    
    result = _check_severe_weather_impl(
        location="Tokyo, Japan",
        departure_date="2025-03-15",
        return_date="2025-03-25"
    )
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Location: {result.get('location')}")
        print(f"Risks Found: {result.get('risk_count', 0)}")
        for risk in result.get('risks', [])[:3]:  # Show first 3
            print(f"  - {risk.get('type')} on {risk.get('date')}: {risk.get('severity')} severity")


def example_natural_disasters():
    """Example: Check for natural disasters"""
    print("\n" + "=" * 60)
    print("Example: Natural Disaster Check")
    print("=" * 60)
    
    result = _check_natural_disasters_impl(
        location="Tokyo, Japan",
        departure_date="2025-03-15",
        return_date="2025-03-25"
    )
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Location: {result.get('location')}")
        print(f"Disaster Alerts Found: {result.get('risk_count', 0)}")
        for risk in result.get('risks', [])[:3]:  # Show first 3
            print(f"  - {risk.get('type')}: {risk.get('severity')} severity")
            print(f"    {risk.get('title', '')[:60]}...")


def example_web_search():
    """Example: Web search for risks"""
    print("\n" + "=" * 60)
    print("Example: Web Search for Risks")
    print("=" * 60)
    
    result = _web_search_risks_impl(
        query="Tokyo Japan travel risks March 2025",
        destination="Tokyo, Japan",
        max_results=3
    )
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Search Results: {len(result.get('results', []))} found")
        for item in result.get('results', [])[:3]:
            print(f"\n  Title: {item.get('title', 'N/A')}")
            print(f"  URL: {item.get('url', 'N/A')}")
            print(f"  Content: {item.get('content', '')[:100]}...")


def example_comprehensive_search():
    """Example: Comprehensive risk search"""
    print("\n" + "=" * 60)
    print("Example: Comprehensive Risk Search")
    print("=" * 60)
    
    result = _comprehensive_risk_search_impl(
        destination="Tokyo, Japan",
        departure_date="2025-03-15",
        activities=["hiking", "sightseeing"],
        max_results_per_category=2
    )
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Destination: {result.get('destination')}")
        print(f"General Risks: {len(result.get('general_risks', []))}")
        print(f"Weather Risks: {len(result.get('weather_risks', []))}")
        print(f"Disaster Risks: {len(result.get('disaster_risks', []))}")
        print(f"Advisory Risks: {len(result.get('advisory_risks', []))}")
        print(f"Activity Risks: {len(result.get('activity_risks', []))}")


if __name__ == "__main__":
    print("\nRisk Agent MCP Server - Example Usage\n")
    
    try:
        example_weather_forecast()
        example_severe_weather()
        example_natural_disasters()
        example_web_search()
        example_comprehensive_search()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()

