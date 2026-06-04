import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User


def make_client(user):
    """Return an authenticated APIClient for the given user."""
    client = APIClient()
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
    return client


@pytest.fixture
def user(db):
    return User.objects.create_user(username="alice", spotify_id="spotify_alice")


@pytest.mark.django_db
class TestMeView:
    def test_returns_current_user(self, user):
        client = make_client(user)
        response = client.get(reverse("user_me"))
        assert response.status_code == 200
        assert response.data["username"] == "alice"

    def test_unauthenticated_is_rejected(self):
        client = APIClient()
        response = client.get(reverse("user_me"))
        assert response.status_code == 401


@pytest.mark.django_db
class TestUserSearchView:
    def test_search_finds_user(self, user, db):
        User.objects.create_user(username="bob", spotify_id="spotify_bob")
        client = make_client(user)
        response = client.get(reverse("user_search") + "?search=bob")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["username"] == "bob"

    def test_search_excludes_self(self, user):
        client = make_client(user)
        response = client.get(reverse("user_search") + "?search=alice")
        assert response.status_code == 200
        assert len(response.data) == 0

    def test_empty_query_returns_nothing(self, user):
        client = make_client(user)
        response = client.get(reverse("user_search"))
        assert response.status_code == 200
        assert len(response.data) == 0
