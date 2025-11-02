# Stripe & DynamoDB Setup Guide

This guide will help you set up Stripe and DynamoDB for the payment services.

## Prerequisites

- Docker and Docker Compose installed
- Stripe account (free test account works)
- Python 3.11+ (for local testing)

## Step 1: Stripe Setup

### 1.1 Create or Login to Stripe Account

1. Go to [https://stripe.com](https://stripe.com)
2. Sign up or log in to your account
3. Make sure you're in **Test Mode** (toggle in top right)

### 1.2 Get Your API Keys

1. Navigate to **Developers → API keys** in Stripe Dashboard
2. Copy your **Secret key** (starts with `sk_test_`)
3. Copy your **Publishable key** (starts with `pk_test_`) - optional, but useful for frontend

### 1.3 Set Up Webhook Endpoint (For Local Development)

You have two options:

#### Option A: Use Stripe CLI (Recommended for Local Development)

1. Install Stripe CLI:
   - Windows: Download from [https://github.com/stripe/stripe-cli/releases](https://github.com/stripe/stripe-cli/releases)
   - Mac: `brew install stripe/stripe-cli/stripe`
   - Linux: See [https://stripe.com/docs/stripe-cli](https://stripe.com/docs/stripe-cli)

2. Login to Stripe CLI:
   ```bash
   stripe login
   ```

3. Forward webhooks to local server:
   ```bash
   stripe listen --forward-to localhost:8086/webhook/stripe
   ```
   
   This will give you a webhook signing secret (starts with `whsec_`)

#### Option B: Set Up Webhook in Stripe Dashboard

1. In Stripe Dashboard, go to **Developers → Webhooks**
2. Click **Add endpoint**
3. Endpoint URL: `https://your-domain.com/webhook/stripe` (for production)
   - For local testing, you'll need a tunneling service like ngrok
4. Select events to listen to:
   - `checkout.session.completed`
   - `checkout.session.expired`
   - `payment_intent.payment_failed`
5. Copy the **Signing secret** (starts with `whsec_`)

### 1.4 Get Webhook Secret

- If using Stripe CLI: The secret is shown when you run `stripe listen`
- If using Dashboard: Copy from **Developers → Webhooks → Your endpoint → Signing secret**

## Step 2: Environment Configuration

1. Copy the example environment file:
   ```bash
   cd Payments
   copy .env.example .env
   ```
   (On Mac/Linux: `cp .env.example .env`)

2. Edit `.env` and add your Stripe webhook secret:
   ```
   STRIPE_WEBHOOK_SECRET=whsec_your_actual_secret_here
   STRIPE_SECRET_KEY=sk_test_your_secret_key_here
   ```

## Step 3: Start DynamoDB and Services

1. Make sure Docker is running
2. Start all services:
   ```bash
   cd Payments
   docker-compose up -d
   ```

This will:
- Start DynamoDB Local on port 8000
- Create the `lea-payments-local` table automatically
- Start DynamoDB Admin UI on port 8010
- Start Stripe webhook service on port 8086
- Start payment pages service on port 8085

## Step 4: Verify Setup

### 4.1 Check Services are Running

```bash
docker-compose ps
```

All services should show "Up" status.

### 4.2 Check Health Endpoints

```bash
# Stripe webhook service
curl http://localhost:8086/health

# Payment pages service
curl http://localhost:8085/health
```

Both should return `{"status":"ok"}`.

### 4.3 View DynamoDB Tables

Open in browser: [http://localhost:8010](http://localhost:8010)

You should see the `lea-payments-local` table with its indexes.

### 4.4 Test Payment Flow (Optional)

If you want to test the complete payment flow:

```bash
cd Payments
pip install -r requirements.txt
python test_payment_flow.py
```

This will:
1. Create a test payment record
2. Generate a Stripe checkout link
3. Guide you through making a test payment
4. Verify webhook processing works

**Test Card:** `4242 4242 4242 4242` (use any future expiry, any CVC, any ZIP)

## Step 5: Local Development with Stripe CLI

For local development, use Stripe CLI to forward webhooks:

1. In one terminal, start Stripe CLI:
   ```bash
   stripe listen --forward-to localhost:8086/webhook/stripe
   ```
   
   Copy the webhook secret it provides (e.g., `whsec_...`)

2. Update your `.env` file with the CLI webhook secret

3. Keep the CLI running while testing payments

## Troubleshooting

### Services won't start

- **Ports in use**: Ensure ports 8000, 8010, 8085, 8086 are available
- **Docker not running**: Make sure Docker Desktop is running
- **Missing .env file**: Ensure `.env` exists with `STRIPE_WEBHOOK_SECRET`

### Webhook not receiving events

- **Webhook secret incorrect**: Double-check `STRIPE_WEBHOOK_SECRET` in `.env`
- **Service not running**: Check `docker-compose ps` and logs: `docker-compose logs stripe-webhook`
- **Stripe CLI not forwarding**: If using CLI, ensure it's running: `stripe listen --forward-to localhost:8086/webhook/stripe`

### DynamoDB table not created

- Check init container logs: `docker-compose logs dynamodb-init-hackathon`
- Table might already exist (this is OK)
- Manual creation: Run `python scripts/init_payments_table.py` (set `DDB_ENDPOINT=http://localhost:8000`)

### Payment status not updating

- Verify webhook received event: `docker-compose logs -f stripe-webhook`
- Ensure `client_reference_id` in Stripe session matches `payment_intent_id` in DB
- Check DynamoDB: Visit http://localhost:8010

## Useful Commands

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f stripe-webhook
docker-compose logs -f payment-pages

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Rebuild services
docker-compose down
docker-compose build
docker-compose up -d
```

## Next Steps

Once set up, you can:
- Create payment records in DynamoDB
- Generate Stripe checkout sessions
- Handle webhook events automatically
- Test payment flows end-to-end

For integration examples, see `test_payment_flow.py`.

