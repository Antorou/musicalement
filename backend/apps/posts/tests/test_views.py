from datetime import timedelta
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.friendships.models import Block, Friendship
from apps.posts.models import Comment, Post
from apps.users.models import User


def make_client(user):
    client = APIClient()
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
    return client


def make_user(username, spotify_id):
    return User.objects.create_user(username=username, spotify_id=spotify_id)


def make_post(user, **kwargs):
    defaults = {
        "spotify_track_id": "track_abc",
        "track_title": "Blinding Lights",
        "artist_name": "The Weeknd",
        "album_name": "After Hours",
        "album_cover_url": "https://example.com/cover.jpg",
    }
    defaults.update(kwargs)
    return Post.objects.create(user=user, **defaults)


FAKE_TRACK = {
    "spotify_track_id": "track_123",
    "track_title": "Starboy",
    "artist_name": "The Weeknd",
    "album_name": "Starboy",
    "album_cover_url": "https://example.com/starboy.jpg",
    "preview_url": "",
}


@pytest.mark.django_db
class TestFeedView:
    def test_user_without_post_today_gets_403(self):
        alice = make_user("alice", "s_alice")
        client = make_client(alice)
        response = client.get(reverse("post_feed"))
        assert response.status_code == 403
        assert response.data["detail"] == "post_required"

    def test_user_with_post_today_sees_friends_posts(self):
        alice = make_user("alice", "s_alice")
        bob = make_user("bob", "s_bob")
        Friendship.objects.create(from_user=alice, to_user=bob, status="accepted")

        make_post(alice)  # alice posts today, unlocking the feed
        bob_post = make_post(bob)

        client = make_client(alice)
        response = client.get(reverse("post_feed"))
        assert response.status_code == 200
        ids = [p["id"] for p in response.data]
        assert str(bob_post.id) in ids

    def test_expired_posts_not_in_feed(self):
        alice = make_user("alice", "s_alice")
        bob = make_user("bob", "s_bob")
        Friendship.objects.create(from_user=alice, to_user=bob, status="accepted")

        make_post(alice)
        expired = make_post(bob, expires_at=timezone.now() - timedelta(hours=1))

        client = make_client(alice)
        response = client.get(reverse("post_feed"))
        assert response.status_code == 200
        ids = [p["id"] for p in response.data]
        assert str(expired.id) not in ids

    def test_non_friend_posts_not_in_feed(self):
        alice = make_user("alice", "s_alice")
        stranger = make_user("stranger", "s_stranger")

        make_post(alice)
        stranger_post = make_post(stranger)

        client = make_client(alice)
        response = client.get(reverse("post_feed"))
        assert response.status_code == 200
        ids = [p["id"] for p in response.data]
        assert str(stranger_post.id) not in ids


@pytest.mark.django_db
class TestLikeToggleView:
    def test_like_post(self):
        alice = make_user("alice", "s_alice")
        bob = make_user("bob", "s_bob")
        post = make_post(bob)

        client = make_client(alice)
        response = client.post(reverse("post_like", kwargs={"pk": post.id}))
        assert response.status_code == 200
        assert response.data["liked"] is True
        assert response.data["likes_count"] == 1

    def test_unlike_post(self):
        alice = make_user("alice", "s_alice")
        bob = make_user("bob", "s_bob")
        post = make_post(bob)

        client = make_client(alice)
        client.post(reverse("post_like", kwargs={"pk": post.id}))  # like
        response = client.post(reverse("post_like", kwargs={"pk": post.id}))  # unlike
        assert response.data["liked"] is False
        assert response.data["likes_count"] == 0


@pytest.mark.django_db
class TestCommentDestroyView:
    def test_non_author_cannot_delete_comment(self):
        alice = make_user("alice", "s_alice")
        bob = make_user("bob", "s_bob")
        post = make_post(alice)

        comment = Comment.objects.create(post=post, user=alice, body="alice's comment")

        client = make_client(bob)
        response = client.delete(
            reverse("comment_destroy", kwargs={"pk": post.id, "comment_pk": comment.id})
        )
        assert response.status_code == 404
        assert Comment.objects.filter(id=comment.id).exists()


@pytest.mark.django_db
class TestCommentLikeToggleView:
    def test_like_and_unlike_comment(self):
        alice = make_user("alice", "s_alice")
        bob = make_user("bob", "s_bob")
        post = make_post(bob)
        comment = Comment.objects.create(post=post, user=bob, body="nice track")

        client = make_client(alice)
        url = reverse("comment_like", kwargs={"pk": post.id, "comment_pk": comment.id})

        liked = client.post(url)
        assert liked.status_code == 200
        assert liked.data == {"liked": True, "likes_count": 1}

        unliked = client.post(url)
        assert unliked.data == {"liked": False, "likes_count": 0}

    def test_like_unknown_comment_404(self):
        alice = make_user("alice", "s_alice")
        post = make_post(alice)
        client = make_client(alice)
        import uuid
        url = reverse("comment_like", kwargs={"pk": post.id, "comment_pk": uuid.uuid4()})
        assert client.post(url).status_code == 404


@pytest.mark.django_db
class TestBlockInFeed:
    def test_blocked_friend_posts_hidden_from_feed(self):
        alice = make_user("alice", "s_alice")
        bob = make_user("bob", "s_bob")
        Friendship.objects.create(from_user=alice, to_user=bob, status="accepted")
        Block.objects.create(blocker=alice, blocked=bob)

        make_post(alice)  # unlock the feed
        bob_post = make_post(bob)

        client = make_client(alice)
        response = client.get(reverse("post_feed"))
        assert response.status_code == 200
        ids = [p["id"] for p in response.data]
        assert str(bob_post.id) not in ids

    def test_blocker_also_hidden_from_blocked_user_feed(self):
        """Blocking is symmetric: the blocked user also stops seeing the blocker."""
        alice = make_user("alice", "s_alice")
        bob = make_user("bob", "s_bob")
        Friendship.objects.create(from_user=alice, to_user=bob, status="accepted")
        Block.objects.create(blocker=alice, blocked=bob)

        alice_post = make_post(alice)
        make_post(bob)  # unlock bob's feed

        client = make_client(bob)
        response = client.get(reverse("post_feed"))
        ids = [p["id"] for p in response.data]
        assert str(alice_post.id) not in ids
