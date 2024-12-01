from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from Wrappedapp.models import SpotifyAccount, SpotifyWrapped
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

class ViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client = Client()
        # Create a SpotifyAccount linked to the user
        SpotifyAccount.objects.create(
            user=self.user,
            access_token="mock_access_token",
            refresh_token="mock_refresh_token",
            expires_at=timezone.now() + timedelta(hours=1)
        )

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    @patch('Wrappedapp.spotify_api_functions.get_artist_thank_you')
    @patch('Wrappedapp.spotify_api_functions.get_sound_town')
    @patch('Wrappedapp.spotify_api_functions.get_total_minutes_listened')
    @patch('Wrappedapp.spotify_api_functions.get_top_genres')
    @patch('Wrappedapp.spotify_api_functions.get_top_artists')
    @patch('Wrappedapp.spotify_api_functions.get_top_songs')
    @patch('Wrappedapp.spotify_api_functions.get_valid_spotify_token')
    def test_create_wrapped_view(
            self, mock_get_valid_spotify_token, mock_get_top_songs, mock_get_top_artists,
            mock_get_top_genres, mock_get_total_minutes_listened, mock_get_sound_town,
            mock_get_artist_thank_you
    ):
        self.client.login(username="testuser", password="password")

        # Mock Spotify data
        mock_get_valid_spotify_token.return_value = "mock_access_token"
        mock_get_top_songs.return_value = [
            {"name": "Mock Song", "artist": "Mock Artist", "duration_ms": 300000}
        ]
        mock_get_top_artists.return_value = [
            {"name": "Mock Artist", "genres": ["Pop", "Rock"]},
            {"name": "Another Artist", "genres": ["Jazz", "Blues"]}
        ]
        mock_get_top_genres.return_value = ["Pop", "Rock", "Jazz", "Blues"]
        mock_get_total_minutes_listened.return_value = 100
        mock_get_sound_town.return_value = "Mock Town"
        mock_get_artist_thank_you.return_value = {"Mock Artist": "Thank you!"}

        # Call the view
        response = self.client.post(reverse('create_wrapped'))

        # Assert redirect
        self.assertEqual(response.status_code, 302)

        # Assert SpotifyWrapped object creation
        self.assertEqual(SpotifyWrapped.objects.count(), 1)
        wrapped = SpotifyWrapped.objects.first()

        # Assert fields
        self.assertEqual(wrapped.user, self.user)

    def test_logout_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)
