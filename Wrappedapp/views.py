"""Views for Wrappedapp."""
import urllib.parse
from django.contrib.auth import login, logout

from django.http import JsonResponse
import requests
from .forms import SignUpForm


from django.shortcuts import render, redirect
from django.conf import settings
from .models import SpotifyAccount  # Adjust as per your model for SpotifyAccount
import spotipy
from spotipy.oauth2 import SpotifyOAuth





client_id = settings.SPOTIFY_CLIENT_ID
client_secret = settings.SPOTIFY_CLIENT_SECRET
redirect_uri = settings.SPOTIFY_REDIRECT_URI


# Create your views here.
# Wrappedapp/views.py

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



def dashboard(request):
    # Get the Spotify account info if connected
    spotify_account = None
    if request.user.is_authenticated:
        try:
            spotify_account = SpotifyAccount.objects.get(user=request.user)
        except SpotifyAccount.DoesNotExist:
            spotify_account = None

    return render(request, 'dashboard.html', {'spotify_account': spotify_account})

def spotify_connect(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-read-private user-read-email",
    )

    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)
    return redirect(auth_url)
def spotify_disconnect(request):
    if request.user.is_authenticated:
        try:
            spotify_account = SpotifyAccount.objects.get(user=request.user)
            spotify_account.delete()  # Remove the account info
        except SpotifyAccount.DoesNotExist:
            pass
    return redirect('dashboard')

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

def spotify_callback(request):
    code = request.GET.get("code")
    token_url = "https://accounts.spotify.com/api/token"

    response = requests.post(token_url, data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
    })

    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        # Save tokens in the session (or database) for later use
        request.session["access_token"] = access_token
        request.session["refresh_token"] = refresh_token

        # Redirect to another view, or render a template
        return redirect("home")  # Change 'home' to your target URL
    else:
        return redirect("error")  # Handle errors gracefully