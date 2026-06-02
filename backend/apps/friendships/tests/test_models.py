import pytest

from apps.friendships.models import Friendship
from apps.users.models import User


@pytest.mark.django_db
class TestFriendshipModel:
    def test_create_pending_friendship(self):
        alice = User.objects.create_user(username="alice", spotify_id="s_alice")
        bob = User.objects.create_user(username="bob", spotify_id="s_bob")
        f = Friendship.objects.create(from_user=alice, to_user=bob)
        assert f.status == Friendship.STATUS_PENDING

    def test_unique_constraint(self):
        alice = User.objects.create_user(username="alice", spotify_id="s_alice")
        bob = User.objects.create_user(username="bob", spotify_id="s_bob")
        Friendship.objects.create(from_user=alice, to_user=bob)
        with pytest.raises(Exception):
            Friendship.objects.create(from_user=alice, to_user=bob)

    def test_accept_friendship(self):
        alice = User.objects.create_user(username="alice", spotify_id="s_alice")
        bob = User.objects.create_user(username="bob", spotify_id="s_bob")
        f = Friendship.objects.create(from_user=alice, to_user=bob)
        f.status = Friendship.STATUS_ACCEPTED
        f.save()
        assert Friendship.objects.get(pk=f.pk).status == Friendship.STATUS_ACCEPTED
