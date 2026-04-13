import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import stripe
import boto3
import uuid
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional, Dict
import threading
import time

load_dotenv()

app = FastAPI(title="LEA Payment Pages", version="1.0.0")

# In-memory store for pending payments (for extension polling)
# Format: {payment_intent_id: {checkout_url, policy_name, premium, created_at, claimed}}
pending_payments: Dict[str, Dict] = {}
pending_payments_lock = threading.Lock()

# CORS middleware to allow extension to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Initialize DynamoDB
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv("AWS_REGION", "ap-southeast-1"),
    endpoint_url=os.getenv("DDB_ENDPOINT", "http://localhost:8000"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "dummy"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "dummy")
)

payments_table = dynamodb.Table(os.getenv("DYNAMODB_PAYMENTS_TABLE", "lea-payments-local"))

class PaymentRequest(BaseModel):
    amount: int = 5000  # Default $50 in cents
    product_name: str = "Travel Insurance - Standard Plan"
    currency: str = "SGD"

class TriggerPaymentRequest(BaseModel):
    policy_name: str
    premium: float  # Premium amount in dollars (will be converted to cents)
    currency: str = "SGD"

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "payment-pages"}

@app.post("/trigger-payment")
async def trigger_payment(payment_request: TriggerPaymentRequest):
    """
    Endpoint for MCP to trigger payment creation
    Accepts policy_name and premium, creates Stripe checkout session
    and stores it for the extension to retrieve
    """
    try:
        # Convert premium from dollars to cents
        amount_cents = int(payment_request.premium * 100)
        
        # Generate unique payment intent ID
        payment_intent_id = f"payment_{uuid.uuid4().hex[:12]}"
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        
        # Create payment record in DynamoDB
        payment_record = {
            'payment_intent_id': payment_intent_id,
            'user_id': user_id,
            'payment_status': 'pending',
            'amount': amount_cents,
            'currency': payment_request.currency,
            'product_name': payment_request.policy_name,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        payments_table.put_item(Item=payment_record)
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': payment_request.currency.lower(),
                    'unit_amount': amount_cents,
                    'product_data': {
                        'name': payment_request.policy_name,
                        'description': 'Travel Insurance Policy',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'http://localhost:8085/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url='http://localhost:8085/cancel',
            client_reference_id=payment_intent_id,
        )
        
        # Update payment record with Stripe session ID
        payments_table.update_item(
            Key={'payment_intent_id': payment_intent_id},
            UpdateExpression='SET stripe_session_id = :sid',
            ExpressionAttributeValues={':sid': checkout_session.id}
        )
        
        # Store in pending payments for extension to retrieve
        with pending_payments_lock:
            pending_payments[payment_intent_id] = {
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id,
                'policy_name': payment_request.policy_name,
                'premium': payment_request.premium,
                'amount_cents': amount_cents,
                'currency': payment_request.currency,
                'created_at': datetime.utcnow().isoformat(),
                'claimed': False
            }
        
        return JSONResponse({
            "success": True,
            "payment_intent_id": payment_intent_id,
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id,
            "message": "Payment checkout created successfully. Extension will retrieve it."
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/get-pending-payment")
async def get_pending_payment():
    """
    Endpoint for extension to poll for pending payments
    Returns the first unclaimed pending payment
    """
    try:
        with pending_payments_lock:
            # Find first unclaimed payment
            for payment_id, payment_data in pending_payments.items():
                if not payment_data.get('claimed', False):
                    # Mark as claimed
                    payment_data['claimed'] = True
                    return JSONResponse({
                        "has_payment": True,
                        "payment_intent_id": payment_id,
                        "checkout_url": payment_data['checkout_url'],
                        "session_id": payment_data['session_id'],
                        "policy_name": payment_data['policy_name'],
                        "premium": payment_data['premium'],
                        "amount_cents": payment_data['amount_cents'],
                        "currency": payment_data['currency']
                    })
            
            # No pending payments
            return JSONResponse({
                "has_payment": False,
                "message": "No pending payments"
            })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"has_payment": False, "error": str(e)}
        )

@app.post("/create-checkout")
async def create_checkout(payment_request: PaymentRequest):
    """
    Create a Stripe checkout session and payment record
    Returns the checkout URL for the extension to redirect to
    """
    try:
        # Generate unique payment intent ID
        payment_intent_id = f"payment_{uuid.uuid4().hex[:12]}"
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        
        # Create payment record in DynamoDB
        payment_record = {
            'payment_intent_id': payment_intent_id,
            'user_id': user_id,
            'payment_status': 'pending',
            'amount': payment_request.amount,
            'currency': payment_request.currency,
            'product_name': payment_request.product_name,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        payments_table.put_item(Item=payment_record)
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': payment_request.currency.lower(),
                    'unit_amount': payment_request.amount,
                    'product_data': {
                        'name': payment_request.product_name,
                        'description': 'Travel Insurance Policy',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'http://localhost:8085/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url='http://localhost:8085/cancel',
            client_reference_id=payment_intent_id,
        )
        
        # Update payment record with Stripe session ID
        payments_table.update_item(
            Key={'payment_intent_id': payment_intent_id},
            UpdateExpression='SET stripe_session_id = :sid',
            ExpressionAttributeValues={':sid': checkout_session.id}
        )
        
        return JSONResponse({
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id,
            "payment_intent_id": payment_intent_id
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/success", response_class=HTMLResponse)
async def payment_success(request: Request):
    session_id = request.query_params.get("session_id", "")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Payment Successful - LEA Insurance</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            
            .container {{
                background: white;
                border-radius: 16px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                padding: 40px;
                text-align: center;
                max-width: 500px;
                width: 100%;
            }}
            
            .success-icon {{
                width: 80px;
                height: 80px;
                background: #10b981;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 24px;
                animation: pulse 2s infinite;
            }}
            
            .success-icon svg {{
                width: 40px;
                height: 40px;
                color: white;
            }}
            
            @keyframes pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
                100% {{ transform: scale(1); }}
            }}
            
            h1 {{
                color: #1f2937;
                font-size: 28px;
                font-weight: 700;
                margin-bottom: 16px;
            }}
            
            .subtitle {{
                color: #6b7280;
                font-size: 16px;
                margin-bottom: 32px;
                line-height: 1.5;
            }}
            
            .info-box {{
                background: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 32px;
            }}
            
            .info-label {{
                color: #374151;
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 8px;
            }}
            
            .session-id {{
                color: #6b7280;
                font-family: 'Monaco', 'Menlo', monospace;
                font-size: 12px;
                word-break: break-all;
                background: #f3f4f6;
                padding: 8px;
                border-radius: 4px;
            }}
            
            .next-steps {{
                text-align: left;
                margin-bottom: 32px;
            }}
            
            .next-steps h3 {{
                color: #1f2937;
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 16px;
            }}
            
            .next-steps ul {{
                color: #4b5563;
                font-size: 14px;
                line-height: 1.6;
                padding-left: 20px;
            }}
            
            .next-steps li {{
                margin-bottom: 8px;
            }}
            
            .close-button {{
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.2s;
            }}
            
            .close-button:hover {{
                background: #5a67d8;
            }}
            
            .footer {{
                margin-top: 32px;
                padding-top: 24px;
                border-top: 1px solid #e5e7eb;
                color: #9ca3af;
                font-size: 12px;
            }}
            
            @media (max-width: 480px) {{
                .container {{
                    padding: 24px;
                }}
                
                h1 {{
                    font-size: 24px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success-icon">
                <svg fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                </svg>
            </div>
            
            <h1>Payment Successful!</h1>
            <p class="subtitle">
                Your travel insurance payment has been processed successfully. 
                Your policy will be created and sent to your email shortly.
            </p>
            
            <div class="info-box">
                <div class="info-label">Payment Session ID:</div>
                <div class="session-id">{session_id or 'Not provided'}</div>
            </div>
            
            <div class="next-steps">
                <h3>What happens next?</h3>
                <ul>
                    <li>You will receive a confirmation email with your policy details</li>
                    <li>Your policy documents will be available within 5-10 minutes to your email</li>
                    <li>Return to the chat to continue or ask any questions</li>
                    <li>Keep your payment confirmation for your records</li>
                </ul>
            </div>
            
            <div class="footer">
                LEA Insurance • Secure Payment Processing
            </div>
        </div>
        
        <script>
            if (window.opener) {{
                setTimeout(() => {{
                    window.close();
                }}, 10000);
            }}
            
            console.log('Payment Success - Session ID:', '{session_id}');
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/cancel", response_class=HTMLResponse)
async def payment_cancel(request: Request):
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Payment Cancelled - LEA Insurance</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 16px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                padding: 40px;
                text-align: center;
                max-width: 500px;
                width: 100%;
            }
            
            .cancel-icon {
                width: 80px;
                height: 80px;
                background: #ef4444;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 24px;
            }
            
            .cancel-icon svg {
                width: 40px;
                height: 40px;
                color: white;
            }
            
            h1 {
                color: #1f2937;
                font-size: 28px;
                font-weight: 700;
                margin-bottom: 16px;
            }
            
            .subtitle {
                color: #6b7280;
                font-size: 16px;
                margin-bottom: 32px;
                line-height: 1.5;
            }
            
            .actions {
                display: flex;
                gap: 16px;
                justify-content: center;
                flex-wrap: wrap;
                margin-bottom: 32px;
            }
            
            .button {
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                text-decoration: none;
                cursor: pointer;
                border: none;
                transition: all 0.2s;
                min-width: 120px;
            }
            
            .button-primary {
                background: #667eea;
                color: white;
            }
            
            .button-primary:hover {
                background: #5a67d8;
            }
            
            .button-secondary {
                background: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
            }
            
            .button-secondary:hover {
                background: #e5e7eb;
            }
            
            .footer {
                margin-top: 32px;
                padding-top: 24px;
                border-top: 1px solid #e5e7eb;
                color: #9ca3af;
                font-size: 12px;
            }
            
            @media (max-width: 480px) {
                .container {
                    padding: 24px;
                }
                
                h1 {
                    font-size: 24px;
                }
                
                .actions {
                    flex-direction: column;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="cancel-icon">
                <svg fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                </svg>
            </div>
            
            <h1>Payment Cancelled</h1>
            <p class="subtitle">
                Your payment was cancelled. No charges have been made to your account.
                You can return to the chat to try again or get help.
            </p>
            
            <div class="actions">
                <button class="button button-primary" onclick="window.close()">
                    Return to Chat
                </button>
            </div>
            
            <div class="footer">
                LEA Insurance • No Payment Processed
            </div>
        </div>
        
        <script>
            if (window.opener) {
                setTimeout(() => {
                    window.close();
                }, 15000);
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8085))
    uvicorn.run(app, host="0.0.0.0", port=port)

