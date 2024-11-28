import unittest
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from Wrappedapp.models import SpotifyAccount, SpotifyWrapped
from django.contrib.auth.models import User

class ViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client = Client()

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    @patch('Wrappedapp.spotify_api_functions.get_valid_spotify_token')
    def test_create_wrapped_view(self, mock_get_valid_spotify_token):
        self.client.login(username="testuser", password="password")
        mock_get_valid_spotify_token.return_value = "mock_token"
        response = self.client.post(reverse('create_wrapped'))
        self.assertEqual(response.status_code, 302)

    def test_logout_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)
