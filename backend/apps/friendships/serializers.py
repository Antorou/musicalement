from rest_framework import serializers

from apps.users.serializers import UserSerializer

from .models import Friendship


class FriendshipSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)
    to_user_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Friendship
        fields = ["id", "from_user", "to_user", "to_user_id", "status", "created_at"]
        read_only_fields = ["id", "from_user", "to_user", "status", "created_at"]
