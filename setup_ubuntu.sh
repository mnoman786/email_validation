#!/usr/bin/env bash
# =============================================================================
#  EmailGuard — Ubuntu Setup Script (no Docker, systemd services)
#  Ports:  Backend → 9002   |   Frontend → 5000
#
#  Usage:
#    sudo bash setup_ubuntu.sh              # full first-time install
#    sudo bash setup_ubuntu.sh --update     # pull latest code & restart
#    sudo bash setup_ubuntu.sh --restart    # restart services only
# =============================================================================
set -euo pipefail

# ── Colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'

info()    { echo -e "${CYAN}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC}   $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
error()   { echo -e "${RED}[ERR]${NC}  $*"; exit 1; }

# ── Config ───────────────────────────────────────────────────────────────────
APP_DIR="/opt/emailguard"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
LOG_DIR="/var/log/emailguard"
SERVICE_USER="www-data"

BACKEND_PORT=9002
FRONTEND_PORT=5000

# ── Mode detection ────────────────────────────────────────────────────────────
MODE="install"
[[ "${1:-}" == "--update" ]]  && MODE="update"
[[ "${1:-}" == "--restart" ]] && MODE="restart"

# ── Root check ────────────────────────────────────────────────────────────────
[[ "$EUID" -ne 0 ]] && error "Please run as root:  sudo bash setup_ubuntu.sh"

# =============================================================================
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       EmailGuard — Ubuntu Setup              ║${NC}"
echo -e "${BLUE}║  Backend :${NC} http://localhost:${BACKEND_PORT}            ${BLUE}║${NC}"
echo -e "${BLUE}║  Frontend:${NC} http://localhost:${FRONTEND_PORT}            ${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════╝${NC}"
echo ""

# =============================================================================
#  RESTART ONLY
# =============================================================================
if [[ "$MODE" == "restart" ]]; then
    info "Restarting services..."
    systemctl restart emailguard-backend emailguard-frontend
    systemctl status emailguard-backend --no-pager -l
    systemctl status emailguard-frontend --no-pager -l
    success "Services restarted."
    exit 0
fi

# =============================================================================
#  UPDATE
# =============================================================================
if [[ "$MODE" == "update" ]]; then
    info "Stopping services for update..."
    systemctl stop emailguard-backend emailguard-frontend || true

    info "Updating backend dependencies..."
    cd "$BACKEND_DIR"
    sudo -u "$SERVICE_USER" venv/bin/pip install -r requirements_local.txt -q
    DJANGO_SETTINGS_MODULE=config.settings.local venv/bin/python manage.py migrate --run-syncdb
    DJANGO_SETTINGS_MODULE=config.settings.local venv/bin/python manage.py collectstatic --noinput -v 0
    DJANGO_SETTINGS_MODULE=config.settings.local venv/bin/python manage.py update_disposable_domains --source github || \
        venv/bin/python manage.py update_disposable_domains --source local

    info "Rebuilding frontend..."
    cd "$FRONTEND_DIR"
    sudo -u "$SERVICE_USER" npm ci --silent
    sudo -u "$SERVICE_USER" npm run build

    info "Restarting services..."
    systemctl start emailguard-backend emailguard-frontend
    success "Update complete."
    exit 0
fi

# =============================================================================
#  FULL INSTALL
# =============================================================================

# ── 1. System packages ────────────────────────────────────────────────────────
info "[1/9] Installing system packages..."
apt-get update -qq
apt-get install -y -qq \
    python3 python3-pip python3-venv python3-dev \
    build-essential libpq-dev \
    curl git wget \
    nginx \
    lsb-release ca-certificates gnupg

# ── 2. Node.js (LTS 20.x) ────────────────────────────────────────────────────
info "[2/9] Installing Node.js 20 LTS..."
if ! command -v node &>/dev/null || [[ "$(node -v | cut -d. -f1 | tr -d v)" -lt 18 ]]; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - 2>/dev/null
    apt-get install -y -qq nodejs
fi
success "Node $(node -v)  |  npm $(npm -v)"

# ── 3. App directory ─────────────────────────────────────────────────────────
info "[3/9] Setting up app directory at $APP_DIR..."
mkdir -p "$APP_DIR" "$LOG_DIR"

# Detect where this script lives (the project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
info "  Copying project from: $SCRIPT_DIR"
rsync -a --exclude=".git" --exclude="node_modules" --exclude="venv" \
      --exclude="__pycache__" --exclude="*.pyc" --exclude=".next" \
      "$SCRIPT_DIR/" "$APP_DIR/"

chown -R "$SERVICE_USER:$SERVICE_USER" "$APP_DIR" "$LOG_DIR"

# ── 4. Backend Python venv ────────────────────────────────────────────────────
info "[4/9] Setting up Python virtual environment..."
cd "$BACKEND_DIR"
if [[ ! -d venv ]]; then
    python3 -m venv venv
fi
venv/bin/pip install --upgrade pip wheel -q
venv/bin/pip install gunicorn -q
venv/bin/pip install -r requirements_local.txt -q
success "Python deps installed."

# ── 5. Backend .env ───────────────────────────────────────────────────────────
info "[5/9] Configuring backend environment..."
if [[ ! -f "$BACKEND_DIR/.env" ]]; then
    cat > "$BACKEND_DIR/.env" <<EOF
DJANGO_SETTINGS_MODULE=config.settings.local
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
FRONTEND_URL=http://localhost:${FRONTEND_PORT}
STRIPE_PUBLIC_KEY=pk_test_placeholder
STRIPE_SECRET_KEY=sk_test_placeholder
STRIPE_WEBHOOK_SECRET=
EOF
    success ".env created at $BACKEND_DIR/.env"
else
    warn ".env already exists — skipping."
fi
chown "$SERVICE_USER:$SERVICE_USER" "$BACKEND_DIR/.env"
chmod 600 "$BACKEND_DIR/.env"

# ── 6. Django setup ───────────────────────────────────────────────────────────
info "[6/9] Running Django setup (migrate, collectstatic, seed)..."
export DJANGO_SETTINGS_MODULE=config.settings.local

venv/bin/python manage.py migrate --run-syncdb 2>&1 | tail -5

venv/bin/python manage.py collectstatic --noinput -v 0 2>/dev/null || true

venv/bin/python manage.py shell -c "
from django.contrib.auth import get_user_model
from apps.billing.models import Subscription, CreditPack
User = get_user_model()
if not User.objects.filter(email='admin@emailguard.io').exists():
    u = User.objects.create_superuser('admin@emailguard.io', 'admin123')
    u.first_name = 'Admin'
    u.is_verified = True
    u.save()
    Subscription.objects.get_or_create(user=u, defaults={'plan': 'pro', 'available_credits': 99999})
    print('[seed] Admin user created: admin@emailguard.io / admin123')
else:
    print('[seed] Admin user already exists')
packs = [
    ('Starter Pack',    1000,    9.99, False),
    ('Growth Pack',     5000,   29.99, True),
    ('Pro Pack',       25000,   99.99, False),
    ('Enterprise Pack',100000, 299.99, False),
]
for name, credits, price, popular in packs:
    CreditPack.objects.get_or_create(name=name, defaults={'credits': credits, 'price_usd': price, 'is_active': True, 'is_popular': popular})
print('[seed] Credit packs ready')
" 2>&1

info "  Importing disposable domain blocklist..."
venv/bin/python manage.py update_disposable_domains --source github 2>&1 | tail -3 || \
    venv/bin/python manage.py update_disposable_domains --source local 2>&1 | tail -3

chown -R "$SERVICE_USER:$SERVICE_USER" "$BACKEND_DIR"

# ── 7. Frontend build ─────────────────────────────────────────────────────────
info "[7/9] Building Next.js frontend..."
cd "$FRONTEND_DIR"

cat > "$FRONTEND_DIR/.env.local" <<EOF
NEXT_PUBLIC_API_URL=http://localhost:${BACKEND_PORT}
EOF

chown "$SERVICE_USER:$SERVICE_USER" "$FRONTEND_DIR/.env.local"

sudo -u "$SERVICE_USER" npm ci --silent
sudo -u "$SERVICE_USER" npm run build

success "Frontend build complete."

# ── 8. systemd services ───────────────────────────────────────────────────────
info "[8/9] Installing systemd services..."

# Backend service
cat > /etc/systemd/system/emailguard-backend.service <<EOF
[Unit]
Description=EmailGuard Django Backend (Gunicorn)
After=network.target

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_USER}
WorkingDirectory=${BACKEND_DIR}
EnvironmentFile=${BACKEND_DIR}/.env
Environment="DJANGO_SETTINGS_MODULE=config.settings.local"
Environment="PATH=${BACKEND_DIR}/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=${BACKEND_DIR}/venv/bin/gunicorn \\
    config.wsgi:application \\
    --bind 0.0.0.0:${BACKEND_PORT} \\
    --workers 3 \\
    --worker-class sync \\
    --timeout 120 \\
    --keep-alive 5 \\
    --max-requests 1000 \\
    --max-requests-jitter 100 \\
    --log-level info \\
    --access-logfile ${LOG_DIR}/backend-access.log \\
    --error-logfile ${LOG_DIR}/backend-error.log
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=emailguard-backend
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Frontend service
NODE_BIN=$(command -v node)
cat > /etc/systemd/system/emailguard-frontend.service <<EOF
[Unit]
Description=EmailGuard Next.js Frontend
After=network.target emailguard-backend.service

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_USER}
WorkingDirectory=${FRONTEND_DIR}
Environment="NODE_ENV=production"
Environment="PORT=${FRONTEND_PORT}"
Environment="NEXT_PUBLIC_API_URL=http://localhost:${BACKEND_PORT}"
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=${NODE_BIN} node_modules/.bin/next start --port ${FRONTEND_PORT}
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=emailguard-frontend
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable emailguard-backend emailguard-frontend
success "systemd services installed and enabled."

# ── 9. nginx reverse proxy (optional, but configured) ─────────────────────────
info "[9/9] Configuring Nginx reverse proxy..."
cat > /etc/nginx/sites-available/emailguard <<EOF
# EmailGuard — Nginx reverse proxy
# Frontend at /         →  :${FRONTEND_PORT}
# Backend  at /api/     →  :${BACKEND_PORT}
# Backend  at /admin/   →  :${BACKEND_PORT}

server {
    listen 80;
    server_name _;

    client_max_body_size 50M;

    # Backend API + Admin
    location ~ ^/(api|admin|static-django|media)/ {
        proxy_pass         http://127.0.0.1:${BACKEND_PORT};
        proxy_set_header   Host              \$host;
        proxy_set_header   X-Real-IP         \$remote_addr;
        proxy_set_header   X-Forwarded-For   \$proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 10s;
    }

    # Next.js frontend (everything else)
    location / {
        proxy_pass         http://127.0.0.1:${FRONTEND_PORT};
        proxy_set_header   Host              \$host;
        proxy_set_header   X-Real-IP         \$remote_addr;
        proxy_set_header   X-Forwarded-For   \$proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto \$scheme;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade           \$http_upgrade;
        proxy_set_header   Connection        "upgrade";
    }
}
EOF

ln -sf /etc/nginx/sites-available/emailguard /etc/nginx/sites-enabled/emailguard
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
nginx -t && systemctl reload nginx
success "Nginx configured."

# ── Start services ────────────────────────────────────────────────────────────
info "Starting services..."
systemctl start emailguard-backend
sleep 2
systemctl start emailguard-frontend

# ── Final status ──────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║               EmailGuard is UP and RUNNING                  ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║${NC}  Frontend   :  http://localhost:${FRONTEND_PORT}                     ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  Backend API:  http://localhost:${BACKEND_PORT}/api/v1/             ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  API Docs   :  http://localhost:${BACKEND_PORT}/api/docs/            ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  Django Admin: http://localhost:${BACKEND_PORT}/admin/               ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  Via Nginx  :  http://localhost  (port 80)               ${GREEN}║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║${NC}  Admin login: admin@emailguard.io  /  admin123           ${GREEN}║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║${NC}  Manage services:                                        ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}    systemctl status emailguard-backend                   ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}    systemctl status emailguard-frontend                  ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}    sudo bash setup_ubuntu.sh --restart                   ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}    sudo bash setup_ubuntu.sh --update                    ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  View logs:                                              ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}    journalctl -u emailguard-backend -f                   ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}    journalctl -u emailguard-frontend -f                  ${GREEN}║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

systemctl is-active emailguard-backend  && success "emailguard-backend  — active" || warn "emailguard-backend  — check logs"
systemctl is-active emailguard-frontend && success "emailguard-frontend — active" || warn "emailguard-frontend — check logs"
