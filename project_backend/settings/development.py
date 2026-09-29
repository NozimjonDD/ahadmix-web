from .base import *

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

CSRF_COOKIE_NAME = "csrftoken"
CSRF_HEADER_NAME = "HTTP_X_CSRFTOKEN"

# CSRF_TRUSTED_ORIGINS = [
#     'https://www.e-store.uz',
#     'https://e-store.uz',
# ]

# Use in-memory cache locally — no Redis required in development
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

STATICFILES_DIRS = [
    BASE_DIR / "staticfiles",  # extra shared folder for development
    BASE_DIR.parent / "templates" / "assets",  # serve assets at /static/
    BASE_DIR.parent / "templates" / "data",    # serve data JSONs at /static/
]
