"""
Spotify OAuth views + user profile endpoints.

OAuth flow:
  1. GET /api/v1/auth/spotify/          → redirect to Spotify
  2. GET /api/v1/auth/spotify/callback/ → exchange code, issue JWT, redirect frontend
"""
import secrets
import urllib.parse
from datetime import timedelta

import requests
from django.core.cache import cache
from django.conf import settings
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken

from apps.friendships.selectors import blocked_user_ids

from .models import User
from .serializers import UserProfileSerializer, UserSerializer

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_ME_URL = "https://api.spotify.com/v1/me"
SPOTIFY_SCOPES = "user-read-private user-read-email"


def _get_jwt_for_user(user):
    """Return (access_token, refresh_token) strings for a user."""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token), str(refresh)


class SpotifyAuthView(generics.GenericAPIView):
    """
    Redirects the browser to Spotify's authorization page.
    The `state` parameter prevents CSRF during the OAuth dance.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        state = secrets.token_urlsafe(16)
        cache.set(f"oauth_state:{state}", True, timeout=300)
        params = {
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "scope": SPOTIFY_SCOPES,
            "state": state,
        }
        url = f"{SPOTIFY_AUTH_URL}?{urllib.parse.urlencode(params)}"
        return redirect(url)


class SpotifyCallbackView(generics.GenericAPIView):
    """
    Spotify redirects here after the user authorizes.
    We exchange the code for tokens, fetch the Spotify profile,
    create or update the local User, then redirect the frontend
    with the JWT pair in the query string.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        code = request.GET.get("code")
        error = request.GET.get("error")
        state = request.GET.get("state")

        if error or not code:
            return redirect(f"{settings.FRONTEND_URL}/login?error=spotify_denied")

        # Validate state to prevent CSRF — must match a value we issued
        cache_key = f"oauth_state:{state}"
        if not state or not cache.get(cache_key):
            return redirect(f"{settings.FRONTEND_URL}/login?error=invalid_state")
        cache.delete(cache_key)

        # Exchange authorization code for Spotify tokens
        token_response = requests.post(
            SPOTIFY_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            auth=(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET),
            timeout=10,
        )
        if token_response.status_code != 200:
            return redirect(f"{settings.FRONTEND_URL}/login?error=token_exchange_failed")

        token_data = token_response.json()
        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        expires_in = token_data["expires_in"]  # seconds

        # Fetch Spotify user profile
        profile_response = requests.get(
            SPOTIFY_ME_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        if profile_response.status_code != 200:
            return redirect(f"{settings.FRONTEND_URL}/login?error=profile_fetch_failed")

        profile = profile_response.json()
        spotify_id = profile["id"]
        display_name = profile.get("display_name") or profile["id"]
        avatar_url = ""
        if profile.get("images"):
            avatar_url = profile["images"][0].get("url", "")

        # Sanitize username - Spotify display names can have spaces/special chars
        safe_username = display_name.replace(" ", "_")[:100]

        user, created = User.objects.get_or_create(
            spotify_id=spotify_id,
            defaults={"username": safe_username, "avatar_url": avatar_url},
        )
        if not created:
            # Update tokens and profile pic on every login
            user.avatar_url = avatar_url

        user.spotify_access_token = access_token
        user.spotify_refresh_token = refresh_token
        user.token_expires_at = timezone.now() + timedelta(seconds=expires_in)
        user.save()

        jwt_access, jwt_refresh = _get_jwt_for_user(user)

        # Send tokens to the frontend via query string; frontend removes them from URL immediately
        redirect_url = (
            f"{settings.FRONTEND_URL}/callback?token={jwt_access}&refresh={jwt_refresh}"
        )
        return redirect(redirect_url)


class MeView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        q = self.request.query_params.get("search", "").strip()
        if not q:
            return User.objects.none()
        return (
            User.objects.filter(username__icontains=q)
            .exclude(id=self.request.user.id)
            .exclude(id__in=blocked_user_ids(self.request.user))
        )


class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
