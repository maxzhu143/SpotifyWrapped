"""Views for Wrappedapp."""
import urllib.parse
from django.contrib.auth import login

from .forms import SignUpForm

from .models import SpotifyAccount  # Adjust as per your model for SpotifyAccount
import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import JsonResponse

from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect
import logging

# Initialize logger
logger = logging.getLogger(__name__)


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

@csrf_protect
def unlink(request):
    if request.method == 'POST':
        request.session.flush()
        return redirect('spot_login')  # Redirect to spot_login without triggering re-auth
    return redirect('top_songs')

#ONLY FOR TESTING
def session_status(request):
    return JsonResponse({"session": dict(request.session.items())})

def dashboard(request):
    # Get the Spotify account info if connected
    spotify_account = None
    if request.user.is_authenticated:
        try:
            spotify_account = SpotifyAccount.objects.get(user=request.user)
        except SpotifyAccount.DoesNotExist:
            spotify_account = None

    return render(request, 'dashboard.html', {'spotify_account': spotify_account})


# PLEASE DON'T TOUCH OR I'LL KILL MYSELF
def spot_login(request):
    # Redirect to top_songs if already authenticated
    print("Login START")

    if request.session.get('access_token'):
        print("SIGNED IN")
        return redirect('top_songs')

    print(request.GET.get('login'))

    # Only proceed to Spotify authorization if 'login=true' is explicitly requested
    if request.GET.get('login') == 'true':
        auth_url = (
            'https://accounts.spotify.com/authorize'
            '?response_type=code'
            f'&client_id={settings.SPOTIFY_CLIENT_ID}'
            f'&redirect_uri={settings.SPOTIFY_REDIRECT_URI}'
            '&scope=user-top-read'
        )
        return redirect(auth_url)

    # If no login parameter is set, redirect to top_songs or another page as needed
    return redirect('top_songs')



def callback(request):
    # Step 2: Get the authorization code from the redirect URL
    code = request.GET.get('code')

    # Step 3: Exchange the authorization code for an access token
    token_url = 'https://accounts.spotify.com/api/token'
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
        'client_id': settings.SPOTIFY_CLIENT_ID,
        'client_secret': settings.SPOTIFY_CLIENT_SECRET,
    }

    response = requests.post(token_url, data=token_data)
    token_info = response.json()
    request.session['access_token'] = token_info.get('access_token')

    return redirect('top_songs')


def top_songs(request):
    access_token = request.session.get('access_token')
    if not access_token:
        return render(request, 'top_songs.html')  # No user_name passed when not connected

    # Fetch user profile information
    headers = {'Authorization': f'Bearer {access_token}'}
    profile_url = 'https://api.spotify.com/v1/me'
    profile_response = requests.get(profile_url, headers=headers)
    profile_data = profile_response.json()
    user_name = profile_data.get('display_name', 'Spotify User')

    # Fetch top tracks
    top_tracks_url = 'https://api.spotify.com/v1/me/top/tracks?limit=10'
    tracks_response = requests.get(top_tracks_url, headers=headers)
    tracks_data = tracks_response.json()

    # Extract song details
    songs = [{
        'name': track['name'],
        'artist': track['artists'][0]['name'],
        'album': track['album']['name'],
        'cover': track['album']['images'][0]['url']
    } for track in tracks_data['items']]

    return render(request, 'top_songs.html', {'songs': songs, 'user_name': user_name})


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