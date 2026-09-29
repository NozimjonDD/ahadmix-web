#!/usr/bin/env bash
# =============================================================================
# setup_server.sh — First-time server provisioning script.
# Run as root on a fresh Ubuntu 22.04+ server.
# Usage:  sudo bash deploy/scripts/setup_server.sh
# =============================================================================
set -euo pipefail

# ---------------------------------------------------------------------------
# Guard: must run as root
# ---------------------------------------------------------------------------
if [[ "$EUID" -ne 0 ]]; then
    echo "Error: please run this script as root (sudo bash $0)" >&2
    exit 1
fi

APP_DIR="/var/www/ahadmix/ahadmix-web"
VENV_DIR="/var/www/ahadmix/venv"
APP_USER="ahadmix"
APP_HOME="/var/www/ahadmix"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
GREEN="\033[0;32m"
CYAN="\033[0;36m"
RESET="\033[0m"

step() {
    echo -e "\n${CYAN}==>${RESET} ${GREEN}$*${RESET}"
}

# ---------------------------------------------------------------------------
# 1. System packages
# ---------------------------------------------------------------------------
step "Updating package lists…"
apt-get update -y

step "Installing system packages…"
apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    nginx \
    postgresql \
    postgresql-contrib \
    redis-server \
    certbot \
    python3-certbot-nginx \
    git \
    curl

# ---------------------------------------------------------------------------
# 2. Application user
# ---------------------------------------------------------------------------
step "Creating system user '${APP_USER}'…"
if ! id -u "$APP_USER" &>/dev/null; then
    useradd --system --shell /bin/bash --home "$APP_HOME" --create-home "$APP_USER"
    echo "  User '${APP_USER}' created."
else
    echo "  User '${APP_USER}' already exists — skipping."
fi

# ---------------------------------------------------------------------------
# 3. Application directories
# ---------------------------------------------------------------------------
step "Creating application directories…"
mkdir -p "$APP_HOME"
chown -R "${APP_USER}:www-data" "$APP_HOME"
chmod 750 "$APP_HOME"

mkdir -p /var/log/ahadmix
chown -R "${APP_USER}:www-data" /var/log/ahadmix
chmod 775 /var/log/ahadmix

# ---------------------------------------------------------------------------
# 4. PostgreSQL — create role and database (idempotent)
# ---------------------------------------------------------------------------
step "Setting up PostgreSQL…"

# Ensure PostgreSQL is running
systemctl enable postgresql
systemctl start postgresql

sudo -u postgres psql -c "
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ahadmix') THEN
        CREATE ROLE ahadmix LOGIN;
        RAISE NOTICE 'Role ahadmix created.';
    ELSE
        RAISE NOTICE 'Role ahadmix already exists — skipping.';
    END IF;
END
\$\$;
"

sudo -u postgres psql -c "
SELECT 'CREATE DATABASE ahadmix_db OWNER ahadmix'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ahadmix_db')
\gexec
"

echo "  Remember to set a password for the ahadmix DB role:"
echo "    sudo -u postgres psql -c \"ALTER ROLE ahadmix PASSWORD 'your-secure-password';\""

# ---------------------------------------------------------------------------
# 5. Clone repository
# ---------------------------------------------------------------------------
step "Cloning application repository…"
if [[ ! -d "$APP_DIR/.git" ]]; then
    # git clone <YOUR_REPO_URL> "$APP_DIR"
    echo "  ⚠  Repo not cloned — uncomment the git clone line above and re-run, or clone manually:"
    echo "     git clone <YOUR_REPO_URL> $APP_DIR"
else
    echo "  Repository already present at $APP_DIR — skipping clone."
fi

# ---------------------------------------------------------------------------
# 6. Python virtual environment
# ---------------------------------------------------------------------------
step "Creating Python virtual environment…"
if [[ ! -d "$VENV_DIR" ]]; then
    python3.12 -m venv "$VENV_DIR"
fi
chown -R "${APP_USER}:www-data" "$VENV_DIR"

step "Installing Python dependencies…"
if [[ -f "$APP_DIR/requirements/production.txt" ]]; then
    sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install --quiet -r "$APP_DIR/requirements/production.txt"
else
    echo "  ⚠  $APP_DIR/requirements/production.txt not found — skipping pip install."
fi

# ---------------------------------------------------------------------------
# 7. systemd service
# ---------------------------------------------------------------------------
step "Installing systemd service…"
cp "$APP_DIR/deploy/systemd/ahadmix.service" /etc/systemd/system/ahadmix.service
systemctl daemon-reload
systemctl enable ahadmix
systemctl start ahadmix

# ---------------------------------------------------------------------------
# 8. Nginx
# ---------------------------------------------------------------------------
step "Installing Nginx configuration…"
cp "$APP_DIR/deploy/nginx/ahadmix.conf" /etc/nginx/sites-available/ahadmix

if [[ ! -L /etc/nginx/sites-enabled/ahadmix ]]; then
    ln -s /etc/nginx/sites-available/ahadmix /etc/nginx/sites-enabled/ahadmix
fi

# Remove default site if still enabled
if [[ -L /etc/nginx/sites-enabled/default ]]; then
    rm /etc/nginx/sites-enabled/default
fi

nginx -t
systemctl enable nginx
systemctl reload nginx

# ---------------------------------------------------------------------------
# Done — print next steps
# ---------------------------------------------------------------------------
echo ""
echo -e "${GREEN}======================================================${RESET}"
echo -e "${GREEN}  Server setup complete!${RESET}"
echo -e "${GREEN}======================================================${RESET}"
echo ""
echo "Next steps:"
echo ""
echo "  1. Copy the env template and fill in your secrets:"
echo "       cp $APP_DIR/deploy/.env.production $APP_DIR/.env"
echo "       nano $APP_DIR/.env"
echo ""
echo "  2. Obtain an SSL certificate with Certbot:"
echo "       certbot --nginx -d ahadmix.uz -d www.ahadmix.uz"
echo ""
echo "  3. Reload services after SSL is installed:"
echo "       systemctl reload nginx"
echo "       systemctl restart ahadmix"
echo ""
echo "  4. For subsequent deployments, run:"
echo "       bash $APP_DIR/deploy/scripts/deploy.sh"
echo "     or from your local machine:"
echo "       make deploy"
echo ""
