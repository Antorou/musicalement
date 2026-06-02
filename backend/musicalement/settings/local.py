"""
Local development settings. Reads values from .env via python-decouple.
"""
from decouple import config

from .base import *  # noqa: F401, F403

DEBUG = True

SECRET_KEY = config("SECRET_KEY", default="dev-secret-key-change-in-production")

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB", default="musicalement"),
        "USER": config("POSTGRES_USER", default="musicalement"),
        "PASSWORD": config("POSTGRES_PASSWORD", default="musicalement"),
        "HOST": config("POSTGRES_HOST", default="db"),
        "PORT": config("POSTGRES_PORT", default="5432"),
    }
}

REDIS_URL = config("REDIS_URL", default="redis://redis:6379/0")

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

CORS_ALLOWED_ORIGINS = [
    config("FRONTEND_URL", default="http://localhost:5173"),
]
CORS_ALLOW_CREDENTIALS = True

# Spotify OAuth
SPOTIFY_CLIENT_ID = config("SPOTIFY_CLIENT_ID", default="")
SPOTIFY_CLIENT_SECRET = config("SPOTIFY_CLIENT_SECRET", default="")
SPOTIFY_REDIRECT_URI = config(
    "SPOTIFY_REDIRECT_URI",
    default="http://localhost:8000/api/v1/auth/spotify/callback/",
)
FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:5173")
