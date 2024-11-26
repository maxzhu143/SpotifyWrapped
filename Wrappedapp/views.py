from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.db import models
from django.conf import settings


class SpotifyAccount(models.Model):
    """
    Represents a user's linked Spotify account, storing authentication tokens
    and related metadata.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="spotify_account"
    )
    access_token = models.CharField(
        max_length=255,
        help_text="The access token for Spotify API requests."
    )
    refresh_token = models.CharField(
        max_length=255,
        help_text="The refresh token for renewing the access token."
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    display_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Spotify display name of the linked account."
    )
    spotify_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The unique Spotify ID for the account."
    )
    profile_url = models.URLField(
        null=True,
        blank=True,
        help_text="URL to the user's Spotify profile."
    )
    profile_image = models.URLField(
        null=True,
        blank=True,
        help_text="URL to the user's Spotify profile image."
    )

    def is_token_expired(self):
        """Checks if the current access token has expired."""
        return datetime.now() >= self.expires_at

    def __str__(self):
        return f"{self.user.username}'s Spotify Account"



class SpotifyWrapped(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wrapped_objects")
    title = models.CharField(max_length=255, default="My Spotify Wrapped")  # Optional title
    top_songs = models.JSONField(default=dict)  # Example: List of songs
    top_artists = models.JSONField(default=dict)  # Example: List of artists
    top_genres = models.JSONField(default=dict)  # Example: List of genres  # Optional string field
    total_minutes_listened = models.IntegerField(default=0)  # Example: Total listening time
    sound_town = models.CharField(max_length=255, null=True, blank=True)
    artist_thank_you = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    top_podcasts = models.JSONField(default=dict)
    personality = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Wrapped {self.title} for {self.user.username}"