from django.contrib import admin

from .models import Comment, CommentLike, Like, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("user", "track_title", "artist_name", "created_at", "expires_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "track_title", "artist_name")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "body", "created_at")


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ("user", "comment", "created_at")
