"""Views for Wrappedapp."""
import urllib.parse
from django.contrib.auth import login, logout

from django.http import JsonResponse
import requests
from .forms import SignUpForm
from decouple import config

import spotipy
from django.conf import settings

client_id = settings.SPOTIFY_CLIENT_ID
client_secret = settings.SPOTIFY_CLIENT_SECRET
redirect_uri = settings.SPOTIFY_REDIRECT_URI


# Create your views here.
# Wrappedapp/views.py
from django.shortcuts import render, redirect
from django.conf import settings
from spotipy.oauth2 import SpotifyOAuth
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope='user-read-recently-played user-top-read user-library-read'
    )


@login_required
def spotify_connect(request):
    """View to handle Spotify connection button and initiate OAuth flow"""
    try:
        sp_oauth = get_spotify_oauth()
        auth_url = sp_oauth.get_authorize_url()
        return render(request, 'spotify_connect.html', {'auth_url': auth_url})
    except Exception as e:
        messages.error(request, f"Failed to connect to Spotify: {str(e)}")
        return redirect('home')  # Replace with your home view name


@login_required
def spotify_callback(request):
    """Handle the callback from Spotify OAuth"""
    try:
        sp_oauth = get_spotify_oauth()
        code = request.GET.get('code')

        if code:
            # Get tokens from Spotify
            token_info = sp_oauth.get_access_token(code)

            # Store token info in session for now (you might want to store in DB instead)
            request.session['spotify_token_info'] = token_info

            messages.success(request, "Successfully connected to Spotify!")
            return redirect('home')  # Replace with your success page

    except Exception as e:
        messages.error(request, f"Failed to connect to Spotify: {str(e)}")

    return redirect('home')  # Replace with your error page

def home(request):
    access_token = request.session.get("access_token", "")
    return render(request, "home.html", {"access_token": access_token})


def register(request):
    """Handle user registration."""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            return redirect('dashboard')  # Redirect to dashboard after registering
    else:
        form = SignUpForm()

    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    """Display user dashboard."""
    return render(request, 'dashboard.html')


def my_data_view(request):
    data = {"message": "Hello from Django!"}
    return JsonResponse(data)

def spotify_authorize(request):
    spotify_auth_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": "user-top-read",  # Add other scopes as needed
    }
    auth_url = f"{spotify_auth_url}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)

@login_required
def spotify_login(request):
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)
