from datetime import timedelta

import pytest
from django.utils import timezone

from apps.posts.models import Comment, Like, Post
from apps.users.models import User


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


@pytest.mark.django_db
class TestPostModel:
    def test_expires_at_set_automatically(self):
        user = make_user("alice", "s_alice")
        post = make_post(user)
        assert post.expires_at is not None
        # Should be approximately 24 hours from now
        delta = post.expires_at - post.created_at
        assert abs(delta.total_seconds() - 86400) < 5

    def test_is_expired_false_for_new_post(self):
        user = make_user("alice", "s_alice")
        post = make_post(user)
        assert post.is_expired is False

    def test_is_expired_true_for_old_post(self):
        user = make_user("alice", "s_alice")
        post = make_post(user)
        post.expires_at = timezone.now() - timedelta(hours=1)
        post.save()
        assert post.is_expired is True

    def test_like_unique_constraint(self):
        user = make_user("alice", "s_alice")
        post = make_post(user)
        Like.objects.create(post=post, user=user)
        with pytest.raises(Exception):
            Like.objects.create(post=post, user=user)

    def test_comment_ordering(self):
        user = make_user("alice", "s_alice")
        post = make_post(user)
        c1 = Comment.objects.create(post=post, user=user, body="first")
        c2 = Comment.objects.create(post=post, user=user, body="second")
        comments = list(post.comments.all())
        assert comments[0] == c1
        assert comments[1] == c2
