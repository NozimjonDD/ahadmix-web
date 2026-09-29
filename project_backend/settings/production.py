from .base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
DEBUG = False

ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "ahadmix.uz,www.ahadmix.uz").split(",")]

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

CSRF_TRUSTED_ORIGINS = [
    "https://ahadmix.nozim-dev.uz",
    "http://localhost:3002",
    "http://localhost:3000",
    "https://www.ahadmix.nozim-dev.uz",
]

CORS_ALLOWED_ORIGINS = [
    "https://ahadmix.nozim-dev.uz",
    "https://www.ahadmix.nozim-dev.uz",
]

# ---------------------------------------------------------------------------
# Static & Media
# ---------------------------------------------------------------------------
# BASE_DIR points to project_backend/, so .parent is the project root.
STATIC_ROOT = BASE_DIR.parent / "static"
MEDIA_ROOT = BASE_DIR.parent / "media"

# ---------------------------------------------------------------------------
# Cache (Redis)
# ---------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("CACHE_REDIS_URL", "redis://127.0.0.1:6379/1"),
    }
}
