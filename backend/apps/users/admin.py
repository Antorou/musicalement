from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "spotify_id", "created_at", "is_staff")
    search_fields = ("username", "spotify_id")
    ordering = ("-created_at",)
    fieldsets = (
        (None, {"fields": ("username", "spotify_id", "avatar_url")}),
        ("Spotify tokens", {"fields": ("spotify_access_token", "spotify_refresh_token", "token_expires_at"), "classes": ("collapse",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {"fields": ("username", "spotify_id")}),
    )
