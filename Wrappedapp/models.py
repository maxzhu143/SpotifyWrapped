"""Model definitions for Wrappedapp."""


# Define your models here if any exist
# Example:
# class YourModel(models.Model):
#     """A description of what YourModel represents."""
#     field_name = models.CharField(max_length=100)
from django.db import models
from django.contrib.auth.models import User

class SpotifyAccount(models.Model) :
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField (max_length=255)
    refresh_token = models.CharField (max_length=255)
    expires_at = models.DateTimeField ()
    def __str__(self):
        # Return a string representation, which can be the user's username
        return self.user.username