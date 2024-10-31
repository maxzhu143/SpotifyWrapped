"""Tests for Wrappedapp."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


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
        self.assertContains(response, "Please enter a correct username and password. Note that both fields may be case-sensitive.")


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
        self.assertEqual(response.status_code, 200)

        # Verify that the response contains expected content
        self.assertContains(response, "You have been logged out.")  # Adjust based on actual content
        self.assertContains(response, "Go back to the home page")  # Check for the 'home' link/button


class NavbarDisplayTest(TestCase):
    def setUp(self):
        # Set up URLs and user for testing
        self.user = User.objects.create_user(username='testuser', password='pokPyw-xyxquf-gozdo0')
        self.home_url = reverse('home')

    def test_navbar_for_authenticated_user(self):
        # Log in the user
        self.client.login(username='testuser', password='pokPyw-xyxquf-gozdo0')

        # Get response and check navbar elements
        response = self.client.get(self.home_url)
        self.assertContains(response, 'Dashboard')  # Confirms 'Dashboard' link is present
        self.assertContains(response, 'Log Out')  # Confirms 'Log Out' button is present
        self.assertNotContains(response, 'Sign Up')  # Authenticated users should not see 'Sign Up'
        self.assertNotContains(response, 'Log In')  # Authenticated users should not see 'Log In'

    def test_navbar_for_unauthenticated_user(self):
        # Get response without logging in
        response = self.client.get(self.home_url)

        # Check that unauthenticated users see 'Sign Up' and 'Log In' links
        self.assertContains(response, 'Sign Up')
        self.assertContains(response, 'Log In')
        self.assertNotContains(response, 'Dashboard')  # Unauthenticated users shouldn't see 'Dashboard'
        self.assertNotContains(response, 'Log Out')  # Unauthenticated users shouldn't see 'Log Out'
