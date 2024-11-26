"""Views for Wrappedapp."""
import urllib.parse
from django.contrib.auth import login, logout
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
    get_valid_spotify_token, get_top_songs, get_top_artists, get_top_genres,
    get_sound_town, get_total_minutes_listened, get_top_podcasts, get_artist_thank_you
)
from datetime import datetime, timedelta
from django.shortcuts import redirect
from Wrappedapp.models import SpotifyWrapped, SpotifyAccount
from django.utils import timezone

from .utils import generate_psychoanalysis

client_id = settings.SPOTIFY_CLIENT_ID
client_secret = settings.SPOTIFY_CLIENT_SECRET
redirect_uri = settings.SPOTIFY_REDIRECT_URI



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




def home(request):
    access_token = request.session.get("access_token", "")
    return render(request, "home.html", {"access_token": access_token})

@login_required
def dashboard(request):
    # Check if the Spotify account is linked
    spotify_account = SpotifyAccount.objects.filter(user=request.user).first()

    # Get the user's saved SpotifyWrapped objects
    wrapped_objects = SpotifyWrapped.objects.filter(user=request.user).order_by('-created_at')

    context = {
        "spotify_account": spotify_account,
        "spotify_linked": bool(spotify_account),  # True if Spotify account is linked
        "wrapped_objects": wrapped_objects,  # Add the saved wrapped objects to the context
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

@login_required
def wrapped_carousel(request, wrapped_id):
    """
    View to render the Wrapped Carousel page for a specific SpotifyWrapped object.
    """
    try:
        # Fetch the specific SpotifyWrapped object for the user
        wrapped = SpotifyWrapped.objects.get(id=wrapped_id, user=request.user)

        # Pass the SpotifyWrapped data to the template
        return render(request, 'wrapped_carousel.html', {'wrapped': wrapped})
    except SpotifyWrapped.DoesNotExist:
        # Handle case where the Wrapped object does not exist
        return render(request, 'error.html', {'message': 'Spotify Wrapped not found.'})


@login_required
def create_wrapped(request):
    try:
        # Fetch Spotify token from the linked account
        spotify_token = get_valid_spotify_token(request.user)
        # Fetch data from Spotify API
        top_songs = get_top_songs(spotify_token)
        top_artists = get_top_artists(spotify_token)
        top_genres = get_top_genres(spotify_token)
        total_minutes = get_total_minutes_listened(spotify_token)
        sound_town = get_sound_town(top_genres)
        artist_thank_you = get_artist_thank_you(spotify_token)
        top_podcasts = get_top_podcasts(spotify_token)
        personality = generate_psychoanalysis(top_songs, top_artists, top_genres, total_minutes)


        # Create a new SpotifyWrapped object
        wrapped = SpotifyWrapped.objects.create(
            user=request.user,
            title=f"My Spotify Wrapped {SpotifyWrapped.objects.filter(user=request.user).count() + 1}",
            top_songs=top_songs,
            top_artists=top_artists,
            top_genres=top_genres,
            personality=personality,
            total_minutes_listened=total_minutes,
            sound_town=sound_town,
            artist_thank_you=artist_thank_you,
            top_podcasts="top_podcasts",
        )

        # Redirect to the carousel view to display the new Wrapped data
        return redirect('wrapped_carousel', wrapped_id=wrapped.id)
    except Exception as e:
        print(f"Error fetching Spotify data: {e}")
        return render(request, 'error.html', {'message': f"Failed to create Spotify Wrapped: {e}"})

@login_required


def custom_logout_view(request):
    logout(request)
    return render(request, 'logout.html')