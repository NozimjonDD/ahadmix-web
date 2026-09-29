# Ahadmix Deployment Guide

This directory contains all files needed to deploy **ahadmix.uz** on a Ubuntu 22.04+ server.

```
deploy/
├── nginx/
│   └── ahadmix.conf          Nginx virtual-host config
├── gunicorn/
│   └── gunicorn.conf.py      Gunicorn Python config
├── systemd/
│   └── ahadmix.service       systemd service unit
├── scripts/
│   ├── setup_server.sh       First-time server provisioning
│   └── deploy.sh             Incremental deploy (git pull → restart)
├── .env.production           Env template (copy → .env and fill secrets)
└── README.md                 ← you are here
```

---

## 1. Prerequisites

- A fresh **Ubuntu 22.04+** server with root SSH access.
- DNS A-records for `ahadmix.uz` and `www.ahadmix.uz` pointing to the server IP.
- A local SSH alias `ahadmix-server` in `~/.ssh/config` (needed for `make deploy`).

```
# ~/.ssh/config example
Host ahadmix-server
    HostName <SERVER_IP>
    User ahadmix
    IdentityFile ~/.ssh/id_ed25519
```

---

## 2. First-Time Setup

### 2a. Run the provisioning script (as root on the server)

```bash
# Upload or clone the repo first, then:
sudo bash /var/www/ahadmix/ahadmix-web/deploy/scripts/setup_server.sh
```

The script will:
- Install system packages (Python 3.12, Nginx, PostgreSQL, Redis, Certbot, …)
- Create the `ahadmix` system user
- Create the PostgreSQL role and database
- Set up the Python virtual environment and install requirements
- Install and enable the systemd service
- Install and reload the Nginx config

### 2b. Configure environment variables

```bash
cp /var/www/ahadmix/ahadmix-web/deploy/.env.production \
   /var/www/ahadmix/ahadmix-web/.env
nano /var/www/ahadmix/ahadmix-web/.env
```

Fill in every `change-me` value:

| Key | Description |
|-----|-------------|
| `SECRET_KEY` | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DB_PASSWORD` | The password set for the `ahadmix` PostgreSQL role |
| `ADMIN_PASSWORD` | Set a unique password for the LED CITY editor at `/site-admin/`. The editor login is disabled while this is blank. |
| Others | Review and confirm default values |

LED CITY JSON files under `templates/data/` are local runtime data and are not tracked by Git. On a fresh checkout, Django copies the initial files from `templates/data_seed/` when the home page or site editor is first opened. Keep `templates/data/` when updating an existing server; those files contain edits made in the panel.

### 2c. Obtain an SSL certificate

```bash
sudo certbot --nginx -d ahadmix.uz -d www.ahadmix.uz
```

Certbot will automatically update the Nginx config and schedule auto-renewal.

### 2d. Restart services

```bash
sudo systemctl restart ahadmix
sudo systemctl reload nginx
```

---

## 3. Deploy Updates

### Via Makefile (from your local machine)

```bash
make deploy
```

### Manually (SSH into server)

```bash
ssh ahadmix-server
cd /var/www/ahadmix/ahadmix-web
bash deploy/scripts/deploy.sh
```

The deploy script performs:
1. `git pull origin main`
2. `pip install -r requirements/production.txt`
3. `python manage.py migrate --noinput`
4. `python manage.py collectstatic --noinput --clear`
5. `systemctl reload ahadmix`
6. `nginx -t && systemctl reload nginx`

---

## 4. Service Management

```bash
# Gunicorn (Django application)
sudo systemctl status  ahadmix
sudo systemctl start   ahadmix
sudo systemctl stop    ahadmix
sudo systemctl restart ahadmix
sudo systemctl reload  ahadmix   # graceful zero-downtime reload

# Nginx
sudo systemctl status  nginx
sudo nginx -t                    # test config before reload
sudo systemctl reload  nginx
```

---

## 5. Logs

```bash
# Gunicorn — via journalctl
journalctl -u ahadmix -f
journalctl -u ahadmix --since "1 hour ago"

# Gunicorn — log files
tail -f /var/log/ahadmix/gunicorn-access.log
tail -f /var/log/ahadmix/gunicorn-error.log

# Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Shortcuts (from local machine)
make logs         # journalctl -u ahadmix -f
make nginx-logs   # tail -f /var/log/nginx/error.log
```

---

## 6. Architecture

```
                        Internet
                           │
                   ┌───────▼────────┐
                   │    Nginx       │  :443 (SSL/TLS)
                   │  (reverse      │  :80  → redirect HTTPS
                   │   proxy)       │
                   └───────┬────────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
    /static/ │    /media/  │   /assets/  │  ← served directly by Nginx
    /data/   │             │             │     (no Gunicorn involved)
             │             │             │
             └─────────────┘─────────────┘
                           │
                           │  Unix socket
                           │  /run/ahadmix/gunicorn.sock
                           │
                   ┌───────▼────────┐
                   │   Gunicorn     │  sync workers
                   │  (WSGI server) │  cpu_count * 2 + 1
                   └───────┬────────┘
                           │
                   ┌───────▼────────┐
                   │    Django      │
                   │  application   │
                   └───┬───────┬────┘
                       │       │
              ┌────────▼─┐  ┌──▼──────────┐
              │PostgreSQL│  │    Redis     │
              │ ahadmix  │  │ cache/broker │
              │   _db    │  │  :6379       │
              └──────────┘  └─────────────┘
```
