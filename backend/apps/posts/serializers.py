from rest_framework import serializers

from apps.users.serializers import UserSerializer

from .models import Comment, Post


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    liked_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "user", "body", "created_at", "likes_count", "liked_by_me"]
        read_only_fields = ["id", "user", "created_at", "likes_count", "liked_by_me"]

    def get_liked_by_me(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    comments_count = serializers.IntegerField(source="comments.count", read_only=True)
    liked_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id", "user",
            "spotify_track_id", "track_title", "artist_name",
            "album_name", "album_cover_url", "preview_url",
            "note", "expires_at", "created_at",
            "likes_count", "comments_count", "liked_by_me",
        ]
        read_only_fields = fields

    def get_liked_by_me(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
