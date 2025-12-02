"""
FastAPI Server for Policy Eligibility Scanner
Exposes HTTP endpoints for scanning policy eligibility
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
import logging
import uvicorn

from .config import SERVER_HOST, SERVER_PORT, ALLOWED_ORIGINS, TAXONOMY_FILE_PATH
from .policy_analyzer import PolicyAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Policy Analyzer API",
    description="Comprehensive policy analysis tool for travel insurance products. Handles eligibility scanning, benefits analysis, exclusions, and policy grading.",
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

# Global analyzer instance
analyzer = None


# ============================================================================
# Request/Response Models
# ============================================================================

class EligibilityRequest(BaseModel):
    """Request model for eligibility scanning"""
    product: str = Field(..., description="Product name (e.g., 'Scootsurance', 'TravelEasy', 'TravelEasy Pre-Ex')")
    user_data: Dict[str, Any] = Field(..., description="User-provided data fields for eligibility checking")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product": "Scootsurance",
                "user_data": {
                    "departure_location": "Singapore",
                    "age": 35,
                    "purchase_timing": "before departure from Singapore"
                }
            }
        }


class ConditionResult(BaseModel):
    """Result for a single condition check"""
    condition: str
    eligible: bool
    reason: str
    original_text: Optional[str] = None
    parameters_checked: Optional[List[str]] = None


class SkippedCondition(BaseModel):
    """Information about a skipped condition"""
    condition: str
    reason: str
    original_text: Optional[str] = None


class EligibilityResponse(BaseModel):
    """Response model for eligibility scanning"""
    success: bool
    product: str
    eligible: bool
    conditions_checked: List[ConditionResult]
    conditions_skipped: List[SkippedCondition]
    errors: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "product": "Scootsurance",
                "eligible": True,
                "conditions_checked": [
                    {
                        "condition": "trip_start_singapore",
                        "eligible": True,
                        "reason": "Location requirements met",
                        "original_text": "Your trip must begin in Singapore.",
                        "parameters_checked": ["departure_location"]
                    }
                ],
                "conditions_skipped": [
                    {
                        "condition": "good_health",
                        "reason": "No parameters to check",
                        "original_text": "The insured persons must be in good health."
                    }
                ],
                "errors": []
            }
        }


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str
    version: str


# ============================================================================
# Startup and Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize analyzer on startup"""
    global analyzer
    logger.info("Initializing Policy Analyzer...")
    try:
        analyzer = PolicyAnalyzer(TAXONOMY_FILE_PATH)
        logger.info("Policy Analyzer initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize analyzer: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    global analyzer
    if analyzer:
        logger.info("Policy Analyzer shutdown")


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
        service="Policy Analyzer API",
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    """
    return HealthResponse(
        status="healthy",
        service="Policy Analyzer API",
        version="1.0.0"
    )


@app.post("/scan_policy_eligibility", response_model=EligibilityResponse)
async def scan_policy_eligibility(request: EligibilityRequest):
    """
    Scan policy eligibility for a given product and user data
    
    This endpoint:
    1. Filters layer_1_general_conditions by condition_type == "eligibility"
    2. For each condition, checks if parameters exist
    3. If parameters exist, performs rule-based checks against user data
    4. If no parameters, skips that condition
    
    Args:
        request: Eligibility request with product name and user data
        
    Returns:
        Eligibility results with checked and skipped conditions
    """
    global analyzer
    
    if not analyzer:
        raise HTTPException(status_code=503, detail="Policy Analyzer not initialized")
    
    logger.info(f"Scanning eligibility for product: {request.product}")
    
    try:
        # Call the scan function
        result = analyzer.scan_policy_eligibility(
            product=request.product,
            user_data=request.user_data
        )
        
        # Convert to response model
        response = EligibilityResponse(
            success=True,
            product=result['product'],
            eligible=result['eligible'],
            conditions_checked=[
                ConditionResult(**cond) for cond in result['conditions_checked']
            ],
            conditions_skipped=[
                SkippedCondition(**cond) for cond in result['conditions_skipped']
            ],
            errors=result.get('errors', [])
        )
        
        logger.info(f"Eligibility scan completed: eligible={result['eligible']}, "
                   f"checked={len(result['conditions_checked'])}, "
                   f"skipped={len(result['conditions_skipped'])}")
        
        return response
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error scanning eligibility: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/products", response_model=List[str])
async def get_products():
    """
    Get list of available products from taxonomy
    """
    global analyzer
    
    if not analyzer:
        raise HTTPException(status_code=503, detail="Policy Analyzer not initialized")
    
    try:
        products = analyzer.taxonomy_data.get('products', [])
        return products
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/eligibility_conditions", response_model=List[Dict[str, Any]])
async def get_eligibility_conditions():
    """
    Get list of eligibility conditions from layer_1_general_conditions
    """
    global analyzer
    
    if not analyzer:
        raise HTTPException(status_code=503, detail="Policy Analyzer not initialized")
    
    try:
        layer_1_conditions = analyzer.taxonomy_data.get('layers', {}).get('layer_1_general_conditions', [])
        eligibility_conditions = [
            {
                'condition': cond.get('condition'),
                'condition_type': cond.get('condition_type'),
                'products': list(cond.get('products', {}).keys())
            }
            for cond in layer_1_conditions
            if cond.get('condition_type') == 'eligibility'
        ]
        return eligibility_conditions
    except Exception as e:
        logger.error(f"Error getting eligibility conditions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/show_policy_benefits", response_model=Dict[str, List[str]])
@app.get("/show_policy_benefits/{product}", response_model=Dict[str, List[str]])
async def show_policy_benefits(product: Optional[str] = None):
    """
    Show policy benefits for a specific product or all products
    
    Returns the exact benefit_name for each product from layer_2_benefits
    where condition_exist is true.
    
    Args:
        product: Optional product name (e.g., "Scootsurance", "TravelEasy", "TravelEasy Pre-Ex")
                 If not provided, returns benefits for all products
    
    Returns:
        Dictionary with product names as keys and lists of benefit names as values
    """
    global analyzer
    
    if not analyzer:
        raise HTTPException(status_code=503, detail="Policy Analyzer not initialized")
    
    try:
        result = analyzer.show_policy_benefits(product=product)
        logger.info(f"Retrieved benefits for product(s): {list(result.keys())}")
        return result
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting policy benefits: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


class BenefitDetailsRequest(BaseModel):
    """Request model for benefit details"""
    product: str = Field(..., description="Product name (e.g., 'Scootsurance', 'TravelEasy', 'TravelEasy Pre-Ex')")
    benefit_name: str = Field(..., description="Benefit name (must match exactly with layer_2_benefits benefit_name)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product": "Scootsurance",
                "benefit_name": "accidental_death_permanent_disablement"
            }
        }


class BenefitDetailsResponse(BaseModel):
    """Response model for benefit details"""
    success: bool
    product: str
    benefit_name: str
    layer_2_details: Dict[str, Any]
    layer_3_eligibility: List[Dict[str, Any]]
    layer_3_exclusion: List[Dict[str, Any]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "product": "Scootsurance",
                "benefit_name": "accidental_death_permanent_disablement",
                "layer_2_details": {
                    "benefit_name": "accidental_death_permanent_disablement",
                    "condition_exist": True,
                    "parameters": {
                        "coverage_limit": {
                            "12_to_69_years": "$100,000",
                            "70_to_74_years": "$50,000",
                            "below_12_years": "$10,000"
                        }
                    }
                },
                "layer_3_eligibility": [
                    {
                        "condition": "injury_time_limit_for_compensation",
                        "condition_type": "benefit_eligibility",
                        "condition_exist": True,
                        "original_text": "Death within ninety (90) days from the date of Accident...",
                        "parameters": {
                            "death_time_limit": 90,
                            "permanent_disablement_time_limit": 180,
                            "unit": "days"
                        }
                    }
                ],
                "layer_3_exclusion": [
                    {
                        "condition": "loss_by_illness",
                        "condition_type": "benefit_exclusion",
                        "condition_exist": True,
                        "original_text": "In addition to the General Exclusions...",
                        "parameters": {}
                    }
                ]
            }
        }


@app.post("/show_policy_benefit_details", response_model=BenefitDetailsResponse)
async def show_policy_benefit_details(request: BenefitDetailsRequest):
    """
    Show detailed information for a specific policy benefit
    
    Returns:
    - Layer 2 details: Benefit information from layer_2_benefits
    - Layer 3 eligibility: List of benefit_eligibility conditions for the benefit
    - Layer 3 exclusion: List of benefit_exclusion conditions for the benefit
    
    The benefit_name in layer 3 must match the benefit_name in layer 2 for correct extraction.
    
    Args:
        request: Benefit details request with product name and benefit name
        
    Returns:
        Detailed benefit information including layer 2 and layer 3 data
    """
    global analyzer
    
    if not analyzer:
        raise HTTPException(status_code=503, detail="Policy Analyzer not initialized")
    
    logger.info(f"Retrieving benefit details for product: {request.product}, benefit: {request.benefit_name}")
    
    try:
        result = analyzer.show_policy_benefit_details(
            product=request.product,
            benefit_name=request.benefit_name
        )
        
        response = BenefitDetailsResponse(
            success=True,
            product=result['product'],
            benefit_name=result['benefit_name'],
            layer_2_details=result['layer_2_details'],
            layer_3_eligibility=result['layer_3_eligibility'],
            layer_3_exclusion=result['layer_3_exclusion']
        )
        
        logger.info(f"Retrieved benefit details: {len(result['layer_3_eligibility'])} eligibility, "
                   f"{len(result['layer_3_exclusion'])} exclusion conditions")
        
        return response
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error getting benefit details: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


class ExclusionResponse(BaseModel):
    """Response model for policy exclusions"""
    success: bool
    product: str
    exclusions: List[Dict[str, Any]]
    total_count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "product": "Scootsurance",
                "exclusions": [
                    {
                        "condition": "pre_existing_conditions",
                        "condition_type": "exclusion",
                        "original_text": "Pre-Existing Medical Condition Any Injury or Illness which: (a) You have received medical treatment, diagnosis, consultation, or prescribed drugs within 365 days prior to Your trip...",
                        "parameters": {
                            "lookback_period": 365,
                            "unit": "days"
                        }
                    },
                    {
                        "condition": "travel_advisory_exclusion",
                        "condition_type": "exclusion",
                        "original_text": "Your travel to a country, specific area or event when the government in Singapore or destination country has issued travel advisory against travelling to or to defer non-essential travel to the planned destination",
                        "parameters": {}
                    }
                ],
                "total_count": 2
            }
        }


@app.get("/show_policy_exclusion/{product}", response_model=ExclusionResponse)
async def show_policy_exclusion(product: str):
    """
    Show list of exclusions in layer 1 for a specific policy
    
    Returns all exclusions from layer_1_general_conditions where:
    - condition_type == "exclusion"
    - condition_exist == true for the specified product
    
    Args:
        product: Product name (e.g., "Scootsurance", "TravelEasy", "TravelEasy Pre-Ex")
    
    Returns:
        List of exclusions with their details (condition name, original text, parameters)
    """
    global analyzer
    
    if not analyzer:
        raise HTTPException(status_code=503, detail="Policy Analyzer not initialized")
    
    logger.info(f"Retrieving exclusions for product: {product}")
    
    try:
        result = analyzer.show_policy_exclusion(product=product)
        
        response = ExclusionResponse(
            success=True,
            product=result['product'],
            exclusions=result['exclusions'],
            total_count=result['total_count']
        )
        
        logger.info(f"Retrieved {result['total_count']} exclusions for product: {product}")
        
        return response
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error getting policy exclusions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


class ExclusionDetailsRequest(BaseModel):
    """Request model for exclusion details"""
    product: str = Field(..., description="Product name (e.g., 'Scootsurance', 'TravelEasy', 'TravelEasy Pre-Ex')")
    condition: str = Field(..., description="Exclusion condition name (e.g., 'pre_existing_conditions', 'travel_advisory_exclusion')")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product": "Scootsurance",
                "condition": "pre_existing_conditions"
            }
        }


class ExclusionDetailsResponse(BaseModel):
    """Response model for exclusion details"""
    success: bool
    product: str
    condition: str
    exclusion_details: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "product": "Scootsurance",
                "condition": "pre_existing_conditions",
                "exclusion_details": {
                    "condition": "pre_existing_conditions",
                    "condition_type": "exclusion",
                    "condition_exist": True,
                    "original_text": "Pre-Existing Medical Condition Any Injury or Illness which: (a) You have received medical treatment, diagnosis, consultation, or prescribed drugs within 365 days prior to Your trip...",
                    "parameters": {
                        "lookback_period": 365,
                        "unit": "days"
                    }
                }
            }
        }


@app.post("/show_policy_exclusion_details", response_model=ExclusionDetailsResponse)
async def show_policy_exclusion_details(request: ExclusionDetailsRequest):
    """
    Show detailed information for a specific exclusion condition
    
    Returns exclusion details from layer_1_general_conditions for the specified
    product and condition where condition_type == "exclusion".
    
    Args:
        request: Exclusion details request with product name and condition name
        
    Returns:
        Detailed exclusion information including original text and parameters
    """
    global analyzer
    
    if not analyzer:
        raise HTTPException(status_code=503, detail="Policy Analyzer not initialized")
    
    logger.info(f"Retrieving exclusion details for product: {request.product}, condition: {request.condition}")
    
    try:
        result = analyzer.show_policy_exclusion_details(
            product=request.product,
            condition=request.condition
        )
        
        response = ExclusionDetailsResponse(
            success=True,
            product=result['product'],
            condition=result['condition'],
            exclusion_details=result['exclusion_details']
        )
        
        logger.info(f"Retrieved exclusion details for condition: {request.condition}")
        
        return response
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error getting exclusion details: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


class PrioritizedBenefit(BaseModel):
    """Model for a prioritized benefit"""
    benefit_name: str = Field(..., description="Name of the benefit")
    priority: Optional[int] = Field(None, description="Priority rank (1 = highest, defaults to order in list)")
    priority_score: Optional[float] = Field(None, ge=0, le=100, description="Explicit priority score (0-100, overrides priority)")


class GradePolicyRequest(BaseModel):
    """Request model for policy grading"""
    prioritized_benefits: List[Union[str, PrioritizedBenefit]] = Field(
        ..., 
        description="List of prioritized benefits. Can be simple strings (order = priority) or objects with benefit_name, priority, and optional priority_score"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "prioritized_benefits": [
                    {
                        "benefit_name": "accidental_death_permanent_disablement",
                        "priority": 1
                    },
                    {
                        "benefit_name": "funeral_expenses_accidental_death",
                        "priority": 2
                    },
                    "child_education_grant",
                    "family_assistance"
                ]
            }
        }


class GradePolicyResponse(BaseModel):
    """Response model for policy grading"""
    success: bool
    policy_scores: Dict[str, float]
    percentage_scores: Dict[str, float]
    rankings: List[str]
    detailed_scores: Dict[str, Dict[str, Any]]
    prioritized_benefits: List[Dict[str, Any]]
    max_possible_score: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "policy_scores": {
                    "Scootsurance": 55.0,
                    "TravelEasy": 45.0,
                    "TravelEasy Pre-Ex": 50.0
                },
                "percentage_scores": {
                    "Scootsurance": 78.6,
                    "TravelEasy": 64.3,
                    "TravelEasy Pre-Ex": 71.4
                },
                "rankings": ["Scootsurance", "TravelEasy Pre-Ex", "TravelEasy"],
                "detailed_scores": {
                    "Scootsurance": {
                        "accidental_death_permanent_disablement": {
                            "points": 30.0,
                            "priority": 1,
                            "covered": True
                        }
                    }
                },
                "prioritized_benefits": [
                    {
                        "benefit_name": "accidental_death_permanent_disablement",
                        "priority": 1,
                        "score": 30.0
                    }
                ],
                "max_possible_score": 70.0
            }
        }


@app.post("/grade_policy", response_model=GradePolicyResponse)
async def grade_policy(request: GradePolicyRequest):
    """
    Grade policies based on prioritized benefits using a point system
    
    Scoring System:
    - Base points per benefit: 10 points
    - Priority multipliers:
      - Priority 1 (highest): 3.0x = 30 points
      - Priority 2: 2.5x = 25 points
      - Priority 3: 2.0x = 20 points
      - Priority 4: 1.5x = 15 points
      - Priority 5+: 1.0x = 10 points
    - Bonus: +5 points if policy covers all top 3 prioritized benefits
    - If explicit priority_score is provided (0-100), it overrides priority-based scoring
    
    Args:
        request: Grade policy request with list of prioritized benefits
        
    Returns:
        Policy scores, rankings, and detailed breakdown for all policies
    """
    global analyzer
    
    if not analyzer:
        raise HTTPException(status_code=503, detail="Policy Analyzer not initialized")
    
    logger.info(f"Grading policies based on {len(request.prioritized_benefits)} prioritized benefits")
    
    try:
        # Convert request to format expected by scanner
        prioritized_benefits_list = []
        for item in request.prioritized_benefits:
            if isinstance(item, str):
                prioritized_benefits_list.append(item)
            else:
                prioritized_benefits_list.append({
                    'benefit_name': item.benefit_name,
                    'priority': item.priority,
                    'priority_score': item.priority_score
                })
        
        result = analyzer.grade_policy(prioritized_benefits=prioritized_benefits_list)
        
        response = GradePolicyResponse(
            success=True,
            policy_scores=result['policy_scores'],
            percentage_scores=result['percentage_scores'],
            rankings=result['rankings'],
            detailed_scores=result['detailed_scores'],
            prioritized_benefits=result['prioritized_benefits'],
            max_possible_score=result['max_possible_score']
        )
        
        logger.info(f"Policy grading completed. Top policy: {result['rankings'][0] if result['rankings'] else 'N/A'}")
        
        return response
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error grading policies: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# ============================================================================
# Server Entry Point
# ============================================================================

if __name__ == "__main__":
    logger.info(f"Starting Policy Analyzer Server on {SERVER_HOST}:{SERVER_PORT}")
    uvicorn.run(
        "policy_eligibility_scanner.server:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=True,
        log_level="info"
    )

