# Policy Eligibility Scanner API

API server for scanning and validating policy eligibility based on Layer 1 general conditions from the Travel Insurance Product Taxonomy.

## Overview

The Policy Eligibility Scanner checks user-provided data against eligibility conditions defined in `Taxonomy_Hackathon.json`. It filters `layer_1_general_conditions` by `condition_type == "eligibility"`, performs rule-based checks on conditions with parameters, and skips conditions without parameters.

## Required User Data Fields

The following user data fields are required based on the eligibility conditions that have parameters. Fields marked as **Optional** will only be checked if provided; if not provided, the condition check will be skipped.

### Required Fields (All Products)

#### 1. `departure_location` (string)
- **Required for**: All products (Scootsurance, TravelEasy, TravelEasy Pre-Ex)
- **Description**: The departure location for the trip
- **Expected Value**: "Singapore" (case-insensitive)
- **Condition**: `trip_start_singapore`
- **Example**: `"departure_location": "Singapore"`

#### 2. `age` (number)
- **Required for**: All products
- **Description**: Age of the insured person in years
- **Expected Value**: Numeric value (integer or float)
- **Condition**: `age_eligibility`
- **Product-Specific Rules**:
  - **Scootsurance**: Must be between 1 month (0.083 years) and 74 years
  - **TravelEasy / TravelEasy Pre-Ex**: Must be 70 years or less for single trip eligibility
- **Example**: `"age": 35`

#### 3. `trip_type` (string)
- **Required for**: TravelEasy, TravelEasy Pre-Ex (optional for Scootsurance)
- **Description**: Type of trip - 'single' for single trip or 'annual' for annual plan
- **Expected Value**: `"single"` or `"annual"` (case-insensitive)
- **Note**: This is **not a condition in the taxonomy**, but a user input that determines which age eligibility parameter to check. The taxonomy has both `maximum_age_single_trip_eligibility` and `maximum_age_annual_plan_purchase` parameters, and `trip_type` selects which one to validate against.
- **Condition**: `age_eligibility` (affects which age validation parameter is checked for TravelEasy products)
- **Product-Specific Rules**:
  - **TravelEasy / TravelEasy Pre-Ex**: 
    - Single trip (`trip_type: "single"`): Checks against `maximum_age_single_trip_eligibility` (70 years)
    - Annual plan (`trip_type: "annual"`): Checks against `maximum_age_annual_plan_purchase` (70 years, must purchase before age 70)
  - **Scootsurance**: Not used (age limits apply regardless of trip type)
- **Default**: If not provided, defaults to `"single"`
- **Example**: `"trip_type": "single"`

#### 4. `purchase_timing` (string)
- **Required for**: All products
- **Description**: When the insurance is being purchased relative to departure
- **Expected Value**: Must contain "before" or "prior" (case-insensitive)
- **Condition**: `pre_trip_purchased`
- **Expected Format**: "before departure from Singapore" or similar
- **Example**: `"purchase_timing": "before departure from Singapore"`

### Required Fields (TravelEasy & TravelEasy Pre-Ex Only)

#### 5. `return_location` (string)
- **Required for**: TravelEasy, TravelEasy Pre-Ex
- **Description**: The return location for the round trip
- **Expected Value**: "Singapore" (case-insensitive)
- **Condition**: `trip_start_singapore`
- **Note**: Not required for Scootsurance (one-way trips allowed)
- **Example**: `"return_location": "Singapore"`


## Example Request Bodies

### Scootsurance (Minimum Required)
```json
{
  "product": "Scootsurance",
  "user_data": {
    "departure_location": "Singapore",
    "age": 35,
    "purchase_timing": "before departure from Singapore"
  }
}
```

### TravelEasy (Single Trip)
```json
{
  "product": "TravelEasy",
  "user_data": {
    "departure_location": "Singapore",
    "return_location": "Singapore",
    "age": 45,
    "trip_type": "single",
    "purchase_timing": "before departure from Singapore"
  }
}
```

### TravelEasy (Annual Plan)
```json
{
  "product": "TravelEasy",
  "user_data": {
    "departure_location": "Singapore",
    "return_location": "Singapore",
    "age": 45,
    "trip_type": "annual",
    "purchase_timing": "before departure from Singapore"
  }
}
```

### TravelEasy Pre-Ex
```json
{
  "product": "TravelEasy Pre-Ex",
  "user_data": {
    "departure_location": "Singapore",
    "return_location": "Singapore",
    "age": 40,
    "trip_type": "single",
    "purchase_timing": "before departure from Singapore"
  }
}
```

## Conditions That Are Skipped

The following eligibility conditions will be automatically skipped during scanning:

1. `good_health` - No parameters to check
2. `awareness_of_circumstances` - No parameters to check
3. `declaration_of_previous_insurance` - No parameters to check
4. `medical_advice_and_treatment_restriction` - No parameters to check
5. `child_accompaniment_requirement` - Explicitly skipped (even though it has parameters)

These conditions are still part of the policy but require manual verification or are declarative in nature.

## API Endpoints

### POST `/scan_policy_eligibility`
Scans policy eligibility for a given product and user data.

**Request Body:**
```json
{
  "product": "Scootsurance",
  "user_data": {
    "departure_location": "Singapore",
    "age": 35,
    "purchase_timing": "before departure from Singapore"
  }
}
```

**Response:**
```json
{
  "success": true,
  "product": "Scootsurance",
  "eligible": true,
  "conditions_checked": [
    {
      "condition": "trip_start_singapore",
      "eligible": true,
      "reason": "Location requirements met",
      "original_text": "Your trip must begin in Singapore.",
      "parameters_checked": ["departure_location"]
    },
    {
      "condition": "age_eligibility",
      "eligible": true,
      "reason": "Age 35 meets requirements (1 months to 74 years)",
      "original_text": "To be eligible for cover under this Policy, You have to be aged over 1 month to 74 years old, before the start of Your trip.",
      "parameters_checked": ["minimum_age", "maximum_age", "unit_min", "unit_max"]
    },
    {
      "condition": "pre_trip_purchased",
      "eligible": true,
      "reason": "Purchase timing 'before departure from Singapore' meets requirement: before departure from Singapore",
      "original_text": "You must purchase the insurance before departing Singapore...",
      "parameters_checked": ["purchase_timing"]
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
```

### GET `/products`
Returns list of available products from taxonomy.

**Response:**
```json
["Scootsurance", "TravelEasy", "TravelEasy Pre-Ex"]
```

### GET `/eligibility_conditions`
Returns list of eligibility conditions from layer_1_general_conditions.

### GET `/show_policy_benefits`
### GET `/show_policy_benefits/{product}`
Returns policy benefits for a specific product or all products.

**Query Parameters:**
- `product` (optional): Product name (e.g., "Scootsurance", "TravelEasy", "TravelEasy Pre-Ex")
  - If not provided, returns benefits for all products
  - If provided, returns benefits only for that product

**Response:**
```json
{
  "Scootsurance": [
    "accidental_death_permanent_disablement",
    "funeral_expenses_accidental_death"
  ],
  "TravelEasy": [
    "funeral_expenses_accidental_death",
    "child_education_grant"
  ],
  "TravelEasy Pre-Ex": [
    "child_education_grant",
    "family_assistance"
  ]
}
```

**Example Requests:**
- `GET /show_policy_benefits` - Returns benefits for all products
- `GET /show_policy_benefits/Scootsurance` - Returns benefits only for Scootsurance

**Note:** Only returns benefits where `condition_exist: true` in the taxonomy. The exact `benefit_name` from `layer_2_benefits` is returned.

### POST `/show_policy_benefit_details`
Returns detailed information for a specific policy benefit, including layer 2 details and layer 3 eligibility/exclusion conditions.

**Request Body:**
```json
{
  "product": "Scootsurance",
  "benefit_name": "accidental_death_permanent_disablement"
}
```

**Response:**
```json
{
  "success": true,
  "product": "Scootsurance",
  "benefit_name": "accidental_death_permanent_disablement",
  "layer_2_details": {
    "benefit_name": "accidental_death_permanent_disablement",
    "condition_exist": true,
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
      "condition_exist": true,
      "original_text": "Death within ninety (90) days from the date of Accident; or Permanent Disablement within one hundred and eighty (180) days from the date of Accident",
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
      "condition_exist": true,
      "original_text": "In addition to the General Exclusions, We will not pay for any claims in respect of any loss caused by or resulting from any Illness or infectious disease.",
      "parameters": {}
    }
  ]
}
```

**Notes:**
- The `benefit_name` must match exactly with the `benefit_name` in `layer_2_benefits`
- Layer 3 conditions are filtered by matching `benefit_name` between layer 2 and layer 3
- Only conditions where `condition_exist: true` for the specific product are included
- Layer 3 conditions are separated into `benefit_eligibility` and `benefit_exclusion` types

### GET `/show_policy_exclusion/{product}`
Returns list of exclusions in layer 1 for a specific policy.

**Path Parameters:**
- `product`: Product name (e.g., "Scootsurance", "TravelEasy", "TravelEasy Pre-Ex")

**Response:**
```json
{
  "success": true,
  "product": "Scootsurance",
  "exclusions": [
    {
      "condition": "pre_existing_conditions",
      "condition_type": "exclusion",
      "original_text": "Pre-Existing Medical Condition Any Injury or Illness which: (a) You have received medical treatment, diagnosis, consultation, or prescribed drugs within 365 days prior to Your trip; or (b) symptoms or manifestations have existed, whether treatment was actually received, within 365 days prior to Your trip; or (c) a reasonable person in the circumstances would be expected to be aware of within 365 days prior to Your trip",
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
```

**Example Request:**
- `GET /show_policy_exclusion/Scootsurance` - Returns all exclusions for Scootsurance

**Notes:**
- Only returns exclusions where `condition_type == "exclusion"` in layer_1_general_conditions
- Only includes exclusions where `condition_exist: true` for the specified product
- Each exclusion includes the condition name, original text, and any parameters

### POST `/show_policy_exclusion_details`
Returns detailed information for a specific exclusion condition.

**Request Body:**
```json
{
  "product": "Scootsurance",
  "condition": "pre_existing_conditions"
}
```

**Response:**
```json
{
  "success": true,
  "product": "Scootsurance",
  "condition": "pre_existing_conditions",
  "exclusion_details": {
    "condition": "pre_existing_conditions",
    "condition_type": "exclusion",
    "condition_exist": true,
    "original_text": "Pre-Existing Medical Condition Any Injury or Illness which: (a) You have received medical treatment, diagnosis, consultation, or prescribed drugs within 365 days prior to Your trip; or (b) symptoms or manifestations have existed, whether treatment was actually received, within 365 days prior to Your trip; or (c) a reasonable person in the circumstances would be expected to be aware of within 365 days prior to Your trip",
    "parameters": {
      "lookback_period": 365,
      "unit": "days"
    }
  }
}
```

**Notes:**
- The `condition` must match exactly with the condition name in `layer_1_general_conditions`
- Only returns exclusion details where `condition_type == "exclusion"`
- Only includes details where `condition_exist: true` for the specified product
- Returns the complete exclusion details including original text and parameters

### POST `/grade_policy`
Grades all policies based on prioritized benefits using a point system to determine which policy is best for the client's scenario.

**Grading System:**
- **Base Points**: 10 points per benefit
- **Priority Multipliers**:
  - Priority 1 (highest): 3.0x = **30 points**
  - Priority 2: 2.5x = **25 points**
  - Priority 3: 2.0x = **20 points**
  - Priority 4: 1.5x = **15 points**
  - Priority 5+: 1.0x = **10 points**
- **Bonus**: +5 points if policy covers all top 3 prioritized benefits
- **Custom Scores**: If `priority_score` (0-100) is provided, it overrides priority-based scoring

**Request Body:**
```json
{
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
```

**Alternative Request Format (with explicit scores):**
```json
{
  "prioritized_benefits": [
    {
      "benefit_name": "accidental_death_permanent_disablement",
      "priority_score": 50.0
    },
    {
      "benefit_name": "funeral_expenses_accidental_death",
      "priority_score": 30.0
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "policy_scores": {
    "Scootsurance": 55.0,
    "TravelEasy": 50.0,
    "TravelEasy Pre-Ex": 45.0
  },
  "percentage_scores": {
    "Scootsurance": 78.6,
    "TravelEasy": 71.4,
    "TravelEasy Pre-Ex": 64.3
  },
  "rankings": ["Scootsurance", "TravelEasy", "TravelEasy Pre-Ex"],
  "detailed_scores": {
    "Scootsurance": {
      "accidental_death_permanent_disablement": {
        "points": 30.0,
        "priority": 1,
        "covered": true
      },
      "funeral_expenses_accidental_death": {
        "points": 25.0,
        "priority": 2,
        "covered": true
      },
      "child_education_grant": {
        "points": 0.0,
        "priority": 3,
        "covered": false
      },
      "_bonus_complete_top_3": {
        "points": 5.0,
        "note": "Bonus for covering all top 3 benefits: accidental_death_permanent_disablement, funeral_expenses_accidental_death, child_education_grant"
      }
    }
  },
  "prioritized_benefits": [
    {
      "benefit_name": "accidental_death_permanent_disablement",
      "priority": 1,
      "score": 30.0
    },
    {
      "benefit_name": "funeral_expenses_accidental_death",
      "priority": 2,
      "score": 25.0
    }
  ],
  "max_possible_score": 70.0
}
```

**Notes:**
- Benefits can be provided as simple strings (order = priority) or as objects with explicit priority/score
- `policy_scores`: Raw point totals for each policy
- `percentage_scores`: Scores normalized to 0-100% based on max possible score
- `rankings`: Policies ranked by score (highest first)
- `detailed_scores`: Breakdown showing which benefits each policy covers and points awarded
- Only benefits where `condition_exist: true` in the taxonomy are counted

### GET `/health`
Health check endpoint.

## Field Validation Rules

### Location Fields
- **Case-insensitive**: "Singapore", "singapore", "SINGAPORE" are all valid
- **Exact match required**: Must match "Singapore" exactly (case-insensitive)

### Age Field
- **Type**: Must be numeric (integer or float)
- **Scootsurance**: 
  - Minimum: 1 month (0.083 years)
  - Maximum: 74 years
- **TravelEasy / TravelEasy Pre-Ex**:
  - Single trip (`trip_type: "single"`): Maximum 70 years
  - Annual plan (`trip_type: "annual"`): Maximum 70 years (must purchase before age 70)
  - Renewal: Up to 80 years

### Trip Type Field
- **Type**: String
- **Valid Values**: `"single"` or `"annual"` (case-insensitive)
- **Required for**: TravelEasy, TravelEasy Pre-Ex (optional for Scootsurance)
- **Usage**: Determines which age eligibility rules apply
  - `"single"`: Checks against `maximum_age_single_trip_eligibility`
  - `"annual"`: Checks against `maximum_age_annual_plan_purchase`
- **Default**: If not provided for TravelEasy products, defaults to `"single"`

### Purchase Timing
- **Format**: Must contain "before" or "prior" (case-insensitive)
- **Example valid values**:
  - "before departure from Singapore"
  - "prior to departure"
  - "before leaving Singapore"


## Error Handling

If a required field is missing, the API will return:
```json
{
  "success": true,
  "eligible": false,
  "conditions_checked": [
    {
      "condition": "trip_start_singapore",
      "eligible": false,
      "reason": "Missing required field: departure_location"
    }
  ]
}
```

## Running the Server

```bash
# From Server directory
python start_policy_eligibility_scanner.py
```

The server runs on `http://localhost:8006` by default (configurable via environment variables).

## Environment Variables

- `POLICY_ELIGIBILITY_HOST`: Server host (default: `0.0.0.0`)
- `POLICY_ELIGIBILITY_PORT`: Server port (default: `8006`)
- `TAXONOMY_FILE_PATH`: Path to Taxonomy_Hackathon.json (default: `../Taxonomy_Hackathon.json`)

## Notes

- All conditions with empty parameters (`{}` or `[]`) are automatically skipped
- Only conditions with `condition_type == "eligibility"` are checked
- Conditions that don't exist for a product (`condition_exist: false`) are skipped
- The scanner performs rule-based validation, not just simple parameter matching

