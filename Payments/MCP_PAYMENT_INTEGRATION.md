# MCP Payment Integration Guide

## Overview
This integration allows MCP (Model Context Protocol) to trigger Stripe payment pages in the Chrome extension by providing policy name and premium information.

## Architecture Flow

```
MCP → Backend API (/trigger-payment) → Extension Polling → Payment Component → Stripe Checkout
```

## How It Works

1. **MCP calls backend endpoint** with policy details
2. **Backend creates Stripe checkout session** and stores it
3. **Extension background script polls** for pending payments
4. **Extension UI receives payment trigger** and shows Payment component
5. **User is redirected** to Stripe checkout page

## API Endpoints

### POST `/trigger-payment`
**Purpose**: MCP calls this endpoint to create a payment checkout session

**Request Body**:
```json
{
  "policy_name": "Travel Insurance - Premium Plan",
  "premium": 59.99,
  "currency": "SGD"
}
```

**Response**:
```json
{
  "success": true,
  "payment_intent_id": "payment_abc123",
  "checkout_url": "https://checkout.stripe.com/pay/cs_...",
  "session_id": "cs_...",
  "message": "Payment checkout created successfully. Extension will retrieve it."
}
```

**Example MCP Call**:
```python
import requests

response = requests.post(
    "http://localhost:8085/trigger-payment",
    json={
        "policy_name": "Travel Insurance - Premium Plan",
        "premium": 59.99,
        "currency": "SGD"
    }
)
```

### GET `/get-pending-payment`
**Purpose**: Extension polls this endpoint to retrieve pending payments

**Response** (when payment available):
```json
{
  "has_payment": true,
  "payment_intent_id": "payment_abc123",
  "checkout_url": "https://checkout.stripe.com/pay/cs_...",
  "session_id": "cs_...",
  "policy_name": "Travel Insurance - Premium Plan",
  "premium": 59.99,
  "amount_cents": 5999,
  "currency": "SGD"
}
```

**Response** (no payment):
```json
{
  "has_payment": false,
  "message": "No pending payments"
}
```

## Extension Components

### Background Script (`background.js`)
- Automatically polls `/get-pending-payment` every 2 seconds
- Sends `triggerPayment` message to extension UI when payment is found
- Auto-starts polling when background script loads

### Payment Component (`Payment.tsx`)
- Listens for payment trigger messages
- Displays policy name and premium from MCP
- Automatically redirects to Stripe checkout URL
- Opens Stripe in new tab (required for Chrome extensions)

### App Component (`App.tsx`)
- Listens for `triggerPayment` messages from background script
- Switches to payment stage when payment is triggered
- Passes payment data to Payment component

## Usage Example

### From MCP/LLM:
```python
# When user wants to purchase insurance
import requests

# Get policy details from your system
policy_name = "Travel Insurance - Premium Plan"
premium = 59.99  # in dollars

# Trigger payment
response = requests.post(
    "http://localhost:8085/trigger-payment",
    json={
        "policy_name": policy_name,
        "premium": premium,
        "currency": "SGD"
    }
)

if response.json()["success"]:
    print(f"Payment checkout created: {response.json()['checkout_url']}")
    print("Extension will automatically show payment page to user")
```

## Configuration

### Backend (Payment Service)
- **Port**: 8085 (default)
- **Environment Variables**:
  - `STRIPE_SECRET_KEY`: Your Stripe secret key
  - `DYNAMODB_PAYMENTS_TABLE`: DynamoDB table name
  - `AWS_REGION`: AWS region
  - `DDB_ENDPOINT`: DynamoDB endpoint (for local: `http://localhost:8000`)

### Extension
- **Polling Interval**: 2 seconds (configurable in `background.js`)
- **Payment API URL**: `http://localhost:8085` (hardcoded, can be made configurable)

## Payment Flow

1. **MCP determines** user needs insurance and calculates premium
2. **MCP calls** `/trigger-payment` with policy details
3. **Backend creates** Stripe checkout session
4. **Backend stores** payment in pending queue
5. **Extension polls** and finds pending payment
6. **Extension UI** shows Payment component with policy details
7. **User clicks** "Continue to Stripe Checkout" or auto-redirects
8. **Stripe checkout** opens in new tab
9. **User completes** payment on Stripe
10. **Stripe webhook** notifies backend (existing webhook handler)

## Notes

- Payments are stored in-memory in the backend (will be lost on restart)
- Each payment can only be retrieved once (marked as `claimed`)
- Extension automatically starts polling on load
- Stripe checkout opens in new tab (Chrome extension security requirement)
- Payment component shows policy name and premium from MCP data

## Testing

### Test MCP Trigger:
```bash
curl -X POST http://localhost:8085/trigger-payment \
  -H "Content-Type: application/json" \
  -d '{
    "policy_name": "Travel Insurance - Test Plan",
    "premium": 29.99,
    "currency": "SGD"
  }'
```

### Check Pending Payment:
```bash
curl http://localhost:8085/get-pending-payment
```

### Expected Behavior:
1. Call `/trigger-payment` with policy details
2. Extension should automatically detect payment within 2 seconds
3. Payment component should appear with correct policy name and premium
4. Clicking button should open Stripe checkout in new tab

