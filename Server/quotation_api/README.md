# Insurance Quotation API

API server for generating insurance policy quotations with multiple coverage tiers.

## Overview

This service provides quotation services for three insurance policy types:
- **Scootsurance**: Standard travel insurance
- **TravelEasy**: Enhanced travel insurance
- **TravelEasy Pre-Ex**: Travel insurance with pre-existing conditions coverage

Each quotation includes three coverage tiers:
- **Basic**: Essential coverage for basic travel protection
- **Standard**: Comprehensive coverage with enhanced benefits
- **Premium**: Maximum protection with premium services and highest limits

## Features

- Generate quotations for multiple policy types
- Three-tier coverage options (Basic, Standard, Premium)
- Premium calculation based on:
  - Policy type
  - Age of insured person
  - Number of days travelling
  - Destination continent
- RESTful API with FastAPI
- Automatic API documentation (Swagger UI)

## Installation

1. Install dependencies:
```bash
cd Server/quotation_api
pip install -r requirements.txt
```

2. Start the server:
```bash
# From Server directory
python start_quotation_api.py
```

Or directly:
```bash
cd Server/quotation_api
uvicorn server:app --host 0.0.0.0 --port 8009 --reload
```

## API Endpoints

### Health Check
- **GET** `/health` - Health check endpoint
- **GET** `/` - Root endpoint with API information

### Quotation
- **POST** `/quote` - Generate insurance quotation

### Information
- **GET** `/policies` - Get list of supported policy types
- **GET** `/continents` - Get list of supported continents
- **GET** `/tiers` - Get list of supported coverage tiers

## Usage Examples

### Generate Quotation

**Request:**
```bash
curl -X POST "http://localhost:8009/quote" \
  -H "Content-Type: application/json" \
  -d '{
    "policy_type": "Scootsurance",
    "age": 35,
    "days": 7,
    "continent": "Asia"
  }'
```

**Response:**
```json
{
  "success": true,
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
```

### Get Supported Policies
```bash
curl http://localhost:8009/policies
```

### Get Supported Continents
```bash
curl http://localhost:8009/continents
```

## Premium Calculation

The premium is calculated using the following formula:

```
Premium = Base Premium × Age Multiplier × Days Multiplier × Continent Multiplier × Tier Multiplier
```

### Base Premiums (SGD)
- Scootsurance: $50.00
- TravelEasy: $60.00
- TravelEasy Pre-Ex: $80.00

### Age Multipliers
- 0-17 years: 0.8x
- 18-30 years: 1.0x
- 31-50 years: 1.2x
- 51-65 years: 1.5x
- 66-75 years: 2.0x
- 76+ years: 2.5x

### Days Multiplier
- Base: 1.0 + (days × 0.05)
- Example: 7 days = 1.35x

### Continent Multipliers
- Asia: 1.0x
- Europe: 1.1x
- North America: 1.15x
- South America: 1.3x
- Africa: 1.4x
- Oceania: 1.05x
- Antarctica: 1.8x

### Tier Multipliers
- Basic: 1.0x
- Standard: 1.5x
- Premium: 2.0x

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8009/docs
- **ReDoc**: http://localhost:8009/redoc

## Configuration

Environment variables (optional):
- `QUOTATION_API_HOST`: Server host (default: `0.0.0.0`)
- `QUOTATION_API_PORT`: Server port (default: `8009`)

## Supported Policy Types

1. **Scootsurance**
   - Standard travel insurance coverage
   - Base premium: $50.00

2. **TravelEasy**
   - Enhanced travel insurance with additional benefits
   - Base premium: $60.00

3. **TravelEasy Pre-Ex**
   - Travel insurance with pre-existing conditions coverage
   - Base premium: $80.00

## Supported Continents

- Asia
- Europe
- North America
- South America
- Africa
- Oceania
- Antarctica

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input parameters)
- `500`: Internal Server Error

Error responses include a `detail` field with error information.

## Development

### Project Structure
```
quotation_api/
├── __init__.py
├── config.py              # Configuration settings
├── quotation_engine.py     # Premium calculation logic
├── server.py              # FastAPI application
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

### Testing

Test the API using the interactive Swagger UI at http://localhost:8009/docs or use curl/Postman.

Example test cases:
1. Scootsurance, age 35, 7 days, Asia
2. TravelEasy, age 65, 14 days, Europe
3. TravelEasy Pre-Ex, age 45, 30 days, Africa

## Notes

- Premiums are calculated for demonstration purposes and may not reflect actual insurance pricing
- All premiums are in SGD (Singapore Dollars)
- The calculation logic can be adjusted in `quotation_engine.py`

