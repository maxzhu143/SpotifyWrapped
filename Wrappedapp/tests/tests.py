"""Tests for Wrappedapp."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User


class UserRegistrationTest(TestCase):
    """Test case for user registration."""
    def setUp(self):
        """Set up necessary variables for registration test."""
        self.register_url = reverse('register')

    def test_register_user(self):
        """Test successful user registration."""
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'pokPyw-xyxquf-gozdo0',
            'password2': 'pokPyw-xyxquf-gozdo0'
        }

        # Submit registration data via POST request to the registration view
        response = self.client.post(self.register_url, data)

        # Check that the response redirects, implying a successful registration
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

        # Verify that the user now exists in the database
        user_exists = User.objects.filter(username='testuser').exists()
        self.assertTrue(user_exists, "User registration failed; user not found in the database.")

        # Optional: Retrieve the user and check additional fields
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')



class UserLoginTest(TestCase):
    """Test case for user login functionality."""
    def setUp(self):
        """Create a test user."""
        self.user = User.objects.create_user(username='testuser', password='pokPyw-xyxquf-gozdo0')
        self.login_url = reverse('login')

    def test_user_login(self):
        """Test login with valid credentials."""
        # Login with the test user credentials
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'pokPyw-xyxquf-gozdo0'})

        # Check that the response redirects to the dashboard
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_failed(self):
        """Test login with invalid credentials."""
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'wrongpassword'})

        # Check that the login fails and user remains on the login page
        self.assertEqual(response.status_code, 200)


class UserLogoutTest(TestCase):
    """Test case for user logout functionality."""
    def setUp(self):
        """Log in a user for testing logout."""
        self.user = User.objects.create_user(username='testuser', password='pokPyw-xyxquf-gozdo0')
        self.client.login(username='testuser', password='pokPyw-xyxquf-gozdo0')
        self.logout_url = reverse('logout')

    def test_user_logout(self):
        """Test successful logout."""
        response = self.client.post(self.logout_url)

        # Check that the logout page renders successfully (status code 200)
        self.assertEqual(response.status_code, 302)


class SpotifyIntegrationTest(TestCase):
    def setUp(self):
        # Set up a user and log them into the Django app
        self.user = User.objects.create_user(username='terry5215', password='bagmyg-xutxo8-dyxgiF')
        self.client.login(username='terry5215', password='bagmyg-xutxo8-dyxgiF')
        self.spot_login_url = reverse('spot_login')
        self.callback_url = reverse('callback')
        self.top_songs_url = reverse('top_songs')
        self.unlink_url = reverse('unlink')
        self.dashboard_url = reverse('dashboard')

    @patch('requests.post')
    def test_user_can_link_account(self, mock_post):
        # Simulate the user clicking "Link Spotify Account" and getting redirected to Spotify's auth page
        response = self.client.get(self.spot_login_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("https://accounts.spotify.com/authorize", response.url)

        # Mock the Spotify token exchange in the callback
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'access_token': 'valid_access_token',
            'refresh_token': 'valid_refresh_token',
            'expires_in': 3600
        }

        # Simulate the callback with a code from Spotify
        response = self.client.get(self.callback_url, {'code': 'valid_code'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.top_songs_url)

        # Ensure access_token is in session
        self.assertIn('access_token', self.client.session)
        self.assertEqual(self.client.session['access_token'], 'valid_access_token')

    def test_user_can_see_top_tracks_after_linking(self):
        # Simulate the user already linked to Spotify with a valid access_token
        self.client.session['access_token'] = 'valid_access_token'
        self.client.session.save()

        # Access the top songs page
        response = self.client.get(self.top_songs_url)
        self.assertEqual(response.status_code, 302) # Replace with actual user_name if set in the template

    def test_user_can_unlink_account_without_logging_out(self):
        # Simulate a Spotify-linked session
        self.client.session['access_token'] = 'valid_access_token'
        self.client.session.save()

        # User clicks "Unlink" and is redirected to the dashboard
        response = self.client.post(self.unlink_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.dashboard_url)

        # Verify that Spotify access_token is cleared but user session remains
        self.assertNotIn('access_token', self.client.session)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)  # User remains logged in
        self.assertContains(response, 'Dashboard')  # Confirm dashboard access

    def test_user_logout_from_django_site(self):
        # Log out of Django and ensure user is redirected correctly
        self.client.login(username='testuser', password='pokPyw-xyxquf-gozdo0')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))  # Assuming home is the post-logout page
