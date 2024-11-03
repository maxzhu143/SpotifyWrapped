"""Model definitions for Wrappedapp."""

from django.db import models
from django.contrib.auth.models import User

# Define your models here if any exist
# Example:
# class YourModel(models.Model):
#     """A description of what YourModel represents."""
#     field_name = models.CharField(max_length=100)
class SpotifyToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    spotify_user_id = models.CharField(max_length=255)
    spotify_display_name = models.CharField(max_length=255, null=True, blank=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        from django.utils import timezone
        return self.expires_at <= timezone.now()