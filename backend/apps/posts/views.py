"""
Post views:
- CreatePostView: fetches current/recent Spotify track, creates Post
- FeedView: friends' posts today (gated: you must have posted today)
- MyPostsView: own full post history
- LikeToggleView: like or unlike a post
- CommentListCreateView / CommentDestroyView: comments on a post
"""
import requests
from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.friendships.models import Friendship

from .models import Comment, Like, Post
from .serializers import CommentSerializer, PostSerializer

SPOTIFY_CURRENTLY_PLAYING = "https://api.spotify.com/v1/me/player/currently-playing"
SPOTIFY_RECENTLY_PLAYED = "https://api.spotify.com/v1/me/player/recently-played?limit=1"


def _fetch_track_from_spotify(user):
    """
    Returns a dict with track info, or None if Spotify fails.
    Tries currently-playing first, falls back to recently-played.
    """
    headers = {"Authorization": f"Bearer {user.spotify_access_token}"}

    # Try currently playing
    resp = requests.get(SPOTIFY_CURRENTLY_PLAYING, headers=headers, timeout=5)
    if resp.status_code == 200 and resp.json().get("item"):
        item = resp.json()["item"]
        return _extract_track(item)

    # Fallback: most recently played
    resp = requests.get(SPOTIFY_RECENTLY_PLAYED, headers=headers, timeout=5)
    if resp.status_code == 200:
        items = resp.json().get("items", [])
        if items:
            return _extract_track(items[0]["track"])

    return None


def _extract_track(item):
    return {
        "spotify_track_id": item["id"],
        "track_title": item["name"],
        "artist_name": ", ".join(a["name"] for a in item["artists"]),
        "album_name": item["album"]["name"],
        "album_cover_url": item["album"]["images"][0]["url"] if item["album"]["images"] else "",
        "preview_url": item.get("preview_url") or "",
    }


def _get_friend_ids(user):
    """Returns a set of user IDs that are confirmed friends with the given user."""
    friendships = Friendship.objects.filter(
        status="accepted"
    ).filter(
        models.Q(from_user=user) | models.Q(to_user=user)
    )
    ids = set()
    for f in friendships:
        ids.add(f.from_user_id if f.to_user_id == user.id else f.to_user_id)
    return ids


# Import Q here after the function that uses it
from django.db import models as django_models  # noqa: E402


def _get_friend_ids_v2(user):
    """Returns a set of user IDs that are confirmed friends with the given user."""
    friendships = Friendship.objects.filter(
        status="accepted"
    ).filter(
        django_models.Q(from_user=user) | django_models.Q(to_user=user)
    )
    ids = set()
    for f in friendships:
        ids.add(f.from_user_id if f.to_user_id == user.id else f.to_user_id)
    return ids


class CreatePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        track = _fetch_track_from_spotify(request.user)
        if not track:
            return Response(
                {"detail": "Could not fetch track from Spotify. Make sure something is playing."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        post = Post.objects.create(user=request.user, **track)
        return Response(PostSerializer(post, context={"request": request}).data, status=status.HTTP_201_CREATED)


class FeedView(generics.ListAPIView):
    """
    Returns friends' posts from today.
    Returns 403 with {"detail": "post_required"} if the user hasn't posted today.
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.none()  # overridden in list()

    def list(self, request, *args, **kwargs):
        today = timezone.now().date()
        has_posted_today = Post.objects.filter(
            user=request.user, created_at__date=today
        ).exists()

        if not has_posted_today:
            return Response(
                {"detail": "post_required"},
                status=status.HTTP_403_FORBIDDEN,
            )

        friend_ids = _get_friend_ids_v2(request.user)
        now = timezone.now()
        queryset = Post.objects.filter(
            user_id__in=friend_ids,
            expires_at__gt=now,
        ).select_related("user").prefetch_related("likes", "comments")

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MyPostsView(generics.ListAPIView):
    """Own full post history - no expiry filter."""
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user).select_related("user")


class PostDestroyView(generics.DestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)


class LikeToggleView(APIView):
    """POST to like, POST again to unlike (toggle)."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        like, created = Like.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
            return Response({"liked": False, "likes_count": post.likes.count()})
        return Response({"liked": True, "likes_count": post.likes.count()})


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs["pk"]).select_related("user")

    def perform_create(self, serializer):
        post = Post.objects.get(pk=self.kwargs["pk"])
        serializer.save(user=self.request.user, post=post)


class CommentDestroyView(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user, post_id=self.kwargs["pk"])
