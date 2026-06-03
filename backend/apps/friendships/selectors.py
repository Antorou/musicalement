from django.db.models import Q

from .models import Block, Friendship


def blocked_user_ids(user):
    """
    IDs of users the given user has blocked OR who have blocked the given user.
    These users are hidden from each other across the app (feed, search, comments).
    """
    blocks = Block.objects.filter(Q(blocker=user) | Q(blocked=user))
    ids = set()
    for b in blocks:
        ids.add(b.blocked_id if b.blocker_id == user.id else b.blocker_id)
    return ids


def friend_ids(user):
    """IDs of users with an accepted friendship with the given user."""
    friendships = Friendship.objects.filter(status="accepted").filter(
        Q(from_user=user) | Q(to_user=user)
    )
    ids = set()
    for f in friendships:
        ids.add(f.from_user_id if f.to_user_id == user.id else f.to_user_id)
    return ids
