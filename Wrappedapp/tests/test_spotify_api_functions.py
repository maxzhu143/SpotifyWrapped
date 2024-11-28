import unittest
from unittest.mock import patch, MagicMock
from Wrappedapp.spotify_api_functions import get_valid_spotify_token, get_top_songs


class SpotifyAPIFunctionsTestCase(unittest.TestCase):
    @patch('requests.post')
    def test_get_valid_spotify_token(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "new_access_token", "expires_in": 3600}
        token = get_valid_spotify_token(MagicMock())
        self.assertEqual(token, "new_access_token")

    @patch('requests.get')
    def test_get_top_songs(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"name": "Test Song"}]}
        songs = get_top_songs("mock_token")
        self.assertEqual(len(songs), 1)
        self.assertEqual(songs[0]['name'], "Test Song")
