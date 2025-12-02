"""
FastAPI Server for Insurance Policy Quotation API
Provides quotation services for Scootsurance, TravelEasy, and TravelEasy Pre-Ex
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import logging

from .config import SERVER_HOST, SERVER_PORT, ALLOWED_ORIGINS
from .quotation_engine import QuotationEngine, PolicyType, Tier, Continent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Insurance Quotation API",
    description="API for generating insurance policy quotations with multiple coverage tiers",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Request/Response Models
# ============================================================================

class QuotationRequest(BaseModel):
    """Request model for quotation generation"""
    policy_type: str = Field(
        ..., 
        description="Policy type: 'Scootsurance', 'TravelEasy', or 'TravelEasy Pre-Ex'"
    )
    age: int = Field(
        ..., 
        ge=0, 
        le=100,
        description="Age of the insured person (0-100)"
    )
    days: int = Field(
        ..., 
        ge=1,
        description="Number of days travelling (minimum 1)"
    )
    continent: str = Field(
        ..., 
        description="Destination continent: 'Asia', 'Europe', 'North America', 'South America', 'Africa', 'Oceania', or 'Antarctica'"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "policy_type": "Scootsurance",
                "age": 35,
                "days": 7,
                "continent": "Asia"
            }
        }


class TierQuotation(BaseModel):
    """Quotation details for a single tier"""
    tier: str = Field(..., description="Tier name: Basic, Standard, or Premium")
    premium: float = Field(..., description="Premium amount in SGD")
    currency: str = Field(default="SGD", description="Currency code")
    coverage_features: List[str] = Field(..., description="List of coverage features for this tier")
    description: str = Field(..., description="Description of the tier")


class QuotationResponse(BaseModel):
    """Response model for quotation generation"""
    success: bool
    policy_type: str
    age: int
    days: int
    continent: str
    tiers: List[TierQuotation]
    calculation_date: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "policy_type": "Scootsurance",
                "age": 35,
                "days": 7,
                "continent": "Asia",
                "tiers": [
                    {
                        "tier": "Basic",
                        "premium": 52.50,
                        "currency": "SGD",
                        "coverage_features": [
                            "Medical expenses coverage",
                            "Trip cancellation",
                            "Baggage loss",
                            "Basic emergency assistance"
                        ],
                        "description": "Essential coverage for basic travel protection"
                    },
                    {
                        "tier": "Standard",
                        "premium": 78.75,
                        "currency": "SGD",
                        "coverage_features": [
                            "All Basic features",
                            "Higher medical coverage limits",
                            "Trip delay coverage",
                            "Personal accident coverage",
                            "24/7 emergency assistance"
                        ],
                        "description": "Comprehensive coverage with enhanced benefits"
                    },
                    {
                        "tier": "Premium",
                        "premium": 105.00,
                        "currency": "SGD",
                        "coverage_features": [
                            "All Standard features",
                            "Maximum coverage limits",
                            "Adventure sports coverage",
                            "Pre-existing conditions (where applicable)",
                            "Premium concierge services",
                            "Extended coverage periods"
                        ],
                        "description": "Maximum protection with premium services and highest limits"
                    }
                ],
                "calculation_date": "2024-01-15T10:30:00"
            }
        }


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str
    version: str
    supported_policies: List[str]
    supported_continents: List[str]


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def root():
    """
    Root endpoint - returns API information
    """
    return HealthResponse(
        status="healthy",
        service="Insurance Quotation API",
        version="1.0.0",
        supported_policies=[pt.value for pt in PolicyType],
        supported_continents=[c.value for c in Continent]
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    """
    return HealthResponse(
        status="healthy",
        service="Insurance Quotation API",
        version="1.0.0",
        supported_policies=[pt.value for pt in PolicyType],
        supported_continents=[c.value for c in Continent]
    )


@app.post("/quote", response_model=QuotationResponse)
async def generate_quotation(request: QuotationRequest):
    """
    Generate insurance policy quotation with three tiers (Basic, Standard, Premium)
    
    This endpoint calculates premiums based on:
    - Policy type (Scootsurance, TravelEasy, TravelEasy Pre-Ex)
    - Age of the insured person
    - Number of days travelling
    - Destination continent
    
    Returns three tiers with different coverage levels and premiums.
    
    Args:
        request: Quotation request with policy details
        
    Returns:
        Quotation response with all three tiers and their premiums
    """
    logger.info(
        f"Generating quotation for policy: {request.policy_type}, "
        f"age: {request.age}, days: {request.days}, continent: {request.continent}"
    )
    
    try:
        # Validate policy type
        try:
            PolicyType(request.policy_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid policy type. Supported types: {[pt.value for pt in PolicyType]}"
            )
        
        # Validate continent
        try:
            Continent(request.continent)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid continent. Supported continents: {[c.value for c in Continent]}"
            )
        
        # Generate quotation
        quotation = QuotationEngine.generate_quotation(
            policy_type=request.policy_type,
            age=request.age,
            days=request.days,
            continent=request.continent
        )
        
        # Add calculation date
        quotation["calculation_date"] = datetime.utcnow().isoformat()
        
        # Convert to response model
        response = QuotationResponse(
            success=True,
            policy_type=quotation["policy_type"],
            age=quotation["age"],
            days=quotation["days"],
            continent=quotation["continent"],
            tiers=[
                TierQuotation(**tier) for tier in quotation["tiers"]
            ],
            calculation_date=quotation["calculation_date"]
        )
        
        logger.info(
            f"Quotation generated successfully. Premiums: "
            f"Basic={response.tiers[0].premium}, "
            f"Standard={response.tiers[1].premium}, "
            f"Premium={response.tiers[2].premium}"
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating quotation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/policies", response_model=List[str])
async def get_supported_policies():
    """
    Get list of supported policy types
    """
    return [pt.value for pt in PolicyType]


@app.get("/continents", response_model=List[str])
async def get_supported_continents():
    """
    Get list of supported continents
    """
    return [c.value for c in Continent]


@app.get("/tiers", response_model=List[str])
async def get_supported_tiers():
    """
    Get list of supported coverage tiers
    """
    return [t.value for t in Tier]


# ============================================================================
# Server Entry Point
# ============================================================================

if __name__ == "__main__":
    logger.info(f"Starting Quotation API Server on {SERVER_HOST}:{SERVER_PORT}")
    import uvicorn
    uvicorn.run(
        "quotation_api.server:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=True,
        log_level="info"
    )

