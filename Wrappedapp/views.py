"""Views for Wrappedapp."""
import urllib.parse
from django.contrib.auth import login, logout
from .models import SpotifyAccount
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import SignUpForm
import openai
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .spotify_api_functions import (
    get_top_songs, get_top_artists, get_top_genres, determine_listening_personality,
    get_sound_town, get_total_minutes_listened, get_top_podcasts, get_artist_thank_you
)
from datetime import datetime, timedelta
from django.shortcuts import redirect
from Wrappedapp.models import SpotifyAccount

openai.api_key = settings.OPENAI_API_KEY
client_id = settings.SPOTIFY_CLIENT_ID
client_secret = settings.SPOTIFY_CLIENT_SECRET
redirect_uri = settings.SPOTIFY_REDIRECT_URI

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

def spotify_callback(request):
    code = request.GET.get("code")
    if not code:
        return redirect('error')  # Handle missing code gracefully

    # Exchange code for tokens
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
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        expires_in = tokens.get("expires_in", 3600)  # Default to 3600 seconds if missing

        # Ensure `expires_at` is calculated
        if expires_in is None:
            expires_in = 3600  # Fallback to 1 hour
        expires_at = datetime.now() + timedelta(seconds=expires_in)

        # Save or update the SpotifyAccount
        spotify_account, created = SpotifyAccount.objects.get_or_create(user=request.user)
        spotify_account.access_token = access_token
        spotify_account.refresh_token = refresh_token
        spotify_account.expires_at = expires_at
        spotify_account.save()

        return redirect('dashboard')

    else:
        print(f"Spotify API error: {response.status_code} - {response.text}")
        return redirect('error')  # Handle API errors gracefully

@csrf_exempt  # CSRF protection is already handled in the form
def unlink(request):
    try:
        # Delete the SpotifyAccount for the current user
        SpotifyAccount.objects.filter(user=request.user).delete()
    except SpotifyAccount.DoesNotExist:
        pass  # Handle cases where the account doesn't exist gracefully
    return redirect('dashboard')  # Redirect to the dashboard


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

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from Wrappedapp.models import SpotifyAccount

@login_required
def dashboard(request):
    # Check if the Spotify account is linked
    spotify_account = SpotifyAccount.objects.filter(user=request.user).first()

    context = {
        "spotify_account": spotify_account,
        "spotify_linked": bool(spotify_account),  # True if Spotify account is linked
    }
    return render(request, "dashboard.html", context)


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

def contact_developers(request):
    return render(request, 'contact_developers.html')


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

def wrapped_carousel(request):
    return render(request, 'wrapped_carousel.html')



def stats_page(request):
    access_token = request.session.get('access_token')
    if not access_token:
        return redirect('spotify_login')

    # Collect data with error handling
    top_songs = get_top_songs(access_token)
    top_artists = get_top_artists(access_token)
    top_genres = get_top_genres(access_token)
    personality = determine_listening_personality(access_token)
    sound_town = get_sound_town([genre[0] for genre in top_genres])
    total_minutes_listened = get_total_minutes_listened(access_token)
    top_podcasts = get_top_podcasts(access_token)  # This might be empty if 404 occurs
    artist_messages = get_artist_thank_you(access_token)

    context = {
        'top_songs': top_songs,
        'top_artists': top_artists,
        'top_genres': top_genres,
        'personality': personality,
        'sound_town': sound_town,
        'total_minutes_listened': total_minutes_listened,
        'top_podcasts': top_podcasts,
        'artist_messages': artist_messages,
    }
    return render(request, 'stats_page.html', context)






@login_required


def custom_logout_view(request):
    logout(request)
    return render(request, 'logout.html')