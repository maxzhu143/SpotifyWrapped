from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


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


class ListeningHistory(models.Model):
    """
    Represents a user's listening history retrieved from Spotify.
    """
    spotify_account = models.ForeignKey(
        SpotifyAccount,
        on_delete=models.CASCADE,
        related_name="listening_history"
    )
    track_name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    album_name = models.CharField(max_length=255, null=True, blank=True)
    played_at = models.DateTimeField()
    duration_ms = models.IntegerField(
        help_text="Duration of the track in milliseconds."
    )

    def __str__(self):
        return f"{self.track_name} by {self.artist_name}"


class WrappedSummary(models.Model):
    """
    Represents a user's Spotify Wrapped summary for the year.
    """
    spotify_account = models.ForeignKey(
        SpotifyAccount,
        on_delete=models.CASCADE,
        related_name="wrapped_summaries"
    )
    year = models.IntegerField(help_text="The year this summary covers.")
    top_tracks = models.JSONField(
        help_text="JSON representation of the user's top tracks."
    )
    top_artists = models.JSONField(
        help_text="JSON representation of the user's top artists."
    )
    top_genres = models.JSONField(
        help_text="JSON representation of the user's top genres."
    )
    listening_minutes = models.IntegerField(
        help_text="Total minutes listened during the year."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.spotify_account.user.username}'s Wrapped {self.year}"

from django.db import models
from django.conf import settings

class SpotifyWrapped(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wrapped_objects")
    title = models.CharField(max_length=255, default="My Spotify Wrapped")  # Optional title
    top_songs = models.JSONField(default=dict)  # Example: List of songs
    top_artists = models.JSONField(default=dict)  # Example: List of artists
    top_genres = models.JSONField(default=dict)  # Example: List of genres
    personality = models.CharField(max_length=255, null=True, blank=True)  # Optional string field
    total_minutes_listened = models.IntegerField(default=0)  # Example: Total listening time
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wrapped {self.title} for {self.user.username}"
