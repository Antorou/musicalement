import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


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

    @property
    def current_streak(self):
        """
        Number of consecutive days (ending today or yesterday) the user has posted.
        Posting once a day is the app's core loop, so the streak is the count of
        unbroken days up to the most recent post. A gap of more than one day resets it.
        """
        dates = (
            self.posts.values_list("created_at", flat=True)
            .order_by("-created_at")
        )
        # Collapse to a sorted set of distinct local dates, most recent first
        days = sorted({timezone.localtime(dt).date() for dt in dates}, reverse=True)
        if not days:
            return 0

        today = timezone.localdate()
        # The streak is only "live" if the latest post is today or yesterday
        if (today - days[0]).days > 1:
            return 0

        streak = 1
        for prev, nxt in zip(days, days[1:]):
            if (prev - nxt).days == 1:
                streak += 1
            else:
                break
        return streak
