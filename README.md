# EmailGuard — Production-Ready Email Validation & Intelligence Platform

A full-stack SaaS platform for real-time and bulk email validation, built with **Django + DRF** (backend) and **Next.js 14 + TypeScript** (frontend).

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Nginx                               │
│              (Reverse Proxy + Static Files)                 │
└─────────────┬───────────────────────┬───────────────────────┘
              │                       │
     ┌────────▼──────┐      ┌─────────▼──────┐
     │  Next.js 14   │      │  Django/DRF    │
     │  (Frontend)   │      │  (Backend API) │
     └───────────────┘      └────────┬───────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
     ┌────────▼──────┐    ┌──────────▼──────┐    ┌─────────▼──────┐
     │  PostgreSQL   │    │  Redis Cache    │    │ Celery Workers │
     │  (Database)   │    │  (Queue/Cache)  │    │ (Async Tasks)  │
     └───────────────┘    └─────────────────┘    └────────────────┘
```

## Features

### Email Validation Pipeline
1. **Syntax Validation** — RFC 5321/5322 compliance check
2. **Domain Extraction** — Parse local part & domain
3. **DNS Lookup** — Resolve domain DNS records
4. **MX Record Verification** — Check mail exchanger records
5. **SMTP Connection Check** — Connect to mail server
6. **Mailbox Verification** — RCPT TO verification
7. **Catch-All Detection** — Probe with random address
8. **Disposable Domain Check** — 500+ known providers
9. **Spam/Risk Analysis** — Pattern matching + database
10. **Score Calculation** — 0–100 quality score

### Scoring System
| Factor | Points |
|--------|--------|
| Syntax valid | +10 |
| MX records found | +10 |
| SMTP verified | +25 |
| Not catch-all | +10 |
| Not disposable | +5 |
| Not spam trap | +5 |
| Domain reputation | 0-15 |
| Not role account | +5 |
| Not free provider | +5 |
| Disposable penalty | -30 |
| Spam trap penalty | -40 |
| Blacklist penalty | -20 |

### API Response
```json
{
  "email": "john@example.com",
  "valid": true,
  "score": 87,
  "status": "valid",
  "is_disposable": false,
  "is_catch_all": false,
  "is_role_account": false,
  "is_free_provider": false,
  "smtp_check": true,
  "mx_found": true,
  "domain_reputation": "good",
  "risk_level": "low",
  "suggested_action": "safe_to_send"
}
```

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local frontend dev)
- Python 3.12+ (for local backend dev)

### 1. Clone & Configure

```bash
git clone <repo-url>
cd email_validation

# Backend environment
cp backend/.env.example backend/.env
# Edit backend/.env with your settings

# Frontend environment
cp frontend/.env.local.example frontend/.env.local
```

### 2. Start with Docker (Recommended)

```bash
# Development
docker-compose -f docker-compose.dev.yml up -d

# Production
docker-compose up -d
```

### 3. Create Admin User

```bash
docker exec -it emailguard_backend python manage.py createsuperuser
```

### 4. Access the Platform

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Django Admin | http://localhost:8000/admin |
| API Docs (Swagger) | http://localhost:8000/api/docs/ |
| API Docs (ReDoc) | http://localhost:8000/api/redoc/ |
| Flower (Celery) | http://localhost:5555 |

---

## Local Development (Without Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your local settings

# Run migrations
python manage.py migrate

# Load initial data (optional)
python manage.py loaddata fixtures/initial_data.json

# Start development server
python manage.py runserver

# Start Celery workers (separate terminals)
celery -A config worker -Q validation -c 4 --loglevel=debug
celery -A config worker -Q bulk -c 2 --loglevel=debug
celery -A config beat --loglevel=debug
```

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

---

## Project Structure

```
email_validation/
├── backend/
│   ├── apps/
│   │   ├── accounts/          # User auth, profiles, audit logs
│   │   ├── validation/        # Email validation, bulk jobs
│   │   │   └── engine/        # Validation pipeline
│   │   │       ├── validator.py    # Main orchestrator
│   │   │       ├── syntax.py       # Syntax/role/provider checks
│   │   │       ├── dns_checker.py  # MX/DNS lookup
│   │   │       ├── smtp_checker.py # SMTP verification
│   │   │       ├── disposable_checker.py
│   │   │       └── scorer.py       # Score calculation
│   │   ├── billing/           # Subscriptions, credits, Stripe
│   │   ├── api_keys/          # API key management
│   │   └── webhooks/          # Webhook delivery system
│   ├── config/                # Django settings, URLs, Celery
│   ├── core/                  # Shared utilities
│   └── requirements.txt
│
├── frontend/
│   └── src/
│       ├── app/               # Next.js App Router pages
│       │   ├── dashboard/     # Main dashboard
│       │   ├── validate/      # Single email checker
│       │   ├── bulk/          # Bulk upload & jobs
│       │   ├── history/       # Validation history
│       │   ├── api-keys/      # API key management
│       │   ├── billing/       # Credits & plans
│       │   ├── webhooks/      # Webhook config
│       │   ├── settings/      # Account settings
│       │   ├── login/         # Auth pages
│       │   └── register/
│       ├── components/        # Reusable UI components
│       ├── lib/               # API client, utilities
│       ├── store/             # Zustand state
│       └── types/             # TypeScript types
│
├── nginx/                     # Nginx config
├── docker-compose.yml         # Production Docker
├── docker-compose.dev.yml     # Development Docker
└── README.md
```

---

## API Reference

### Authentication
```
POST /api/v1/auth/register/       # Register
POST /api/v1/auth/login/          # Login
POST /api/v1/auth/logout/         # Logout
GET  /api/v1/auth/me/             # Current user
POST /api/v1/auth/token/refresh/  # Refresh JWT
```

### Validation
```
POST /api/v1/validation/validate/          # Single email
GET  /api/v1/validation/history/           # History (paginated)
GET  /api/v1/validation/stats/             # Statistics
POST /api/v1/validation/bulk/              # Upload CSV
GET  /api/v1/validation/bulk/{id}/         # Job status
GET  /api/v1/validation/bulk/{id}/results/ # Job results
GET  /api/v1/validation/bulk/{id}/download/# Download CSV
```

### Management
```
GET/POST   /api/v1/api-keys/        # API keys
DELETE     /api/v1/api-keys/{id}/   # Revoke key
GET/POST   /api/v1/webhooks/        # Webhooks
GET        /api/v1/billing/subscription/
GET        /api/v1/billing/plans/
POST       /api/v1/billing/checkout/
```

### External API Authentication
```bash
# Using JWT Bearer token
curl -H "Authorization: Bearer <access_token>" ...

# Using API Key
curl -H "X-API-Key: eg_your_key_here" ...
```

---

## Email Scoring Algorithm

```python
score = 0
if syntax_valid:      score += 10
if mx_found:          score += 10
if smtp_check:        score += 25
if not catch_all:     score += 10
if not disposable:    score += 5
if not spam_trap:     score += 5
score += reputation_score  # 0-15
if not role_account:  score += 5
if not free_provider: score += 5
if is_blacklisted:    score -= 20
if is_spam_trap:      score -= 40
if is_disposable:     score -= 30

# Verdict
if score >= 70 and smtp_check: status = "valid"
elif score >= 40:              status = "risky"
elif is_catch_all:             status = "catch_all"
elif is_disposable:            status = "disposable"
elif is_spam_trap:             status = "spam_trap"
else:                          status = "unknown"
```

---

## Production Deployment

### Environment Variables (Required)
```env
SECRET_KEY=<strong-random-key>
DEBUG=False
DB_NAME=emailvalidation
DB_USER=postgres
DB_PASSWORD=<strong-password>
REDIS_URL=redis://redis:6379/0
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Scaling Workers
```bash
# Scale bulk workers for high volume
docker-compose up -d --scale celery_bulk=4

# Scale validation workers
docker-compose up -d --scale celery_validation=8
```

### Celery Queue Strategy
| Queue | Workers | Concurrency | Use |
|-------|---------|-------------|-----|
| `validation` | 4 | 4 | Single email checks |
| `bulk` | 2-8 | 8 | Batch processing |
| `webhooks` | 1-2 | 2 | Webhook delivery |

---

## Credits System

- Free plan: **100 credits**
- 1 credit = 1 email validation
- Credits deducted on validation request
- Insufficient credits → 402 Payment Required
- Stripe integration for purchasing packs

---

## Security

- JWT authentication (1h access + 30d refresh)
- API key hashing (SHA-256)
- CORS configuration
- Rate limiting (DRF throttling)
- IP whitelist per API key
- Audit logs for all key actions
- HTTPS enforcement in production
