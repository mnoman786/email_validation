#!/bin/bash
# EmailGuard Initial Setup Script

set -e

echo "================================"
echo "  EmailGuard Platform Setup"
echo "================================"

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed. Aborting." >&2; exit 1; }

# Setup environment files
if [ ! -f backend/.env ]; then
    echo "Creating backend .env from example..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env with your settings before continuing."
    echo "   Required: SECRET_KEY, DB_PASSWORD, STRIPE_SECRET_KEY"
fi

if [ ! -f frontend/.env.local ]; then
    echo "Creating frontend .env.local from example..."
    cp frontend/.env.local.example frontend/.env.local
fi

# Start services
echo "Starting Docker services..."
docker-compose -f docker-compose.dev.yml up -d db redis

echo "Waiting for database to be ready..."
sleep 5

# Run migrations
echo "Running database migrations..."
docker-compose -f docker-compose.dev.yml run --rm backend python manage.py migrate

# Create superuser
echo "Creating superuser..."
docker-compose -f docker-compose.dev.yml run --rm backend python manage.py createsuperuser --noinput \
    --email admin@emailguard.io || true

# Load sample credit packs
docker-compose -f docker-compose.dev.yml run --rm backend python manage.py shell -c "
from apps.billing.models import CreditPack
CreditPack.objects.get_or_create(name='Starter Pack', defaults={'credits': 1000, 'price_usd': 9.99, 'is_active': True})
CreditPack.objects.get_or_create(name='Growth Pack', defaults={'credits': 5000, 'price_usd': 29.99, 'is_active': True, 'is_popular': True})
CreditPack.objects.get_or_create(name='Pro Pack', defaults={'credits': 25000, 'price_usd': 99.99, 'is_active': True})
CreditPack.objects.get_or_create(name='Enterprise Pack', defaults={'credits': 100000, 'price_usd': 299.99, 'is_active': True})
print('Credit packs created!')
"

# Start all services
echo "Starting all services..."
docker-compose -f docker-compose.dev.yml up -d

echo ""
echo "================================"
echo "  Setup Complete! 🎉"
echo "================================"
echo ""
echo "Access the platform:"
echo "  Frontend:     http://localhost:3000"
echo "  API Docs:     http://localhost:8000/api/docs/"
echo "  Django Admin: http://localhost:8000/admin"
echo "  Flower:       (not started in dev)"
echo ""
echo "API Example:"
echo "  curl -X POST http://localhost:8000/api/v1/auth/login/ \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"email\": \"admin@emailguard.io\", \"password\": \"your_password\"}'"
echo ""
