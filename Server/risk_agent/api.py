"""
Risk Agent API Server
Provides REST API endpoints for risk assessment
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging

from .config import RISK_ASSESSMENT_SETTINGS
from .mcp_server import (
    _get_weather_forecast_impl,
    _check_severe_weather_impl,
    _check_natural_disasters_impl,
    _web_search_risks_impl,
    _comprehensive_risk_search_impl,
    _check_travel_advisories_impl
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Risk Agent API",
    description="Travel risk assessment API using MCP tools",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://*",
        "http://localhost:*",
        "http://127.0.0.1:*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class RiskAssessmentRequest(BaseModel):
    """Request model for risk assessment"""
    query: str
    destination: Optional[str] = None
    departure_date: Optional[str] = None
    return_date: Optional[str] = None
    activities: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None


class RiskAssessmentResponse(BaseModel):
    """Response model for risk assessment"""
    success: bool
    destination: str
    weather_risks: List[Dict[str, Any]]
    natural_disasters: List[Dict[str, Any]]
    travel_advisories: List[Dict[str, Any]]
    activity_risks: List[Dict[str, Any]]
    overall_risk_level: str
    recommendations: List[str]
    error: Optional[str] = None


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Risk Agent API",
        "mcp_tools_available": True
    }


@app.post("/assess_risk", response_model=RiskAssessmentResponse)
async def assess_risk(request: RiskAssessmentRequest):
    """
    Comprehensive risk assessment endpoint
    Assesses weather, natural disasters, travel advisories, and activity risks
    """
    logger.info(f"Assessing risk for: {request.query}")
    
    try:
        # Extract destination from query or use provided destination
        destination = request.destination
        if not destination:
            destination = request.query
        
        # Initialize risk assessment results
        weather_risks = []
        natural_disasters = []
        travel_advisories = []
        activity_risks = []
        recommendations = []
        
        # Check weather risks
        if RISK_ASSESSMENT_SETTINGS.get('check_weather', True):
            try:
                weather_result = _check_severe_weather_impl(
                    location=destination,
                    departure_date=request.departure_date,
                    return_date=request.return_date
                )
                if 'risks' in weather_result:
                    weather_risks = weather_result['risks']
                    if weather_risks:
                        recommendations.append(f"Consider travel dates carefully - {len(weather_risks)} weather risk(s) detected")
                logger.info(f"Weather risks found: {len(weather_risks)}")
            except Exception as e:
                logger.error(f"Error checking weather: {e}")
        
        # Check natural disasters
        if RISK_ASSESSMENT_SETTINGS.get('check_natural_disasters', True):
            try:
                disaster_result = _check_natural_disasters_impl(
                    location=destination,
                    departure_date=request.departure_date,
                    return_date=request.return_date
                )
                if 'risks' in disaster_result:
                    natural_disasters = disaster_result['risks']
                    if natural_disasters:
                        recommendations.append(f"Natural disaster alerts: {len(natural_disasters)} active alert(s)")
                logger.info(f"Natural disasters found: {len(natural_disasters)}")
            except Exception as e:
                logger.error(f"Error checking disasters: {e}")
        
        # Check travel advisories
        if RISK_ASSESSMENT_SETTINGS.get('check_travel_advisories', True):
            try:
                advisory_result = _check_travel_advisories_impl(destination=destination)
                if 'advisories' in advisory_result:
                    travel_advisories = advisory_result['advisories']
                    if travel_advisories:
                        recommendations.append(f"Check government travel advisories - {len(travel_advisories)} alert(s) found")
                logger.info(f"Travel advisories found: {len(travel_advisories)}")
            except Exception as e:
                logger.error(f"Error checking advisories: {e}")
        
        # Check activity-specific risks if activities provided
        if request.activities:
            try:
                for activity in request.activities:
                    activity_result = _comprehensive_risk_search_impl(
                        destination=destination,
                        departure_date=request.departure_date,
                        activities=[activity],
                        max_results_per_category=2
                    )
                    if 'activity_risks' in activity_result:
                        activity_risks.extend(activity_result['activity_risks'])
                logger.info(f"Activity risks found: {len(activity_risks)}")
            except Exception as e:
                logger.error(f"Error checking activity risks: {e}")
        
        # Determine overall risk level
        total_risks = len(weather_risks) + len(natural_disasters) + len(travel_advisories) + len(activity_risks)
        
        if total_risks == 0:
            overall_risk_level = "low"
            recommendations.append("No significant risks detected for this destination")
        elif total_risks <= 2:
            overall_risk_level = "low"
            recommendations.append("Minimal risks detected - standard insurance coverage recommended")
        elif total_risks <= 5:
            overall_risk_level = "medium"
            recommendations.append("Moderate risks detected - comprehensive insurance coverage recommended")
        else:
            overall_risk_level = "high"
            recommendations.append("Significant risks detected - comprehensive insurance with extensive coverage strongly recommended")
        
        response = RiskAssessmentResponse(
            success=True,
            destination=destination,
            weather_risks=weather_risks,
            natural_disasters=natural_disasters,
            travel_advisories=travel_advisories,
            activity_risks=activity_risks,
            overall_risk_level=overall_risk_level,
            recommendations=recommendations
        )
        
        logger.info(f"Risk assessment complete: {overall_risk_level} risk level")
        return response
        
    except Exception as e:
        logger.error(f"Error in risk assessment: {e}")
        return RiskAssessmentResponse(
            success=False,
            destination=destination or "",
            weather_risks=[],
            natural_disasters=[],
            travel_advisories=[],
            activity_risks=[],
            overall_risk_level="unknown",
            recommendations=[],
            error=str(e)
        )


@app.get("/weather")
async def get_weather(
    location: str,
    departure_date: Optional[str] = None,
    return_date: Optional[str] = None
):
    """
    Get weather forecast for a location
    """
    try:
        result = _get_weather_forecast_impl(
            location=location,
            departure_date=departure_date,
            return_date=return_date
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error getting weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/disasters")
async def check_disasters(
    location: str,
    departure_date: Optional[str] = None,
    return_date: Optional[str] = None
):
    """
    Check for natural disaster alerts
    """
    try:
        result = _check_natural_disasters_impl(
            location=location,
            departure_date=departure_date,
            return_date=return_date
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error checking disasters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/advisories")
async def check_advisories(destination: str, country: Optional[str] = None):
    """
    Check for travel advisories
    """
    try:
        result = _check_travel_advisories_impl(
            destination=destination,
            country=country
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error checking advisories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Risk Agent API",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "assess_risk": "POST /assess_risk",
            "weather": "GET /weather",
            "disasters": "GET /disasters",
            "advisories": "GET /advisories"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)









