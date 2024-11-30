import unittest
from django.test import TestCase
from Wrappedapp.models import SpotifyAccount, SpotifyWrapped
from django.contrib.auth.models import User

class ModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")

    def test_spotify_account_creation(self):
        spotify_account = SpotifyAccount.objects.create(
            user=self.user,
            access_token="access_token",
            refresh_token="refresh_token"
        )
        self.assertEqual(spotify_account.user.username, "testuser")
        self.assertEqual(spotify_account.access_token, "access_token")

    def test_spotify_wrapped_creation(self):
        wrapped = SpotifyWrapped.objects.create(
            user=self.user,
            title="My Spotify Wrapped",
            personality="Test Personality"
        )
        self.assertEqual(wrapped.user.username, "testuser")
        self.assertEqual(wrapped.title, "My Spotify Wrapped")
