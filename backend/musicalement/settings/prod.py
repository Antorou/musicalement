from decouple import config

from .base import *  # noqa: F401, F403

DEBUG = False

# Fail loudly if SECRET_KEY is not set — no fallback in production
SECRET_KEY = config("SECRET_KEY")

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=lambda v: [h.strip() for h in v.split(",")])

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": config("POSTGRES_HOST"),
        "PORT": config("POSTGRES_PORT", default="5432"),
        "CONN_MAX_AGE": 60,
    }
}

REDIS_URL = config("REDIS_URL")

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

CORS_ALLOWED_ORIGINS = config(
    "FRONTEND_URL", cast=lambda v: [h.strip() for h in v.split(",")]
)
CORS_ALLOW_CREDENTIALS = True

SPOTIFY_CLIENT_ID = config("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = config("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = config("SPOTIFY_REDIRECT_URI")
FRONTEND_URL = config("FRONTEND_URL")

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
