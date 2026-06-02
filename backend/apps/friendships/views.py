from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.users.models import User

from .models import Friendship
from .serializers import FriendshipSerializer


class FriendshipListCreateView(generics.ListCreateAPIView):
    """
    GET  - list all friendships (accepted + pending) involving the current user
    POST - send a friend request: body = {"to_user_id": "<uuid>"}
    """
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Friendship.objects.filter(
            Q(from_user=user) | Q(to_user=user)
        ).select_related("from_user", "to_user")

    def perform_create(self, serializer):
        to_user_id = serializer.validated_data.pop("to_user_id")
        try:
            to_user = User.objects.get(pk=to_user_id)
        except User.DoesNotExist:
            raise ValidationError({"to_user_id": "User not found."})

        if to_user == self.request.user:
            raise ValidationError({"to_user_id": "Cannot send a friend request to yourself."})

        # Block if a friendship already exists in either direction
        exists = Friendship.objects.filter(
            Q(from_user=self.request.user, to_user=to_user) |
            Q(from_user=to_user, to_user=self.request.user)
        ).exists()
        if exists:
            raise ValidationError({"detail": "Friendship already exists."})

        serializer.save(from_user=self.request.user, to_user=to_user)


class FriendshipDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    PATCH  - accept or reject a request: body = {"status": "accepted"} or {"status": "rejected"}
    DELETE - remove a friend or cancel a pending request
    """
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Friendship.objects.filter(Q(from_user=user) | Q(to_user=user))

    def partial_update(self, request, *args, **kwargs):
        friendship = self.get_object()
        new_status = request.data.get("status")

        # Only the recipient can accept/reject
        if friendship.to_user != request.user:
            return Response(
                {"detail": "Only the recipient can accept or reject a request."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if new_status == "accepted":
            friendship.status = Friendship.STATUS_ACCEPTED
            friendship.save()
            return Response(FriendshipSerializer(friendship).data)

        # Any other value (e.g. "rejected") = delete the request
        friendship.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
