from unittest.mock import patch
from django.test import TestCase
from Wrappedapp.models import SpotifyAccount
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from Wrappedapp.spotify_api_functions import get_valid_spotify_token, get_top_songs


class SpotifyAPIFunctionsTestCase(TestCase):

    @patch('requests.post')
    def test_get_valid_spotify_token(self, mock_post):
        # Mock the response from Spotify's token refresh endpoint
        mock_response = mock_post.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "expires_in": 3600
        }

        # Create a mock user and corresponding SpotifyAccount object
        user = User.objects.create(username="testuser")
        spotify_account = SpotifyAccount.objects.create(
            user=user,
            access_token="old_access_token",
            refresh_token="mock_refresh_token",
            expires_at=timezone.now() - timedelta(seconds=1)  # Token expired
        )

        # Call the function and assert the result
        token = get_valid_spotify_token(user)
        self.assertEqual(token, "new_access_token")  # Validate new token
        spotify_account.refresh_from_db()  # Refresh object from the database
        self.assertEqual(spotify_account.access_token, "new_access_token")  # Validate DB update

    @patch('requests.get')
    def test_get_top_songs(self, mock_get):
        # Mock the Spotify API response
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"name": "Test Song", "artists": [{"name": "Test Artist"}], "album": {"name": "Test Album", "images": [{"url": "test_url"}]}, "duration_ms": 300000, "external_urls": {"spotify": "test_url"}}]
        }

        # Call the function and assert the result
        songs = get_top_songs("mock_token")
        self.assertEqual(len(songs), 1)
        self.assertEqual(songs[0]['name'], "Test Song")
        self.assertEqual(songs[0]['artist'], "Test Artist")
        self.assertEqual(songs[0]['album'], "Test Album")
        self.assertEqual(songs[0]['cover'], "test_url")
        self.assertEqual(songs[0]['spotify_url'], "test_url")
