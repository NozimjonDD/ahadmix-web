"""
Gunicorn configuration for ahadmix.uz
Reference: https://docs.gunicorn.org/en/stable/settings.html
"""

import multiprocessing

# ---------------------------------------------------------------------------
# Server socket
# ---------------------------------------------------------------------------
bind = "unix:/run/ahadmix/gunicorn.sock"

# ---------------------------------------------------------------------------
# Worker processes
# ---------------------------------------------------------------------------
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
keepalive = 5

# ---------------------------------------------------------------------------
# Request limits (helps prevent memory leaks)
# ---------------------------------------------------------------------------
max_requests = 1000
max_requests_jitter = 100

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
loglevel = "info"
accesslog = "/var/log/ahadmix/gunicorn-access.log"
errorlog = "/var/log/ahadmix/gunicorn-error.log"
capture_output = True

# ---------------------------------------------------------------------------
# Process naming
# ---------------------------------------------------------------------------
proc_name = "ahadmix"
