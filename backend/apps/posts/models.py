import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")

    # Data fetched from Spotify at post creation time - stored so we don't need Spotify to render the feed
    spotify_track_id = models.CharField(max_length=50)
    track_title = models.CharField(max_length=200)
    artist_name = models.CharField(max_length=200)
    album_name = models.CharField(max_length=200)
    album_cover_url = models.URLField()
    preview_url = models.URLField(blank=True, default="")  # 30-second audio clip

    note = models.CharField(max_length=140, blank=True, default="")
    expires_at = models.DateTimeField()  # = created_at + 24h
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.user.username} - {self.track_title}"


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")  # one like per user per post

    def __str__(self):
        return f"{self.user.username} likes {self.post}"


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    body = models.CharField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.username} on {self.post}: {self.body[:40]}"


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comment_likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("comment", "user")  # one like per user per comment

    def __str__(self):
        return f"{self.user.username} likes comment {self.comment_id}"
