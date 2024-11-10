"""Views for Wrappedapp."""
import urllib.parse
from django.contrib.auth import login

from .forms import SignUpForm

from .models import SpotifyAccount  # Adjust as per your model for SpotifyAccount
import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
import requests
from .forms import SignUpForm
from decouple import config
import openai
from django.views.decorators.csrf import csrf_exempt
import json







openai.api_key = settings.OPENAI_API_KEY
client_id = settings.SPOTIFY_CLIENT_ID
client_secret = settings.SPOTIFY_CLIENT_SECRET
redirect_uri = settings.SPOTIFY_REDIRECT_URI


# Create your views here.
# Wrappedapp/views.py



def spot_login(request):
    # Step 1: Redirect the user to Spotify's authorization page
    print(request.session.keys())
    #return redirect('top_songs')

    auth_url = (
        'https://accounts.spotify.com/authorize'
        '?response_type=code'
        f'&client_id={settings.SPOTIFY_CLIENT_ID}'
        f'&redirect_uri={settings.SPOTIFY_REDIRECT_URI}'
        '&scope=user-top-read'
    )
    return redirect(auth_url)

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

@csrf_exempt  # CSRF protection is already handled in the form
def unlink(request):
    print("UNLINK")
    print(request)
    if request.method == 'POST':
        print(request.session.keys())
        print("Currently Unlinking")
        # Clear the session to log the user out of Spotify
        request.session.pop('access_token', None)
        request.session.pop('access_token', None)
        request.session.pop('refresh_token', None)
        request.session.pop('expires_at', None)
        print("hey")
        return redirect('dashboard')  # Redirect to login page or homepage

def top_songs(request):
    access_token = request.session.get('access_token')
    if not access_token:
        print("Access token is needed")
        return redirect('spot_login')

    headers = {'Authorization': f'Bearer {access_token}'}

    # Get user profile information for the display name
    profile_url = 'https://api.spotify.com/v1/me'
    profile_response = requests.get(profile_url, headers=headers)
    if profile_response.status_code == 200:
        profile_data = profile_response.json()
        user_name = profile_data.get('display_name', 'Spotify User')
    else:
        print("Failed to fetch user profile:", profile_response.status_code, profile_response.text)
        user_name = 'Spotify User'

    # Fetch top tracks
    top_tracks_url = 'https://api.spotify.com/v1/me/top/tracks?limit=10'
    tracks_response = requests.get(top_tracks_url, headers=headers)
    if tracks_response.status_code == 200:
        tracks_data = tracks_response.json()

        # Extract song details if there are items in the response
        songs = [{
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name'],
            'cover': track['album']['images'][0]['url']
        } for track in tracks_data.get('items', [])]  # Safely handle missing 'items' key
    else:
        print("Failed to fetch top tracks:", tracks_response.status_code, tracks_response.text)
        songs = []  # Provide an empty list as a fallback

    return render(request, 'top_songs.html', {'songs': songs, 'user_name': user_name})

def home(request):
    access_token = request.session.get("access_token", "")
    return render(request, "home.html", {"access_token": access_token})

@login_required(login_url='login')
def dashboard(request):
    # Get the Spotify account info if connected
    spotify_account = None
    if request.user.is_authenticated:
        try:
            spotify_account = SpotifyAccount.objects.get(user=request.user)
        except SpotifyAccount.DoesNotExist:
            spotify_account = None
    return render(request, 'dashboard.html', {'spotify_account': spotify_account})

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

#might cause issues becuase we have two
@login_required
def dashboard(request):
    """Display user dashboard."""
    return render(request, 'dashboard.html')

def contact_developers(request):
    return render(request, 'contact_developers.html')

#might not need
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

@csrf_exempt
def describe_user_tracks(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            track_names = data.get('trackNames', [])

            # Create a prompt for the LLM using the track names
            prompt = f"Based on the top tracks that include {', '.join(track_names)}, " \
                     "describe how this user might act or think in terms of personality and music preferences."

            # Call OpenAI API to generate the description
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                max_tokens=100
            )
            description = response.choices[0].text.strip()

            # Return the description to the frontend
            return JsonResponse({'description': description})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)
