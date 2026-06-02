import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, spotify_id, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        user = self.model(username=username, spotify_id=spotify_id, **extra_fields)
        user.set_unusable_password()  # login is always via Spotify, never password
        user.save(using=self._db)
        return user

    def create_superuser(self, username, spotify_id, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, spotify_id, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model. Identity comes from Spotify - no password login.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    spotify_id = models.CharField(max_length=100, unique=True)
    username = models.CharField(max_length=100, unique=True)
    avatar_url = models.URLField(blank=True, default="")

    # Spotify OAuth tokens - access_token expires in 1 hour, refresh_token is long-lived
    spotify_access_token = models.TextField(blank=True, default="")
    spotify_refresh_token = models.TextField(blank=True, default="")
    token_expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["spotify_id"]

    def __str__(self):
        return self.username
