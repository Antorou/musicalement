from datetime import timedelta

import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone


@shared_task
def refresh_spotify_tokens():
    """
    Proactively refresh Spotify access tokens that expire within 10 minutes.
    Runs every 45 minutes via Celery Beat.
    """
    from .models import User

    threshold = timezone.now() + timedelta(minutes=10)
    expiring_users = User.objects.filter(
        token_expires_at__lt=threshold,
        spotify_refresh_token__gt="",
    )

    for user in expiring_users:
        try:
            resp = requests.post(
                "https://accounts.spotify.com/api/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": user.spotify_refresh_token,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                auth=(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET),
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                user.spotify_access_token = data["access_token"]
                user.token_expires_at = timezone.now() + timedelta(seconds=data["expires_in"])
                if "refresh_token" in data:
                    user.spotify_refresh_token = data["refresh_token"]
                user.save(update_fields=["spotify_access_token", "spotify_refresh_token", "token_expires_at"])
        except Exception:
            pass  # individual failures should not crash the task
