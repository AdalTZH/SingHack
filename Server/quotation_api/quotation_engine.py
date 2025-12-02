"""
Quotation Engine
Calculates insurance premiums for different policy types and tiers
"""
from typing import Dict, List
from enum import Enum


class PolicyType(str, Enum):
    """Supported policy types"""
    SCOOTSURANCE = "Scootsurance"
    TRAVELEASY = "TravelEasy"
    TRAVELEASY_PRE_EX = "TravelEasy Pre-Ex"


class Tier(str, Enum):
    """Insurance coverage tiers"""
    BASIC = "Basic"
    STANDARD = "Standard"
    PREMIUM = "Premium"


class Continent(str, Enum):
    """Supported continents for travel insurance"""
    ASIA = "Asia"
    EUROPE = "Europe"
    NORTH_AMERICA = "North America"
    SOUTH_AMERICA = "South America"
    AFRICA = "Africa"
    OCEANIA = "Oceania"
    ANTARCTICA = "Antarctica"


class QuotationEngine:
    """
    Engine for calculating insurance policy quotations
    
    Premium calculation factors:
    - Base premium by policy type
    - Age multiplier (risk increases with age)
    - Days multiplier (longer trips = higher risk)
    - Continent multiplier (risk varies by destination)
    - Tier multiplier (coverage level)
    """
    
    # Base premiums per policy type (in SGD)
    BASE_PREMIUMS = {
        PolicyType.SCOOTSURANCE: 50.0,
        PolicyType.TRAVELEASY: 60.0,
        PolicyType.TRAVELEASY_PRE_EX: 80.0,  # Higher base for pre-existing conditions
    }
    
    # Tier multipliers
    TIER_MULTIPLIERS = {
        Tier.BASIC: 1.0,
        Tier.STANDARD: 1.5,
        Tier.PREMIUM: 2.0,
    }
    
    # Age multipliers (risk increases with age)
    AGE_MULTIPLIERS = {
        (0, 17): 0.8,      # Children/Teens
        (18, 30): 1.0,     # Young adults
        (31, 50): 1.2,     # Middle-aged
        (51, 65): 1.5,     # Seniors
        (66, 75): 2.0,     # Elderly
        (76, 100): 2.5,    # Very elderly
    }
    
    # Days multiplier (per day rate)
    DAYS_BASE_RATE = 1.0
    DAYS_MULTIPLIER = 0.05  # 5% increase per day
    
    # Continent risk multipliers
    CONTINENT_MULTIPLIERS = {
        Continent.ASIA: 1.0,           # Base risk
        Continent.EUROPE: 1.1,         # Slightly higher
        Continent.NORTH_AMERICA: 1.15, # Moderate risk
        Continent.SOUTH_AMERICA: 1.3,  # Higher risk
        Continent.AFRICA: 1.4,         # Higher risk
        Continent.OCEANIA: 1.05,       # Slightly higher
        Continent.ANTARCTICA: 1.8,    # Very high risk
    }
    
    @staticmethod
    def get_age_multiplier(age: int) -> float:
        """Get age-based risk multiplier"""
        for (min_age, max_age), multiplier in QuotationEngine.AGE_MULTIPLIERS.items():
            if min_age <= age <= max_age:
                return multiplier
        # Default for ages outside range
        return 2.5
    
    @staticmethod
    def get_days_multiplier(days: int) -> float:
        """Calculate days-based multiplier"""
        if days <= 0:
            return 1.0
        # Base rate + (days * daily rate)
        return QuotationEngine.DAYS_BASE_RATE + (days * QuotationEngine.DAYS_MULTIPLIER)
    
    @staticmethod
    def get_continent_multiplier(continent: str) -> float:
        """Get continent-based risk multiplier"""
        try:
            continent_enum = Continent(continent)
            return QuotationEngine.CONTINENT_MULTIPLIERS.get(continent_enum, 1.0)
        except ValueError:
            # Unknown continent, use base multiplier
            return 1.0
    
    @staticmethod
    def calculate_premium(
        policy_type: str,
        age: int,
        days: int,
        continent: str,
        tier: Tier
    ) -> float:
        """
        Calculate premium for a given policy configuration
        
        Args:
            policy_type: Policy type (Scootsurance, TravelEasy, TravelEasy Pre-Ex)
            age: Age of the insured person
            days: Number of days travelling
            continent: Destination continent
            tier: Coverage tier (Basic, Standard, Premium)
            
        Returns:
            Calculated premium in SGD
        """
        # Get base premium
        try:
            policy_enum = PolicyType(policy_type)
            base_premium = QuotationEngine.BASE_PREMIUMS[policy_enum]
        except ValueError:
            # Unknown policy type, use average
            base_premium = 65.0
        
        # Get multipliers
        age_mult = QuotationEngine.get_age_multiplier(age)
        days_mult = QuotationEngine.get_days_multiplier(days)
        continent_mult = QuotationEngine.get_continent_multiplier(continent)
        tier_mult = QuotationEngine.TIER_MULTIPLIERS[tier]
        
        # Calculate premium
        premium = base_premium * age_mult * days_mult * continent_mult * tier_mult
        
        # Round to 2 decimal places
        return round(premium, 2)
    
    @staticmethod
    def generate_quotation(
        policy_type: str,
        age: int,
        days: int,
        continent: str
    ) -> Dict[str, any]:
        """
        Generate quotation with all three tiers for a policy
        
        Args:
            policy_type: Policy type
            age: Age of insured person
            days: Number of days travelling
            continent: Destination continent
            
        Returns:
            Dictionary with quotation details including all three tiers
        """
        tiers = [Tier.BASIC, Tier.STANDARD, Tier.PREMIUM]
        
        quotation_tiers = []
        for tier in tiers:
            premium = QuotationEngine.calculate_premium(
                policy_type=policy_type,
                age=age,
                days=days,
                continent=continent,
                tier=tier
            )
            
            # Determine coverage features based on tier
            coverage_features = QuotationEngine._get_coverage_features(tier)
            
            quotation_tiers.append({
                "tier": tier.value,
                "premium": premium,
                "currency": "SGD",
                "coverage_features": coverage_features,
                "description": QuotationEngine._get_tier_description(tier)
            })
        
        return {
            "policy_type": policy_type,
            "age": age,
            "days": days,
            "continent": continent,
            "tiers": quotation_tiers,
            "calculation_date": None  # Will be set by server
        }
    
    @staticmethod
    def _get_coverage_features(tier: Tier) -> List[str]:
        """Get coverage features for each tier"""
        features = {
            Tier.BASIC: [
                "Medical expenses coverage",
                "Trip cancellation",
                "Baggage loss",
                "Basic emergency assistance"
            ],
            Tier.STANDARD: [
                "All Basic features",
                "Higher medical coverage limits",
                "Trip delay coverage",
                "Personal accident coverage",
                "24/7 emergency assistance"
            ],
            Tier.PREMIUM: [
                "All Standard features",
                "Maximum coverage limits",
                "Adventure sports coverage",
                "Pre-existing conditions (where applicable)",
                "Premium concierge services",
                "Extended coverage periods"
            ]
        }
        return features.get(tier, [])
    
    @staticmethod
    def _get_tier_description(tier: Tier) -> str:
        """Get description for each tier"""
        descriptions = {
            Tier.BASIC: "Essential coverage for basic travel protection",
            Tier.STANDARD: "Comprehensive coverage with enhanced benefits",
            Tier.PREMIUM: "Maximum protection with premium services and highest limits"
        }
        return descriptions.get(tier, "")

