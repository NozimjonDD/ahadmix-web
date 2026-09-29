#!/usr/bin/env bash
# =============================================================================
# deploy.sh — Run ON the server after SSH-ing in.
# Usage:  bash deploy/scripts/deploy.sh
# Or via Makefile:  make deploy   (SSH + runs this script remotely)
# chmod +x deploy/scripts/deploy.sh
# =============================================================================
set -euo pipefail

APP_DIR="/var/local/ahadmix/ahadmix-web"
VENV_DIR="/var/local/ahadmix/ahadmix-web/venv"

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
# Steps
# ---------------------------------------------------------------------------
cd "$APP_DIR"

step "Pulling latest code from git…"
git pull origin main

step "Activating virtual environment…"
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

step "Installing / updating Python dependencies…"
pip install -r requirements/production.txt --quiet

step "Running database migrations…"
python manage.py migrate --noinput

step "Collecting static files…"
python manage.py collectstatic --noinput --clear

step "Ensuring log directory exists…"
mkdir -p /var/log/ahadmix

step "Reloading Gunicorn…"
sudo systemctl reload ahadmix

step "Testing and reloading Nginx…"
sudo nginx -t
sudo systemctl reload nginx

echo -e "\n${GREEN}✔  Deployment complete!${RESET}\n"
