from datetime import timedelta

import pytest
from django.utils import timezone

from apps.posts.models import Post
from apps.users.models import User


def make_post_on(user, days_ago):
    """Create a post whose created_at is `days_ago` days in the past."""
    when = timezone.now() - timedelta(days=days_ago)
    post = Post.objects.create(
        user=user,
        spotify_track_id="t",
        track_title="t",
        artist_name="a",
        album_name="al",
        album_cover_url="https://example.com/c.jpg",
        expires_at=when + timedelta(hours=24),
    )
    # created_at is auto_now_add, so override it explicitly
    Post.objects.filter(pk=post.pk).update(created_at=when)
    return post


@pytest.mark.django_db
class TestCurrentStreak:
    def test_no_posts_is_zero(self):
        user = User.objects.create_user(username="alice", spotify_id="s_alice")
        assert user.current_streak == 0

    def test_three_consecutive_days(self):
        user = User.objects.create_user(username="alice", spotify_id="s_alice")
        make_post_on(user, 0)
        make_post_on(user, 1)
        make_post_on(user, 2)
        assert user.current_streak == 3

    def test_gap_resets_streak(self):
        user = User.objects.create_user(username="alice", spotify_id="s_alice")
        make_post_on(user, 0)
        make_post_on(user, 1)
        make_post_on(user, 5)  # gap breaks the run
        assert user.current_streak == 2

    def test_stale_streak_is_zero(self):
        """A run that ended more than a day ago is no longer live."""
        user = User.objects.create_user(username="alice", spotify_id="s_alice")
        make_post_on(user, 3)
        make_post_on(user, 4)
        assert user.current_streak == 0


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(username="alice", spotify_id="spotify_alice")
        assert user.username == "alice"
        assert user.spotify_id == "spotify_alice"
        assert user.is_active is True
        assert user.is_staff is False

    def test_password_is_unusable(self):
        """Users authenticate via Spotify, never via password."""
        user = User.objects.create_user(username="alice", spotify_id="spotify_alice")
        assert not user.has_usable_password()

    def test_unique_spotify_id(self):
        User.objects.create_user(username="alice", spotify_id="spotify_alice")
        with pytest.raises(Exception):
            User.objects.create_user(username="alice2", spotify_id="spotify_alice")

    def test_unique_username(self):
        User.objects.create_user(username="alice", spotify_id="spotify_alice")
        with pytest.raises(Exception):
            User.objects.create_user(username="alice", spotify_id="spotify_other")

    def test_str(self):
        user = User.objects.create_user(username="alice", spotify_id="spotify_alice")
        assert str(user) == "alice"
