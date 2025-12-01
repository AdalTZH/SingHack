import json
from datetime import datetime
from typing import Dict, List, Any, Optional


def scan_policy_eligibility(
    age: int,
    trip_type: str,  # 'single' or 'annual'
    departure_location: str,
    return_location: str,
    child_age: Optional[int] = None,
    has_adult_guardian: bool = True,
    has_pre_existing_condition: bool = False,
    pre_existing_lookback_days: int = 0,
    travel_advisory_exists: bool = False,
    aware_of_claim_circumstances: bool = False,
    purchased_before_departure: bool = True,
    previously_refused_insurance: bool = False,
    travelling_against_doctor_advice: bool = False,
    travelling_for_medical_treatment: bool = False,
    good_health: bool = True,
    file_path: str = "./Server/Taxonomy_Hackathon.json"
) -> Dict[str, Any]:
    """
    Scans ALL policies and returns which ones the user is eligible for.

    Parameters:
    - age: Age of the insured person in years
    - trip_type: Type of trip ('single' or 'annual')
    - departure_location: Where the trip starts
    - return_location: Where the trip ends
    - child_age: Age of child if applicable (None if not a child)
    - has_adult_guardian: Whether child is accompanied by parent/guardian
    - has_pre_existing_condition: Whether person has pre-existing medical condition
    - pre_existing_lookback_days: Days since last treatment for pre-existing condition
    - travel_advisory_exists: Whether government advisory against travel exists
    - aware_of_claim_circumstances: Whether aware of circumstances likely to lead to claim
    - purchased_before_departure: Whether insurance purchased before departure
    - previously_refused_insurance: Whether previously refused travel insurance
    - travelling_against_doctor_advice: Whether travelling against doctor's advice
    - travelling_for_medical_treatment: Whether travelling to get medical treatment
    - good_health: Whether person is in good health
    - file_path: Path to the taxonomy JSON file

    Returns:
    Dictionary with eligibility status for each policy
    """

    # Load taxonomy data
    try:
        with open(file_path, 'r') as f:
            taxonomy = json.load(f)
    except FileNotFoundError:
        return {"error": f"Taxonomy file not found at {file_path}"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in taxonomy file"}

    # Get all products
    products = taxonomy.get("products", [])
    layer_1_conditions = taxonomy.get("layers",
                                      {}).get("layer_1_general_conditions", [])

    # Initialize results for all policies
    all_results = {
        "eligible_policies": [],
        "ineligible_policies": [],
        "summary": {
            "total_policies": len(products),
            "eligible_count": 0,
            "ineligible_count": 0
        }
    }

    # Check each policy
    for policy_name in products:
        policy_result = {
            "policy_name": policy_name,
            "eligible": True,
            "failed_conditions": [],
            "passed_conditions": [],
            "warnings": []
        }

        # Process each eligibility condition
        for condition in layer_1_conditions:
            if condition.get("condition_type") != "eligibility":
                continue

            condition_name = condition.get("condition")
            product_data = condition.get("products", {}).get(policy_name, {})

            # Skip if condition doesn't exist for this product
            if not product_data.get("condition_exist"):
                continue

            parameters = product_data.get("parameters", {})
            original_text = product_data.get("original_text", "")

            # Check each condition
            passed = True
            failure_reason = ""

            if condition_name == "trip_start_singapore":
                if departure_location.lower() != "singapore":
                    passed = False
                    failure_reason = f"Trip must start in Singapore (currently: {departure_location})"
                elif "return_location" in parameters and return_location.lower(
                ) != "singapore":
                    passed = False
                    failure_reason = f"Trip must end in Singapore (currently: {return_location})"

            elif condition_name == "age_eligibility":
                if policy_name == "Scootsurance":
                    min_age_months = parameters.get("minimum_age", 1)
                    max_age_years = parameters.get("maximum_age", 74)
                    age_in_months = age * 12

                    if age_in_months < min_age_months:
                        passed = False
                        failure_reason = f"Age must be at least {min_age_months} months old (currently: {age} years)"
                    elif age > max_age_years:
                        passed = False
                        failure_reason = f"Age must not exceed {max_age_years} years (currently: {age} years)"

                elif policy_name == "TravelEasy Policy":
                    max_age_single = parameters.get("maximum_age_single_trip",
                                                    80)
                    max_age_annual = parameters.get("maximum_age_annual_plan",
                                                    70)

                    if trip_type == "single" and age > max_age_single:
                        passed = False
                        failure_reason = f"Age exceeds maximum of {max_age_single} years for single trip (currently: {age} years)"
                    elif trip_type == "annual" and age > max_age_annual:
                        passed = False
                        failure_reason = f"Age exceeds maximum of {max_age_annual} years for annual plan (currently: {age} years)"

                    # Note about age 70+
                    if age >= 70 and trip_type == "annual":
                        policy_result["warnings"].append(
                            "Age 70+ only eligible for Standard plan, must purchase before age 70"
                        )

            elif condition_name == "good_health":
                if not good_health:
                    passed = False
                    failure_reason = "Insured person must be in good health or free from physical defects"

            elif condition_name == "child_accompaniment_requirement":
                if child_age is not None and child_age < parameters.get(
                        "minimum_age", 12):
                    if not has_adult_guardian:
                        passed = False
                        failure_reason = f"Child under {parameters.get('minimum_age')} years must be accompanied by {parameters.get('accompanied_by')}"

            elif condition_name == "pre_existing_conditions":
                if has_pre_existing_condition:
                    lookback_period = parameters.get("lookback_period", 0)
                    unit = parameters.get("unit", "days")

                    # Convert to days for comparison
                    lookback_days = lookback_period
                    if unit == "months":
                        lookback_days = lookback_period * 30
                    elif unit == "years":
                        lookback_days = lookback_period * 365

                    if pre_existing_lookback_days < lookback_days:
                        passed = False
                        failure_reason = f"Pre-existing condition treated within {lookback_period} {unit} (required waiting period not met)"

            elif condition_name == "travel_advisory_exclusion":
                if travel_advisory_exists and policy_name == "Scootsurance":
                    passed = False
                    failure_reason = "Cannot travel to destination with government travel advisory"

            elif condition_name == "awareness_of_circumstances":
                if aware_of_claim_circumstances:
                    passed = False
                    failure_reason = "Cannot be aware of circumstances likely to lead to a claim at time of purchase"

            elif condition_name == "pre_trip_purchased":
                if not purchased_before_departure:
                    passed = False
                    failure_reason = "Insurance must be purchased before departing Singapore"

            elif condition_name == "declaration_of_previous_insurance":
                if previously_refused_insurance:
                    policy_result["warnings"].append(
                        "Must declare previous insurance refusal at point of application"
                    )

            elif condition_name == "medical_advice_and_treatment_restriction":
                if travelling_against_doctor_advice:
                    passed = False
                    failure_reason = "Cannot travel against the advice of a doctor"
                if travelling_for_medical_treatment:
                    passed = False
                    failure_reason = "Cannot travel for the purpose of getting medical treatment"

            elif condition_name == "pre_ex_critical_care_eligibility":
                if policy_name == "TravelEasy Pre-Ex Policy":
                    policy_result["warnings"].append(
                        "Must meet all conditions stated under section 52 - Pre-Ex Critical Care"
                    )

            # Record result
            if passed:
                policy_result["passed_conditions"].append({
                    "condition":
                    condition_name,
                    "description":
                    original_text
                })
            else:
                policy_result["eligible"] = False
                policy_result["failed_conditions"].append({
                    "condition":
                    condition_name,
                    "reason":
                    failure_reason,
                    "policy_requirement":
                    original_text
                })

        # Add to appropriate list
        if policy_result["eligible"]:
            all_results["eligible_policies"].append(policy_result)
            all_results["summary"]["eligible_count"] += 1
        else:
            all_results["ineligible_policies"].append(policy_result)
            all_results["summary"]["ineligible_count"] += 1

    return all_results


def print_eligibility_report(results: Dict[str, Any]) -> None:
    """
    Pretty prints the eligibility results
    """
    if "error" in results:
        print(f"ERROR: {results['error']}")
        return

    print("=" * 80)
    print("POLICY ELIGIBILITY REPORT")
    print("=" * 80)
    print(f"\nTotal Policies Checked: {results['summary']['total_policies']}")
    print(f"Eligible: {results['summary']['eligible_count']}")
    print(f"Ineligible: {results['summary']['ineligible_count']}")
    print()

    # Print eligible policies
    if results["eligible_policies"]:
        print("\n" + "=" * 80)
        print("✓ ELIGIBLE POLICIES")
        print("=" * 80)
        for policy in results["eligible_policies"]:
            print(f"\n✓ {policy['policy_name']}")
            print(f"  Status: ELIGIBLE")
            print(f"  Conditions Passed: {len(policy['passed_conditions'])}")

            if policy["warnings"]:
                print(f"\n  ⚠ Warnings:")
                for warning in policy["warnings"]:
                    print(f"    - {warning}")

    # Print ineligible policies
    if results["ineligible_policies"]:
        print("\n" + "=" * 80)
        print("✗ INELIGIBLE POLICIES")
        print("=" * 80)
        for policy in results["ineligible_policies"]:
            print(f"\n✗ {policy['policy_name']}")
            print(f"  Status: NOT ELIGIBLE")
            print(f"  Reasons:")
            for failed in policy["failed_conditions"]:
                print(f"\n    • {failed['reason']}")
                print(
                    f"      Policy Requirement: {failed['policy_requirement'][:150]}..."
                )

    print("\n" + "=" * 80)


# Example usage
if __name__ == "__main__":
    print("\n--- TEST CASE 1: Typical Eligible Customer ---")
    result1 = scan_policy_eligibility(age=35,
                                      trip_type="single",
                                      departure_location="Singapore",
                                      return_location="Singapore",
                                      good_health=True,
                                      purchased_before_departure=True,
                                      has_pre_existing_condition=False)
    print_eligibility_report(result1)

    print(
        "\n\n--- TEST CASE 2: Customer with Pre-existing Condition (Recent Treatment) ---"
    )
    result2 = scan_policy_eligibility(
        age=45,
        trip_type="single",
        departure_location="Singapore",
        return_location="Singapore",
        good_health=True,
        purchased_before_departure=True,
        has_pre_existing_condition=True,
        pre_existing_lookback_days=
        200  # Within 365 day lookback for Scootsurance
    )
    print_eligibility_report(result2)

    print("\n\n--- TEST CASE 3: Senior Citizen (75 years old) ---")
    result3 = scan_policy_eligibility(age=75,
                                      trip_type="single",
                                      departure_location="Singapore",
                                      return_location="Singapore",
                                      good_health=True,
                                      purchased_before_departure=True)
    print_eligibility_report(result3)

    print("\n\n--- TEST CASE 4: Customer Not in Good Health ---")
    result4 = scan_policy_eligibility(age=40,
                                      trip_type="single",
                                      departure_location="Singapore",
                                      return_location="Singapore",
                                      good_health=False,
                                      purchased_before_departure=True)
    print_eligibility_report(result4)
