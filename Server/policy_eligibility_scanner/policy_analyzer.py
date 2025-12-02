"""
Policy Analyzer
Comprehensive policy analysis tool for travel insurance products.
Handles eligibility scanning, benefits analysis, exclusions, and policy grading.
"""
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PolicyAnalyzer:
    """
    Comprehensive policy analyzer for travel insurance products.
    
    Provides functionality for:
    - Eligibility scanning and validation
    - Benefits listing and detailed analysis
    - Exclusions listing and detailed analysis
    - Policy grading and comparison based on prioritized benefits
    """
    
    def __init__(self, taxonomy_file_path: str):
        """
        Initialize the scanner with taxonomy file
        
        Args:
            taxonomy_file_path: Path to Taxonomy_Hackathon.json file
        """
        self.taxonomy_file_path = taxonomy_file_path
        self.taxonomy_data = None
        self._load_taxonomy()
    
    def _load_taxonomy(self):
        """Load taxonomy data from JSON file"""
        try:
            with open(self.taxonomy_file_path, 'r', encoding='utf-8') as f:
                self.taxonomy_data = json.load(f)
            logger.info(f"Taxonomy loaded successfully from {self.taxonomy_file_path}")
        except FileNotFoundError:
            logger.error(f"Taxonomy file not found: {self.taxonomy_file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing taxonomy JSON: {e}")
            raise
    
    def _has_parameters(self, parameters: Any) -> bool:
        """
        Check if parameters exist and are not empty
        
        Args:
            parameters: Parameters object (dict, list, or None)
            
        Returns:
            True if parameters exist and are not empty
        """
        if parameters is None:
            return False
        if isinstance(parameters, dict):
            return len(parameters) > 0
        if isinstance(parameters, list):
            return len(parameters) > 0
        return False
    
    def _check_location_condition(self, condition_params: Dict[str, Any], 
                                   user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check location-based conditions (departure_location, return_location)
        
        Args:
            condition_params: Condition parameters from taxonomy
            user_data: User-provided data
            
        Returns:
            Tuple of (is_eligible, reason)
        """
        if 'departure_location' in condition_params:
            required_departure = condition_params['departure_location']
            user_departure = user_data.get('departure_location', '').strip()
            
            if not user_departure:
                return False, f"Missing required field: departure_location"
            
            if user_departure.lower() != required_departure.lower():
                return False, f"Departure location '{user_departure}' does not match required '{required_departure}'"
        
        if 'return_location' in condition_params:
            required_return = condition_params['return_location']
            user_return = user_data.get('return_location', '').strip()
            
            if not user_return:
                return False, f"Missing required field: return_location"
            
            if user_return.lower() != required_return.lower():
                return False, f"Return location '{user_return}' does not match required '{required_return}'"
        
        return True, "Location requirements met"
    
    def _check_age_condition(self, condition_params: Dict[str, Any], 
                             user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check age-based eligibility conditions
        
        Args:
            condition_params: Condition parameters from taxonomy
            user_data: User-provided data
            
        Returns:
            Tuple of (is_eligible, reason)
        """
        age = user_data.get('age')
        if age is None:
            return False, "Missing required field: age"
        
        try:
            age = float(age)
        except (ValueError, TypeError):
            return False, f"Invalid age value: {age}"
        
        # Check minimum_age and maximum_age (Scootsurance pattern)
        if 'minimum_age' in condition_params and 'maximum_age' in condition_params:
            min_age = condition_params['minimum_age']
            max_age = condition_params['maximum_age']
            unit_min = condition_params.get('unit_min', 'years')
            unit_max = condition_params.get('unit_max', 'years')
            
            # Convert months to years for comparison (approximate)
            if unit_min == 'months':
                min_age_years = min_age / 12.0
            else:
                min_age_years = min_age
            
            if age < min_age_years:
                return False, f"Age {age} is below minimum age requirement of {min_age} {unit_min}"
            
            if age > max_age:
                return False, f"Age {age} exceeds maximum age requirement of {max_age} {unit_max}"
            
            return True, f"Age {age} meets requirements ({min_age} {unit_min} to {max_age} {unit_max})"
        
        # Check TravelEasy pattern with both single trip and annual plan parameters
        # The taxonomy has both parameters, and trip_type determines which one to check
        has_single_trip = 'maximum_age_single_trip_eligibility' in condition_params
        has_annual_plan = 'maximum_age_annual_plan_purchase' in condition_params
        
        if has_single_trip or has_annual_plan:
            trip_type = user_data.get('trip_type', 'single').lower()
            unit = condition_params.get('unit', 'years')
            
            # If both parameters exist, use trip_type to determine which to check
            if has_single_trip and has_annual_plan:
                if trip_type == 'annual':
                    max_age = condition_params['maximum_age_annual_plan_purchase']
                    if age > max_age:
                        return False, f"Age {age} exceeds maximum age for annual plan purchase ({max_age} {unit})"
                    return True, f"Age {age} meets annual plan purchase requirements (up to {max_age} {unit})"
                else:
                    # Default to single trip if trip_type is not 'annual'
                    max_age = condition_params['maximum_age_single_trip_eligibility']
                    if age > max_age:
                        return False, f"Age {age} exceeds maximum age for single trip eligibility ({max_age} {unit})"
                    return True, f"Age {age} meets single trip eligibility requirements (up to {max_age} {unit})"
            elif has_single_trip:
                # Only single trip parameter exists
                max_age = condition_params['maximum_age_single_trip_eligibility']
                if age > max_age:
                    return False, f"Age {age} exceeds maximum age for single trip eligibility ({max_age} {unit})"
                return True, f"Age {age} meets single trip eligibility requirements (up to {max_age} {unit})"
            elif has_annual_plan:
                # Only annual plan parameter exists
                max_age = condition_params['maximum_age_annual_plan_purchase']
                if age > max_age:
                    return False, f"Age {age} exceeds maximum age for annual plan purchase ({max_age} {unit})"
                return True, f"Age {age} meets annual plan purchase requirements (up to {max_age} {unit})"
        
        return True, "Age requirements met"
    
    def _check_age_threshold_condition(self, condition_params: Dict[str, Any], 
                                       user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check age threshold conditions (e.g., child accompaniment)
        
        Args:
            condition_params: Condition parameters from taxonomy
            user_data: User-provided data
            
        Returns:
            Tuple of (is_eligible, reason)
        """
        if 'age_threshold_years_for_accompaniment' in condition_params:
            threshold = condition_params['age_threshold_years_for_accompaniment']
            child_age = user_data.get('child_age')
            is_accompanied = user_data.get('is_accompanied', False)
            
            if child_age is None:
                # If no child age provided, skip this check
                return True, "No child age provided, skipping accompaniment check"
            
            try:
                child_age = float(child_age)
            except (ValueError, TypeError):
                return False, f"Invalid child age value: {child_age}"
            
            if child_age < threshold:
                if not is_accompanied:
                    return False, f"Child age {child_age} is below threshold {threshold} years and must be accompanied"
                return True, f"Child age {child_age} is below threshold {threshold} years and is accompanied"
            
            return True, f"Child age {child_age} meets threshold requirement ({threshold} years)"
        
        return True, "Age threshold requirements met"
    
    def _check_timing_condition(self, condition_params: Dict[str, Any], 
                                user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check timing-based conditions (e.g., purchase_timing)
        
        Args:
            condition_params: Condition parameters from taxonomy
            user_data: User-provided data
            
        Returns:
            Tuple of (is_eligible, reason)
        """
        if 'purchase_timing' in condition_params:
            required_timing = condition_params['purchase_timing']
            purchase_timing = user_data.get('purchase_timing', '').strip()
            
            if not purchase_timing:
                return False, "Missing required field: purchase_timing"
            
            # Check if purchase timing matches requirement
            if 'before departure' in required_timing.lower():
                if 'before' not in purchase_timing.lower() and 'prior' not in purchase_timing.lower():
                    return False, f"Purchase timing '{purchase_timing}' does not meet requirement: {required_timing}"
            
            return True, f"Purchase timing '{purchase_timing}' meets requirement: {required_timing}"
        
        return True, "Timing requirements met"
    
    def _check_condition_parameters(self, condition_name: str, 
                                    condition_params: Dict[str, Any], 
                                    user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Perform rule-based check on condition parameters
        
        Args:
            condition_name: Name of the condition
            condition_params: Parameters for the condition
            user_data: User-provided data
            
        Returns:
            Tuple of (is_eligible, reason)
        """
        # Route to appropriate checker based on condition type
        if condition_name == 'trip_start_singapore':
            return self._check_location_condition(condition_params, user_data)
        
        elif condition_name == 'age_eligibility':
            return self._check_age_condition(condition_params, user_data)
        
        elif condition_name == 'child_accompaniment_requirement':
            return self._check_age_threshold_condition(condition_params, user_data)
        
        elif condition_name == 'pre_trip_purchased':
            return self._check_timing_condition(condition_params, user_data)
        
        # Generic parameter matching for other conditions
        else:
            # Try to match parameters directly
            for param_key, param_value in condition_params.items():
                user_value = user_data.get(param_key)
                if user_value is None:
                    return False, f"Missing required field: {param_key}"
                
                # Simple equality check
                if str(user_value).lower() != str(param_value).lower():
                    return False, f"Parameter '{param_key}' value '{user_value}' does not match required '{param_value}'"
            
            return True, "All parameter requirements met"
    
    def scan_policy_eligibility(self, product: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scan policy eligibility for a given product and user data
        
        This function:
        1. Filters layer_1_general_conditions by condition_type == "eligibility"
        2. For each condition, checks if parameters exist
        3. If parameters exist, performs rule-based checks
        4. If no parameters, skips that condition
        
        Args:
            product: Product name (e.g., "Scootsurance", "TravelEasy", "TravelEasy Pre-Ex")
            user_data: Dictionary containing user-provided data fields
            
        Returns:
            Dictionary containing eligibility results for each condition
        """
        if not self.taxonomy_data:
            raise ValueError("Taxonomy data not loaded")
        
        # Get layer 1 general conditions
        layer_1_conditions = self.taxonomy_data.get('layers', {}).get('layer_1_general_conditions', [])
        
        # Filter by condition_type == "eligibility"
        eligibility_conditions = [
            cond for cond in layer_1_conditions 
            if cond.get('condition_type') == 'eligibility'
        ]
        
        results = {
            'product': product,
            'eligible': True,
            'conditions_checked': [],
            'conditions_skipped': [],
            'errors': []
        }
        
        for condition in eligibility_conditions:
            condition_name = condition.get('condition')
            
            # Skip child accompaniment requirement
            if condition_name == 'child_accompaniment_requirement':
                results['conditions_skipped'].append({
                    'condition': condition_name,
                    'reason': "Child accompaniment condition is skipped",
                    'original_text': condition.get('products', {}).get(product, {}).get('original_text', '')
                })
                continue
            
            products = condition.get('products', {})
            
            # Get product-specific condition data
            product_condition = products.get(product)
            if not product_condition:
                results['conditions_skipped'].append({
                    'condition': condition_name,
                    'reason': f"Condition not applicable to product '{product}'"
                })
                continue
            
            # Check if condition exists for this product
            if not product_condition.get('condition_exist', False):
                results['conditions_skipped'].append({
                    'condition': condition_name,
                    'reason': "Condition does not exist for this product"
                })
                continue
            
            # Get parameters
            parameters = product_condition.get('parameters', {})
            
            # Check if parameters exist and are not empty
            if not self._has_parameters(parameters):
                # Skip condition if no parameters
                results['conditions_skipped'].append({
                    'condition': condition_name,
                    'reason': "No parameters to check",
                    'original_text': product_condition.get('original_text', '')
                })
                continue
            
            # Perform rule-based check
            try:
                is_eligible, reason = self._check_condition_parameters(
                    condition_name, 
                    parameters, 
                    user_data
                )
                
                condition_result = {
                    'condition': condition_name,
                    'eligible': is_eligible,
                    'reason': reason,
                    'original_text': product_condition.get('original_text', ''),
                    'parameters_checked': list(parameters.keys())
                }
                
                results['conditions_checked'].append(condition_result)
                
                # If any condition fails, overall eligibility is False
                if not is_eligible:
                    results['eligible'] = False
                    
            except Exception as e:
                error_msg = f"Error checking condition '{condition_name}': {str(e)}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                results['conditions_checked'].append({
                    'condition': condition_name,
                    'eligible': False,
                    'reason': error_msg,
                    'original_text': product_condition.get('original_text', '')
                })
                results['eligible'] = False
        
        return results
    
    def show_policy_benefits(self, product: Optional[str] = None) -> Dict[str, Any]:
        """
        Show policy benefits for a specific product or all products
        
        This function:
        1. Retrieves layer_2_benefits from taxonomy
        2. Filters benefits where condition_exist is true for the product(s)
        3. Returns the exact benefit_name for each product
        
        Args:
            product: Product name (e.g., "Scootsurance", "TravelEasy", "TravelEasy Pre-Ex")
                     If None, returns benefits for all products
        
        Returns:
            Dictionary containing benefits for each product
        """
        if not self.taxonomy_data:
            raise ValueError("Taxonomy data not loaded")
        
        # Get layer 2 benefits
        layer_2_benefits = self.taxonomy_data.get('layers', {}).get('layer_2_benefits', [])
        
        # Get available products
        available_products = self.taxonomy_data.get('products', [])
        
        # If product is specified, validate it
        if product:
            if product not in available_products:
                raise ValueError(f"Product '{product}' not found. Available products: {available_products}")
            products_to_process = [product]
        else:
            products_to_process = available_products
        
        results = {}
        
        for product_name in products_to_process:
            product_benefits = []
            
            for benefit in layer_2_benefits:
                benefit_name = benefit.get('benefit_name')
                products = benefit.get('products', {})
                
                # Get product-specific benefit data
                product_benefit = products.get(product_name)
                if not product_benefit:
                    continue
                
                # Check if benefit exists for this product
                if product_benefit.get('condition_exist', False):
                    product_benefits.append(benefit_name)
            
            results[product_name] = product_benefits
        
        return results
    
    def show_policy_benefit_details(self, product: str, benefit_name: str) -> Dict[str, Any]:
        """
        Show detailed information for a specific policy benefit
        
        This function:
        1. Retrieves layer_2_benefits details for the specific policy and benefit
        2. Retrieves layer_3_benefit_specific_conditions for the benefit (eligibility and exclusion)
        3. Returns all details for the specific policy
        
        Args:
            product: Product name (e.g., "Scootsurance", "TravelEasy", "TravelEasy Pre-Ex")
            benefit_name: Benefit name (must match exactly with layer_2_benefits benefit_name)
        
        Returns:
            Dictionary containing:
            - layer_2_details: Benefit details from layer_2_benefits
            - layer_3_eligibility: List of benefit_eligibility conditions
            - layer_3_exclusion: List of benefit_exclusion conditions
        """
        if not self.taxonomy_data:
            raise ValueError("Taxonomy data not loaded")
        
        # Validate product
        available_products = self.taxonomy_data.get('products', [])
        if product not in available_products:
            raise ValueError(f"Product '{product}' not found. Available products: {available_products}")
        
        # Get layer 2 benefits
        layer_2_benefits = self.taxonomy_data.get('layers', {}).get('layer_2_benefits', [])
        
        # Find the benefit in layer 2
        layer_2_benefit = None
        for benefit in layer_2_benefits:
            if benefit.get('benefit_name') == benefit_name:
                layer_2_benefit = benefit
                break
        
        if not layer_2_benefit:
            available_benefits = [b.get('benefit_name') for b in layer_2_benefits]
            raise ValueError(f"Benefit '{benefit_name}' not found in layer_2_benefits. Available benefits: {available_benefits}")
        
        # Get product-specific layer 2 details
        products = layer_2_benefit.get('products', {})
        product_benefit = products.get(product)
        
        if not product_benefit:
            raise ValueError(f"Benefit '{benefit_name}' not available for product '{product}'")
        
        if not product_benefit.get('condition_exist', False):
            raise ValueError(f"Benefit '{benefit_name}' does not exist (condition_exist: false) for product '{product}'")
        
        layer_2_details = {
            'benefit_name': benefit_name,
            'condition_exist': product_benefit.get('condition_exist', False),
            'parameters': product_benefit.get('parameters', {})
        }
        
        # Get layer 3 benefit-specific conditions
        layer_3_conditions = self.taxonomy_data.get('layers', {}).get('layer_3_benefit_specific_conditions', [])
        
        # Filter layer 3 conditions by benefit_name (must match exactly)
        benefit_specific_conditions = [
            cond for cond in layer_3_conditions
            if cond.get('benefit_name') == benefit_name
        ]
        
        # Separate eligibility and exclusion conditions
        eligibility_conditions = []
        exclusion_conditions = []
        
        for condition in benefit_specific_conditions:
            condition_type = condition.get('condition_type')
            products = condition.get('products', {})
            product_condition = products.get(product)
            
            if not product_condition:
                continue
            
            condition_data = {
                'condition': condition.get('condition'),
                'condition_type': condition_type,
                'condition_exist': product_condition.get('condition_exist', False),
                'original_text': product_condition.get('original_text', ''),
                'parameters': product_condition.get('parameters', {})
            }
            
            if condition_type == 'benefit_eligibility':
                eligibility_conditions.append(condition_data)
            elif condition_type == 'benefit_exclusion':
                exclusion_conditions.append(condition_data)
        
        return {
            'product': product,
            'benefit_name': benefit_name,
            'layer_2_details': layer_2_details,
            'layer_3_eligibility': eligibility_conditions,
            'layer_3_exclusion': exclusion_conditions
        }
    
    def show_policy_exclusion(self, product: str) -> Dict[str, Any]:
        """
        Show list of exclusions in layer 1 for a specific policy
        
        This function:
        1. Filters layer_1_general_conditions by condition_type == "exclusion"
        2. Returns all exclusions where condition_exist is true for the product
        
        Args:
            product: Product name (e.g., "Scootsurance", "TravelEasy", "TravelEasy Pre-Ex")
        
        Returns:
            Dictionary containing list of exclusions for the product
        """
        if not self.taxonomy_data:
            raise ValueError("Taxonomy data not loaded")
        
        # Validate product
        available_products = self.taxonomy_data.get('products', [])
        if product not in available_products:
            raise ValueError(f"Product '{product}' not found. Available products: {available_products}")
        
        # Get layer 1 general conditions
        layer_1_conditions = self.taxonomy_data.get('layers', {}).get('layer_1_general_conditions', [])
        
        # Filter by condition_type == "exclusion"
        exclusion_conditions = [
            cond for cond in layer_1_conditions
            if cond.get('condition_type') == 'exclusion'
        ]
        
        exclusions = []
        
        for condition in exclusion_conditions:
            condition_name = condition.get('condition')
            products = condition.get('products', {})
            
            # Get product-specific condition data
            product_condition = products.get(product)
            if not product_condition:
                continue
            
            # Check if condition exists for this product
            if product_condition.get('condition_exist', False):
                exclusion_data = {
                    'condition': condition_name,
                    'condition_type': 'exclusion',
                    'original_text': product_condition.get('original_text', ''),
                    'parameters': product_condition.get('parameters', {})
                }
                exclusions.append(exclusion_data)
        
        return {
            'product': product,
            'exclusions': exclusions,
            'total_count': len(exclusions)
        }
    
    def show_policy_exclusion_details(self, product: str, condition: str) -> Dict[str, Any]:
        """
        Show detailed information for a specific exclusion condition
        
        This function:
        1. Finds the exclusion condition in layer_1_general_conditions
        2. Returns the exclusion details for the specific product and condition
        
        Args:
            product: Product name (e.g., "Scootsurance", "TravelEasy", "TravelEasy Pre-Ex")
            condition: Condition name (e.g., "pre_existing_conditions", "travel_advisory_exclusion")
        
        Returns:
            Dictionary containing exclusion details for the specific product and condition
        """
        if not self.taxonomy_data:
            raise ValueError("Taxonomy data not loaded")
        
        # Validate product
        available_products = self.taxonomy_data.get('products', [])
        if product not in available_products:
            raise ValueError(f"Product '{product}' not found. Available products: {available_products}")
        
        # Get layer 1 general conditions
        layer_1_conditions = self.taxonomy_data.get('layers', {}).get('layer_1_general_conditions', [])
        
        # Find the exclusion condition
        exclusion_condition = None
        for cond in layer_1_conditions:
            if cond.get('condition') == condition and cond.get('condition_type') == 'exclusion':
                exclusion_condition = cond
                break
        
        if not exclusion_condition:
            # Get list of available exclusion conditions
            available_exclusions = [
                cond.get('condition') for cond in layer_1_conditions
                if cond.get('condition_type') == 'exclusion'
            ]
            raise ValueError(
                f"Exclusion condition '{condition}' not found. "
                f"Available exclusion conditions: {available_exclusions}"
            )
        
        # Get product-specific exclusion data
        products = exclusion_condition.get('products', {})
        product_exclusion = products.get(product)
        
        if not product_exclusion:
            raise ValueError(f"Exclusion condition '{condition}' not available for product '{product}'")
        
        if not product_exclusion.get('condition_exist', False):
            raise ValueError(
                f"Exclusion condition '{condition}' does not exist "
                f"(condition_exist: false) for product '{product}'"
            )
        
        exclusion_details = {
            'condition': condition,
            'condition_type': 'exclusion',
            'condition_exist': product_exclusion.get('condition_exist', False),
            'original_text': product_exclusion.get('original_text', ''),
            'parameters': product_exclusion.get('parameters', {})
        }
        
        return {
            'product': product,
            'condition': condition,
            'exclusion_details': exclusion_details
        }
    
    def grade_policy(self, prioritized_benefits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Grade policies based on prioritized benefits using a point system
        
        This function:
        1. Takes a list of prioritized benefits (with optional priority scores)
        2. Scores each policy based on which prioritized benefits it offers
        3. Returns scores and rankings for all policies
        
        Grading System:
        - Base points per benefit: 10 points
        - Priority multiplier:
          - Priority 1 (highest): 3.0x = 30 points
          - Priority 2: 2.5x = 25 points
          - Priority 3: 2.0x = 20 points
          - Priority 4: 1.5x = 15 points
          - Priority 5+: 1.0x = 10 points
        - If explicit priority_score is provided, use that directly (0-100 scale)
        - Bonus: +5 points if policy has all top 3 prioritized benefits
        
        Args:
            prioritized_benefits: List of benefit dictionaries, each containing:
                - benefit_name: Name of the benefit (required)
                - priority: Optional priority rank (1 = highest, defaults to order in list)
                - priority_score: Optional explicit score (0-100, overrides priority)
        
        Returns:
            Dictionary containing:
            - policy_scores: Scores for each policy
            - rankings: Policies ranked by score (highest first)
            - detailed_scores: Breakdown of points per benefit per policy
        """
        if not self.taxonomy_data:
            raise ValueError("Taxonomy data not loaded")
        
        if not prioritized_benefits:
            raise ValueError("prioritized_benefits list cannot be empty")
        
        # Get all products
        available_products = self.taxonomy_data.get('products', [])
        layer_2_benefits = self.taxonomy_data.get('layers', {}).get('layer_2_benefits', [])
        
        # Normalize prioritized benefits and assign priority scores
        normalized_benefits = []
        for idx, benefit_item in enumerate(prioritized_benefits):
            if isinstance(benefit_item, str):
                # Simple string format - use index as priority
                benefit_name = benefit_item
                priority = idx + 1
                priority_score = None
            elif isinstance(benefit_item, dict):
                benefit_name = benefit_item.get('benefit_name')
                if not benefit_name:
                    raise ValueError(f"Benefit item at index {idx} missing 'benefit_name'")
                priority = benefit_item.get('priority', idx + 1)
                priority_score = benefit_item.get('priority_score')
            else:
                raise ValueError(f"Invalid benefit item format at index {idx}: {benefit_item}")
            
            # Calculate score if not explicitly provided
            if priority_score is not None:
                score = priority_score
            else:
                # Use priority-based scoring
                if priority == 1:
                    score = 30.0
                elif priority == 2:
                    score = 25.0
                elif priority == 3:
                    score = 20.0
                elif priority == 4:
                    score = 15.0
                else:
                    score = 10.0
            
            normalized_benefits.append({
                'benefit_name': benefit_name,
                'priority': priority,
                'score': score
            })
        
        # Initialize scores for all policies
        policy_scores = {product: 0.0 for product in available_products}
        detailed_scores = {product: {} for product in available_products}
        benefit_coverage = {product: [] for product in available_products}
        
        # Score each policy
        for benefit_info in normalized_benefits:
            benefit_name = benefit_info['benefit_name']
            score = benefit_info['score']
            
            # Find the benefit in layer 2
            benefit_found = False
            for benefit in layer_2_benefits:
                if benefit.get('benefit_name') == benefit_name:
                    benefit_found = True
                    products = benefit.get('products', {})
                    
                    # Check each product
                    for product in available_products:
                        product_benefit = products.get(product)
                        if product_benefit and product_benefit.get('condition_exist', False):
                            # Benefit exists - award points
                            policy_scores[product] += score
                            detailed_scores[product][benefit_name] = {
                                'points': score,
                                'priority': benefit_info['priority'],
                                'covered': True
                            }
                            benefit_coverage[product].append(benefit_name)
                        else:
                            # Benefit doesn't exist
                            detailed_scores[product][benefit_name] = {
                                'points': 0.0,
                                'priority': benefit_info['priority'],
                                'covered': False
                            }
                    break
            
            if not benefit_found:
                # Benefit not found in taxonomy - no points for any policy
                for product in available_products:
                    detailed_scores[product][benefit_name] = {
                        'points': 0.0,
                        'priority': benefit_info['priority'],
                        'covered': False,
                        'note': 'Benefit not found in taxonomy'
                    }
        
        # Bonus: +5 points if policy has all top 3 prioritized benefits
        top_3_benefits = [b['benefit_name'] for b in normalized_benefits[:3]]
        for product in available_products:
            covered_top_3 = [b for b in top_3_benefits if b in benefit_coverage[product]]
            if len(covered_top_3) == len(top_3_benefits) and len(top_3_benefits) > 0:
                policy_scores[product] += 5.0
                detailed_scores[product]['_bonus_complete_top_3'] = {
                    'points': 5.0,
                    'note': f'Bonus for covering all top 3 benefits: {", ".join(top_3_benefits)}'
                }
        
        # Create rankings (highest score first)
        rankings = sorted(
            available_products,
            key=lambda p: policy_scores[p],
            reverse=True
        )
        
        # Calculate percentage scores (normalized to 0-100)
        max_possible_score = sum(b['score'] for b in normalized_benefits) + 5.0  # Include bonus
        percentage_scores = {
            product: (policy_scores[product] / max_possible_score * 100) if max_possible_score > 0 else 0.0
            for product in available_products
        }
        
        return {
            'policy_scores': policy_scores,
            'percentage_scores': percentage_scores,
            'rankings': rankings,
            'detailed_scores': detailed_scores,
            'prioritized_benefits': normalized_benefits,
            'max_possible_score': max_possible_score
        }

