# Théoria SaaS

Extension SaaS du projet Théoria - Copilote vocal personnel avec auth, billing et usage metering.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    THÉORIA SAAS                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🖥️  DESKTOP CLIENT (ton code existant étendu)              │
│     ├── run_saas_daemon.py    # Daemon SaaS avec auth       │
│     └── saas_client.py        # Auth manager + API client   │
│                         │                                    │
│                         ▼ JWT Auth                          │
│                                                              │
│  ⚙️  API SERVER (SaaS)                                      │
│     ├── run_saas_api.py       # API avec SaaS routes        │
│     └── saas/                 # Modules SaaS                │
│         ├── auth.py           # JWT + OAuth                 │
│         ├── billing.py        # Stripe integration          │
│         ├── usage.py          # Metering & quotas           │
│         ├── routes.py         # API routes SaaS             │
│         └── models.py         # Database models             │
│                                                              │
│  🗄️  POSTGRESQL                                              │
│     ├── Users, Subscriptions, Plans                         │
│     └── Usage events                                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Setup Database

```bash
# Install PostgreSQL (macOS)
brew install postgresql@14
brew services start postgresql@14

# Create database
createdb theoria
```

### 2. Setup Environment

```bash
cp .env.saas.example .env
# Edit .env with your keys:
# - MISTRAL_API_KEY
# - JWT_SECRET (generate: openssl rand -base64 32)
# - DATABASE_URL
# - STRIPE_SECRET_KEY (optional for now)
```

### 3. Run SaaS API Server

```bash
# Install dependencies
pip install -r requirements.txt

# Run API
python run_saas_api.py

# API will be available at http://127.0.0.1:8090
# Docs: http://127.0.0.1:8090/docs
# Landing: http://127.0.0.1:8090/
# App web: http://127.0.0.1:8090/app
```

### 4. Run SaaS Desktop Client

```bash
# Login
python run_saas_daemon.py login your@email.com

# Check status
python run_saas_daemon.py status

# Run daemon
python run_saas_daemon.py run
```

## API Endpoints

### Auth
- `POST /v1/auth/login` - Login with email (magic link style)
- `POST /v1/auth/refresh` - Refresh access token
- `POST /v1/auth/logout` - Logout

### User
- `GET /v1/me` - Get current user
- `GET /v1/me/settings` - Get user settings
- `PATCH /v1/me/settings` - Update settings

### Transcription
- `POST /v1/transcribe` - Transcribe audio (auth required)

### Usage
- `GET /v1/usage/current-period` - Get usage stats

### Billing
- `GET /v1/plans` - List available plans
- `POST /v1/billing/checkout-session` - Create Stripe checkout
- `POST /v1/billing/portal-session` - Access customer portal
- `POST /v1/stripe/webhook` - Stripe webhooks

## Plans

| Plan | Minutes/Month | Price |
|------|--------------|-------|
| Free | 30 | €0 |
| Pro | 300 | €12 |
| Power | Unlimited | €29 |

## Run Mode

This repository is now SaaS-first. Use these commands:

```bash
python run_saas_api.py
python run_saas_daemon.py login you@email.com
python run_saas_daemon.py run
```
