import pytest

from apps.users.models import User


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
