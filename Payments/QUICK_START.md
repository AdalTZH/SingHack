# Quick Start - Stripe & DynamoDB Setup

## Quick Setup Steps

### 1. Create `.env` File

Create a `.env` file in the `Payments` folder with this content:

```bash
# Stripe Configuration
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here

# AWS Configuration (defaults for local DynamoDB)
AWS_REGION=ap-southeast-1
DYNAMODB_PAYMENTS_TABLE=lea-payments-local
```

### 2. Get Stripe Credentials

#### Option A: Using Stripe CLI (Easiest for Local Development)

1. **Install Stripe CLI**: 
   - Windows: Download from https://github.com/stripe/stripe-cli/releases
   - Or use: `scoop install stripe` (if you have Scoop)

2. **Login to Stripe**:
   ```bash
   stripe login
   ```

3. **Start forwarding webhooks**:
   ```bash
   stripe listen --forward-to localhost:8086/webhook/stripe
   ```
   
   This will output a webhook secret like `whsec_...` - **copy this!**

4. **Get your API keys**:
   - Go to https://dashboard.stripe.com/apikeys
   - Copy your **Test mode Secret key** (starts with `sk_test_`)

5. **Update `.env` file** with the webhook secret and secret key

#### Option B: Using Stripe Dashboard

1. Go to https://dashboard.stripe.com/test/apikeys
2. Copy your **Secret key** (starts with `sk_test_`)
3. Go to https://dashboard.stripe.com/test/webhooks
4. Add endpoint: `https://your-domain.com/webhook/stripe`
   - For local: Use ngrok or similar tunneling service
5. Copy the **Signing secret** (starts with `whsec_`)
6. Update `.env` file

### 3. Start Services with Docker

```bash
cd Payments
docker-compose up -d
```

This starts:
- ✅ DynamoDB Local (port 8000)
- ✅ DynamoDB Admin UI (port 8010)
- ✅ Stripe Webhook Service (port 8086)
- ✅ Payment Pages Service (port 8085)

### 4. Verify Everything Works

```bash
# Check services are running
docker-compose ps

# Check health endpoints
curl http://localhost:8086/health
curl http://localhost:8085/health

# View DynamoDB in browser
# Open: http://localhost:8010
```

### 5. Test Payment Flow (Optional)

```bash
# Install test dependencies
pip install -r requirements.txt

# Run interactive test
python test_payment_flow.py
```

Use test card: `4242 4242 4242 4242`

## Troubleshooting

### Docker won't start
- Ensure Docker Desktop is running
- Check ports 8000, 8010, 8085, 8086 are free

### Webhook not working
- Ensure `STRIPE_WEBHOOK_SECRET` is set in `.env`
- If using Stripe CLI, keep `stripe listen` running
- Check logs: `docker-compose logs -f stripe-webhook`

### Need Help?
See `SETUP_GUIDE.md` for detailed instructions.




