import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "musicalement.settings.local")

app = Celery("musicalement")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Runs every minute - hook for future notifications on post expiry
    "expire-posts-every-minute": {
        "task": "apps.posts.tasks.expire_posts",
        "schedule": crontab(minute="*"),
    },
    # Proactively refresh Spotify tokens before they expire
    "refresh-spotify-tokens-every-45-minutes": {
        "task": "apps.users.tasks.refresh_spotify_tokens",
        "schedule": crontab(minute="*/45"),
    },
}
