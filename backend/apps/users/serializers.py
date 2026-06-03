from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "avatar_url", "created_at"]
        read_only_fields = fields


class UserProfileSerializer(serializers.ModelSerializer):
    """Richer view for profile pages: streak, post count, block state."""
    current_streak = serializers.IntegerField(read_only=True)
    post_count = serializers.IntegerField(source="posts.count", read_only=True)
    is_blocked = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "avatar_url", "created_at", "current_streak", "post_count", "is_blocked"]
        read_only_fields = fields

    def get_is_blocked(self, obj):
        """True if the requesting user has blocked this profile's user."""
        request = self.context.get("request")
        if request and request.user.is_authenticated and request.user != obj:
            return obj.blocks_received.filter(blocker=request.user).exists()
        return False
