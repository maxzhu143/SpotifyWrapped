"""Views for Wrappedapp."""
import urllib.parse
from django.contrib.auth import login

from .forms import SignUpForm

from .models import SpotifyAccount  # Adjust as per your model for SpotifyAccount
import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_protect
import logging

import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.sessions.models import Session

# Initialize logger
logger = logging.getLogger(__name__)


client_id = settings.SPOTIFY_CLIENT_ID
client_secret = settings.SPOTIFY_CLIENT_SECRET
redirect_uri = settings.SPOTIFY_REDIRECT_URI


# Create your views here.
# Wrappedapp/views.py

# Step 1: Spotify Login
def spotify_login(request):
    scope = "user-top-read"
    auth_url = (
        "https://accounts.spotify.com/authorize"
        f"?client_id={settings.SPOTIFY_CLIENT_ID}"
        f"&response_type=code&redirect_uri={settings.SPOTIFY_REDIRECT_URI}"
        f"&scope={scope}"
    )
    return redirect(auth_url)


# Step 2: Spotify Callback
def spotify_callback(request):
    code = request.GET.get('code')
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
        'client_id': settings.SPOTIFY_CLIENT_ID,
        'client_secret': settings.SPOTIFY_CLIENT_SECRET,
    }
    response = requests.post(token_url, data=payload)
    data = response.json()

    access_token = data.get('access_token')
    if access_token:
        request.session['spotify_access_token'] = access_token
    return redirect('homepage')


# Step 3: Spotify Logout
def spotify_logout(request):
    request.session.pop('spotify_access_token', None)
    return redirect('homepage')


# Step 4: Homepage to Display Spotify Data
def homepage(request):
    access_token = request.session.get('spotify_access_token')
    if not access_token:
        return render(request, 'homepage.html', {'is_connected': False})

    # Fetch Spotify user data
    headers = {'Authorization': f'Bearer {access_token}'}

    # Get the user's profile
    user_profile = requests.get("https://api.spotify.com/v1/me", headers=headers).json()
    user_name = user_profile.get('display_name', 'Spotify User')

    # Get the top 5 tracks
    top_tracks_url = "https://api.spotify.com/v1/me/top/tracks?limit=5&time_range=short_term"
    top_tracks = requests.get(top_tracks_url, headers=headers).json().get('items', [])
    top_tracks = [{'name': track['name'], 'artist': track['artists'][0]['name']} for track in top_tracks]

    # Get the top genre and total listening time (approximation, as Spotify doesn't directly provide listening time)
    top_genre = top_tracks[0]['artist'] if top_tracks else "Unknown Genre"
    total_time = sum(track['duration_ms'] for track in top_tracks) // 60000  # in minutes

    context = {
        'is_connected': True,
        'user_name': user_name,
        'top_tracks': top_tracks,
        'top_genre': top_genre,
        'total_listening_time': total_time,
    }
    return render(request, 'homepage.html', context)
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
    print("This is so fucked")
    print('spotify_token' in request.session)
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
    print(request.session.get('access_token'))

    print("Login START")

    if request.session.get('access_token'):
        print("SIGNED IN")
        return redirect('top_songs')

    print(request.GET.get('spot_login'))

    # Only proceed to Spotify authorization if 'login=true' is explicitly requested

    auth_url = (
        'https://accounts.spotify.com/authorize'
        '?response_type=code'
        f'&client_id={settings.SPOTIFY_CLIENT_ID}'
        f'&redirect_uri={settings.SPOTIFY_REDIRECT_URI}'
        '&scope=user-top-read'
    )

    request.session.flush()

    return redirect(auth_url)


    # If no login parameter is set, redirect to top_songs or another page as needed
    return redirect('top_songs')



def callback(request):
    print("CALLBACK")
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
