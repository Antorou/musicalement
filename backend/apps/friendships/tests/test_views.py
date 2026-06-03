import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.friendships.models import Block, Friendship
from apps.users.models import User


def make_client(user):
    client = APIClient()
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
    return client


@pytest.mark.django_db
class TestBlockView:
    def test_block_user_drops_friendship(self):
        alice = User.objects.create_user(username="alice", spotify_id="s_alice")
        bob = User.objects.create_user(username="bob", spotify_id="s_bob")
        Friendship.objects.create(from_user=alice, to_user=bob, status="accepted")

        client = make_client(alice)
        response = client.post(reverse("block_list_create"), {"blocked_id": str(bob.id)})
        assert response.status_code == 201
        assert Block.objects.filter(blocker=alice, blocked=bob).exists()
        assert not Friendship.objects.filter(from_user=alice, to_user=bob).exists()

    def test_cannot_block_self(self):
        alice = User.objects.create_user(username="alice", spotify_id="s_alice")
        client = make_client(alice)
        response = client.post(reverse("block_list_create"), {"blocked_id": str(alice.id)})
        assert response.status_code == 400

    def test_cannot_friend_blocked_user(self):
        alice = User.objects.create_user(username="alice", spotify_id="s_alice")
        bob = User.objects.create_user(username="bob", spotify_id="s_bob")
        Block.objects.create(blocker=alice, blocked=bob)

        client = make_client(alice)
        response = client.post(reverse("friendship_list_create"), {"to_user_id": str(bob.id)})
        assert response.status_code == 400

    def test_unblock(self):
        alice = User.objects.create_user(username="alice", spotify_id="s_alice")
        bob = User.objects.create_user(username="bob", spotify_id="s_bob")
        block = Block.objects.create(blocker=alice, blocked=bob)

        client = make_client(alice)
        response = client.delete(reverse("block_destroy", kwargs={"pk": block.id}))
        assert response.status_code == 204
        assert not Block.objects.filter(id=block.id).exists()

    def test_blocked_user_hidden_from_search(self):
        alice = User.objects.create_user(username="alice", spotify_id="s_alice")
        bob = User.objects.create_user(username="bob", spotify_id="s_bob")
        Block.objects.create(blocker=alice, blocked=bob)

        client = make_client(alice)
        response = client.get(reverse("user_search"), {"search": "bob"})
        assert response.status_code == 200
        usernames = [u["username"] for u in response.data]
        assert "bob" not in usernames
