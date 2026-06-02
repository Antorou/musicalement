from django.urls import path

from .views import SpotifyAuthView, SpotifyCallbackView

# Mounted at /api/v1/auth/
urlpatterns = [
    path("spotify/", SpotifyAuthView.as_view(), name="spotify_auth"),
    path("spotify/callback/", SpotifyCallbackView.as_view(), name="spotify_callback"),
]
