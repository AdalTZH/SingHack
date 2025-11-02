"""
Risk Agent MCP Server
Exposes tools for travel risk assessment via Model Context Protocol

Tools provided:
- Weather forecasting and severe weather alerts
- Natural disaster detection (earthquakes, tsunamis, typhoons, etc.)
- Web search for travel risks via Tavily
- Travel advisory checking
"""
import sys
from typing import Dict, List, Optional
from datetime import date, datetime, timedelta
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

# Import config
from .config import (
    OPENWEATHER_API_KEY,
    TAVILY_API_KEY,
    GDACS_ENABLED,
    WEATHER_API_PROVIDER
)

# Create MCP server instance
if FASTMCP_AVAILABLE:
    mcp_server = FastMCP(name="RiskAgentServer")
else:
    mcp_server = None

# ============================================================================
# WEATHER TOOLS
# ============================================================================

def _get_weather_forecast_impl(location: str, departure_date: Optional[str] = None, return_date: Optional[str] = None) -> Dict:
    """Implementation for getting weather forecast"""
    if not OPENWEATHER_API_KEY:
        return {'error': 'OpenWeatherMap API key not configured'}
    
    try:
        import requests
        
        # Geocode location
        geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        geo_params = {
            'q': location,
            'limit': 1,
            'appid': OPENWEATHER_API_KEY
        }
        
        geo_response = requests.get(geo_url, params=geo_params, timeout=10)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        
        if not geo_data:
            return {'error': f'Could not find location: {location}'}
        
        lat = geo_data[0]['lat']
        lon = geo_data[0]['lon']
        location_name = geo_data[0].get('name', location)
        
        # Get forecast
        forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
        forecast_params = {
            'lat': lat,
            'lon': lon,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric'
        }
        
        forecast_response = requests.get(forecast_url, params=forecast_params, timeout=10)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        
        # Get current weather
        current_url = "http://api.openweathermap.org/data/2.5/weather"
        current_response = requests.get(current_url, params={**forecast_params}, timeout=10)
        current_data = current_response.json() if current_response.status_code == 200 else None
        
        return {
            'location': location_name,
            'coordinates': {'lat': lat, 'lon': lon},
            'current': current_data,
            'forecast': forecast_data,
            'source': 'openweathermap'
        }
        
    except Exception as e:
        logger.error(f"Error fetching weather forecast: {e}")
        return {'error': str(e)}


def _check_severe_weather_impl(location: str, departure_date: Optional[str] = None, return_date: Optional[str] = None) -> Dict:
    """Implementation for checking severe weather conditions"""
    forecast_result = _get_weather_forecast_impl(location, departure_date, return_date)
    
    if 'error' in forecast_result:
        return forecast_result
    
    risks = []
    forecast_list = forecast_result.get('forecast', {}).get('list', [])
    
    # Parse dates if provided
    travel_start = None
    travel_end = None
    if departure_date:
        try:
            travel_start = datetime.fromisoformat(departure_date.replace('Z', '+00:00')).date()
        except:
            travel_start = datetime.strptime(departure_date, '%Y-%m-%d').date()
    if return_date:
        try:
            travel_end = datetime.fromisoformat(return_date.replace('Z', '+00:00')).date()
        except:
            travel_end = datetime.strptime(return_date, '%Y-%m-%d').date()
    
    for item in forecast_list:
        weather_main = item.get('weather', [{}])[0].get('main', '').lower()
        weather_desc = item.get('weather', [{}])[0].get('description', '').lower()
        wind_speed = item.get('wind', {}).get('speed', 0)
        rain_volume = item.get('rain', {}).get('3h', 0)
        snow_volume = item.get('snow', {}).get('3h', 0)
        temp_max = item.get('main', {}).get('temp_max', 0)
        temp_min = item.get('main', {}).get('temp_min', 0)
        
        dt = datetime.fromtimestamp(item.get('dt', 0))
        forecast_date = dt.date()
        
        # Check if within travel period
        if travel_start and travel_end:
            if not (travel_start <= forecast_date <= travel_end):
                continue
        
        # Check for severe conditions
        if 'thunderstorm' in weather_main:
            risks.append({
                'type': 'thunderstorm',
                'date': str(forecast_date),
                'severity': 'high',
                'description': weather_desc,
                'wind_speed_ms': wind_speed
            })
        
        if rain_volume > 10:
            risks.append({
                'type': 'heavy_rain',
                'date': str(forecast_date),
                'severity': 'medium' if rain_volume < 25 else 'high',
                'precipitation_mm': rain_volume,
                'description': weather_desc
            })
        
        if wind_speed > 15:
            risks.append({
                'type': 'high_wind',
                'date': str(forecast_date),
                'severity': 'high' if wind_speed > 25 else 'medium',
                'wind_speed_ms': wind_speed,
                'description': weather_desc
            })
        
        if temp_max > 35:
            risks.append({
                'type': 'extreme_heat',
                'date': str(forecast_date),
                'severity': 'high' if temp_max > 40 else 'medium',
                'temperature_c': temp_max,
                'description': f'Extreme heat: {temp_max}°C'
            })
        
        if temp_min < 0:
            risks.append({
                'type': 'extreme_cold',
                'date': str(forecast_date),
                'severity': 'high' if temp_min < -10 else 'medium',
                'temperature_c': temp_min,
                'description': f'Extreme cold: {temp_min}°C'
            })
    
    return {
        'location': forecast_result.get('location', location),
        'risks': risks,
        'risk_count': len(risks),
        'source': 'openweathermap'
    }


# ============================================================================
# DISASTER TOOLS
# ============================================================================

def _check_natural_disasters_impl(location: str, departure_date: Optional[str] = None, return_date: Optional[str] = None) -> Dict:
    """Implementation for checking natural disaster alerts"""
    if not GDACS_ENABLED:
        return {'error': 'GDACS alerts are disabled'}
    
    risks = []
    
    try:
        import requests
        import xml.etree.ElementTree as ET
        import re
        
        # Fetch GDACS RSS feed
        gdacs_rss_url = "https://www.gdacs.org/xml/rss.xml"
        response = requests.get(gdacs_rss_url, timeout=15)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        destination = location.lower()
        
        # Parse travel dates
        travel_start = None
        travel_end = None
        if departure_date:
            try:
                travel_start = datetime.fromisoformat(departure_date.replace('Z', '+00:00')).date()
            except:
                travel_start = datetime.strptime(departure_date, '%Y-%m-%d').date()
        if return_date:
            try:
                travel_end = datetime.fromisoformat(return_date.replace('Z', '+00:00')).date()
            except:
                travel_end = datetime.strptime(return_date, '%Y-%m-%d').date()
        
        items = root.findall('.//item')
        
        for item in items[:50]:
            title_elem = item.find('title')
            description_elem = item.find('description')
            pub_date_elem = item.find('pubDate')
            link_elem = item.find('link')
            
            if title_elem is None:
                continue
            
            title = title_elem.text or ''
            description = description_elem.text if description_elem is not None else ''
            pub_date = pub_date_elem.text if pub_date_elem is not None else ''
            link = link_elem.text if link_elem is not None else ''
            
            text = (title + ' ' + description).lower()
            
            # Check if matches destination
            destination_words = destination.split()
            matches = any(word in text for word in destination_words if len(word) > 3)
            
            if not matches:
                if ',' in destination:
                    country_part = destination.split(',')[-1].strip()
                    matches = country_part in text and len(country_part) > 2
            
            if not matches:
                continue
            
            # Extract event type
            event_type = 'Natural Disaster'
            if 'earthquake' in text or ' eq ' in title.lower() or '[EQ]' in title:
                event_type = 'Earthquake'
            elif 'tsunami' in text or ' ts ' in title.lower() or '[TS]' in title:
                event_type = 'Tsunami'
            elif 'cyclone' in text or 'hurricane' in text or 'typhoon' in text or ' tc ' in title.lower() or '[TC]' in title:
                event_type = 'Tropical Cyclone'
            elif 'flood' in text or ' fl ' in title.lower() or '[FL]' in title:
                event_type = 'Flood'
            elif 'volcano' in text or 'volcanic' in text or ' vo ' in title.lower() or '[VO]' in title:
                event_type = 'Volcano'
            elif 'wildfire' in text or 'fire' in text:
                event_type = 'Wildfire'
            
            # Determine severity
            severity = 'low'
            if 'red' in text or 'RED' in title or 'severe' in text or 'major' in text:
                severity = 'critical'
            elif 'orange' in text or 'ORANGE' in title or 'moderate' in text:
                severity = 'high'
            elif 'yellow' in text or 'YELLOW' in title:
                severity = 'medium'
            
            # Parse date
            event_date = None
            if pub_date:
                try:
                    from dateutil import parser
                    event_date = parser.parse(pub_date).date()
                except:
                    pass
            
            # Check date relevance
            if event_date:
                if travel_start and travel_end:
                    days_diff = abs((event_date - travel_start).days)
                    if days_diff > 60 and not (travel_start <= event_date <= travel_end):
                        continue
                elif travel_start:
                    days_diff = abs((event_date - travel_start).days)
                    if days_diff > 60:
                        continue
            
            risks.append({
                'type': event_type,
                'title': title,
                'description': description[:300] if description else title,
                'date': str(event_date) if event_date else None,
                'severity': severity,
                'url': link,
                'source': 'gdacs'
            })
        
        return {
            'location': location,
            'risks': risks,
            'risk_count': len(risks),
            'source': 'gdacs'
        }
        
    except Exception as e:
        logger.error(f"Error checking natural disasters: {e}")
        return {'error': str(e)}


# ============================================================================
# WEB SEARCH TOOLS
# ============================================================================

def _web_search_risks_impl(query: str, destination: Optional[str] = None, max_results: int = 5) -> Dict:
    """Implementation for web search using Tavily"""
    if not TAVILY_API_KEY:
        return {'error': 'Tavily API key not configured'}
    
    try:
        from tavily import TavilyClient
        
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results
        )
        return response
    except Exception as e:
        logger.error(f"Error in web search: {e}")
        return {'results': [], 'error': str(e)}


def _check_travel_advisories_impl(destination: str, country: Optional[str] = None) -> Dict:
    """Implementation for checking travel advisories"""
    if not TAVILY_API_KEY:
        return {'error': 'Tavily API key not configured'}
    
    advisories = []
    
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_API_KEY)
        
        # Search for travel advisories from various sources
        queries = [
            f"{destination} travel advisory government warning",
            f"{destination} US State Department travel advisory",
            f"{destination} UK FCO travel warning",
            f"{destination} travel alert"
        ]
        
        if country:
            queries.append(f"{country} travel advisory")
        
        for query in queries:
            response = client.search(query=query, max_results=3)
            results = response.get('results', [])
            for result in results:
                # Avoid duplicates
                if not any(adv['url'] == result.get('url') for adv in advisories):
                    advisories.append({
                        'title': result.get('title', ''),
                        'content': result.get('content', ''),
                        'url': result.get('url', ''),
                        'source': 'tavily_web_search'
                    })
        
        return {
            'destination': destination,
            'advisories': advisories,
            'advisory_count': len(advisories),
            'source': 'tavily_web_search'
        }
        
    except Exception as e:
        logger.error(f"Error checking travel advisories: {e}")
        return {'error': str(e)}


def _comprehensive_risk_search_impl(
    destination: str,
    departure_date: Optional[str] = None,
    activities: Optional[List[str]] = None,
    max_results_per_category: int = 3
) -> Dict:
    """Implementation for comprehensive risk search"""
    if not TAVILY_API_KEY:
        return {'error': 'Tavily API key not configured'}
    
    results = {
        'destination': destination,
        'general_risks': [],
        'weather_risks': [],
        'disaster_risks': [],
        'advisory_risks': [],
        'activity_risks': []
    }
    
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_API_KEY)
        
        # General risks
        query = f"{destination} travel risks safety"
        response = client.search(query=query, max_results=max_results_per_category)
        results['general_risks'] = response.get('results', [])
        
        # Weather risks
        if departure_date:
            query = f"{destination} weather warnings {departure_date}"
        else:
            query = f"{destination} weather warnings"
        response = client.search(query=query, max_results=max_results_per_category)
        results['weather_risks'] = response.get('results', [])
        
        # Disaster risks
        query = f"{destination} natural disasters"
        response = client.search(query=query, max_results=max_results_per_category)
        results['disaster_risks'] = response.get('results', [])
        
        # Advisory risks
        query = f"{destination} travel advisory warning"
        response = client.search(query=query, max_results=max_results_per_category)
        results['advisory_risks'] = response.get('results', [])
        
        # Activity-specific risks
        if activities:
            for activity in activities:
                query = f"{destination} {activity} risks"
                response = client.search(query=query, max_results=2)
                results['activity_risks'].extend(response.get('results', []))
        
    except Exception as e:
        logger.error(f"Error in comprehensive risk search: {e}")
        results['error'] = str(e)
    
    return results


# ============================================================================
# REGISTER MCP TOOLS
# ============================================================================

if mcp_server:
    @mcp_server.tool(
        name="get_weather_forecast",
        description="Get weather forecast for a location. Returns current conditions and 5-day forecast including temperature, precipitation, wind, and conditions."
    )
    def get_weather_forecast(
        location: str,
        departure_date: Optional[str] = None,
        return_date: Optional[str] = None
    ) -> Dict:
        """Get weather forecast for a specific location and optional travel dates"""
        return _get_weather_forecast_impl(location, departure_date, return_date)
    
    @mcp_server.tool(
        name="check_severe_weather",
        description="Check for severe weather conditions (thunderstorms, heavy rain, high winds, extreme temperatures) for a location and travel dates. Returns list of weather risks with severity levels."
    )
    def check_severe_weather(
        location: str,
        departure_date: Optional[str] = None,
        return_date: Optional[str] = None
    ) -> Dict:
        """Check for severe weather risks during travel period"""
        return _check_severe_weather_impl(location, departure_date, return_date)
    
    @mcp_server.tool(
        name="check_natural_disasters",
        description="Check for natural disaster alerts (earthquakes, tsunamis, typhoons, floods, volcanoes, wildfires) for a location using GDACS. Returns alerts matching the destination."
    )
    def check_natural_disasters(
        location: str,
        departure_date: Optional[str] = None,
        return_date: Optional[str] = None
    ) -> Dict:
        """Check for natural disaster alerts for a location"""
        return _check_natural_disasters_impl(location, departure_date, return_date)
    
    @mcp_server.tool(
        name="web_search_risks",
        description="Search the web for travel risks and warnings using Tavily. Optimized for finding travel-related safety information, advisories, and risk reports."
    )
    def web_search_risks(
        query: str,
        destination: Optional[str] = None,
        max_results: int = 5
    ) -> Dict:
        """Search web for travel risks"""
        return _web_search_risks_impl(query, destination, max_results)
    
    @mcp_server.tool(
        name="comprehensive_risk_search",
        description="Perform comprehensive risk search for a destination including weather, disasters, advisories, and general safety concerns. Searches multiple risk categories and returns organized results."
    )
    def comprehensive_risk_search(
        destination: str,
        departure_date: Optional[str] = None,
        activities: Optional[List[str]] = None,
        max_results_per_category: int = 3
    ) -> Dict:
        """Comprehensive risk search combining multiple search strategies"""
        return _comprehensive_risk_search_impl(destination, departure_date, activities, max_results_per_category)
    
    @mcp_server.tool(
        name="check_travel_advisories",
        description="Check for government travel advisories and warnings for a destination. Searches for official travel advisories from government sources (US State Department, UK FCO, etc.)"
    )
    def check_travel_advisories(
        destination: str,
        country: Optional[str] = None
    ) -> Dict:
        """Check for travel advisories and government warnings"""
        return _check_travel_advisories_impl(destination, country)
    
    logger.info("MCP server tools registered successfully")
else:
    logger.warning("MCP server not available - tools cannot be registered")


# ============================================================================
# SERVER ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    if mcp_server:
        # Run the MCP server
        # FastMCP uses stdio transport for MCP protocol by default
        try:
            mcp_server.run()
        except Exception as e:
            logger.error(f"Error running MCP server: {e}")
            sys.exit(1)
    else:
        print("Error: FastMCP not available. Install with: pip install fastmcp")
        sys.exit(1)

