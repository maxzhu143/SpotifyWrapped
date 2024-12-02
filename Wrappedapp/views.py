"""Views for Wrappedapp."""
import urllib.parse
import logging
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

from .openai_functions import generate_psychoanalysis
from .spotify_api_functions import (
    get_valid_spotify_token, get_top_songs, get_top_artists, get_top_genres,
    get_sound_town, get_total_minutes_listened, get_artist_thank_you
)
from datetime import datetime, timedelta
from django.shortcuts import redirect
from Wrappedapp.models import SpotifyWrapped, SpotifyAccount
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
logger = logging.getLogger(__name__)
openai.api_key = settings.OPENAI_API_KEY
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
    return render(request, "home.html")

@login_required
def dashboard(request):
    # Check if the Spotify account is linked
    spotify_account = SpotifyAccount.objects.filter(user=request.user).first()

    # Get the user's saved SpotifyWrapped objects
    wrapped_objects = SpotifyWrapped.objects.filter(user=request.user).order_by('-created_at')

    if spotify_account:
        access_token = get_valid_spotify_token(user=request.user)
        profile_response = requests.get('https://api.spotify.com/v1/me', headers={'Authorization': f'Bearer {access_token}'})
        user_name = profile_response.json().get('display_name', 'Spotify User')
        print(profile_response.json())
    else:
        user_name = 'Spotify User'

    context = {
        "spotify_account": spotify_account,
        "spotify_linked": bool(spotify_account),  # True if Spotify account is linked
        "wrapped_objects": wrapped_objects,  # Add the saved wrapped objects to the context
        "user_name" : user_name,
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

        # Process top songs for the carousel
        top_songs = wrapped.top_songs  # Assuming `top_songs` is a list of dictionaries

        for song in top_songs:

            # Add fallback values for Spotify URL, album cover, and artist name
            song['spotify_url'] = song.get('spotify_url', '#')  # Fallback to '#' if no URL
            song['album_cover'] = song.get('album_cover', 'default_album_cover.jpg')  # Default cover image
            song['artist'] = song.get('artist', 'Unknown Artist')  # Fallback artist name

        # Pass the Wrapped object and processed top songs to the template
        return render(request, 'wrapped_carousel.html', {
            'wrapped': wrapped,
            'top_songs': top_songs,  # Pass the top songs data to the template
        })

    except SpotifyWrapped.DoesNotExist:
        # Handle case where the Wrapped object does not exist
        return render(request, 'error.html', {'message': 'Spotify Wrapped not found.'})



@login_required
def create_wrapped(request):
    """
    Handles the creation of a SpotifyWrapped object for the logged-in user.
    Fetches data from Spotify and processes it.
    """
    try:
        logger.info("Starting 'create_wrapped' for user: %s", request.user.username)

        # Fetch Spotify token
        spotify_token = get_valid_spotify_token(request.user)
        if not spotify_token:
            raise ValueError("Failed to retrieve Spotify token for the user.")

        # Fetch Spotify data
        logger.info("Fetching Spotify data...")
        top_songs = get_top_songs(spotify_token)
        logger.info(f"Top songs: {top_songs}")
        top_artists = get_top_artists(spotify_token)
        logger.info(f"Top artists: {top_artists}")
        top_genres = get_top_genres(spotify_token)
        logger.info(f"Top genres: {top_genres}")
        total_minutes = get_total_minutes_listened(spotify_token)
        sound_town = get_sound_town(top_genres)
        artist_thank_you = get_artist_thank_you(spotify_token)
        hours = total_minutes / 60

        # Generate psychoanalysis using OpenAI
        logger.info("Generating psychoanalysis...")
        personality, personality_word = generate_psychoanalysis(
            top_songs, top_artists, top_genres, total_minutes
        )
        logger.info(f"Psychoanalysis: {personality} ({personality_word})")

        # Create SpotifyWrapped object
        logger.info("Creating SpotifyWrapped object...")
        wrapped = SpotifyWrapped.objects.create(
            user=request.user,
            title=f"My Spotify Wrapped {SpotifyWrapped.objects.filter(user=request.user).count() + 1}",
            top_songs=top_songs,
            top_artists=top_artists,
            top_genres=top_genres,
            personality=personality,
            personality_word=personality_word,
            total_minutes_listened=total_minutes,
            sound_town=sound_town,
            artist_thank_you=artist_thank_you,
        )

        logger.info(f"SpotifyWrapped created successfully with ID: {wrapped.id}")
        return redirect('wrapped_carousel', wrapped_id=wrapped.id)

    except Exception as e:
        logger.error(f"Error in create_wrapped: {e}", exc_info=True)
        return render(request, 'error.html', {'message': f"Failed to create Spotify Wrapped: {e}"})

@login_required
def custom_logout_view(request):
    logout(request)
    return render(request, 'logout.html')

@login_required
def delete_wrapped(request, wrapped_id):
    wrapped = get_object_or_404(SpotifyWrapped, id=wrapped_id, user=request.user)
    wrapped.delete()
    return redirect('dashboard')  # Replace 'home' with the name of your main page or Wrapped list page.

@login_required
def save_wrapped(request, wrapped_id):
    wrapped = get_object_or_404(SpotifyWrapped, id=wrapped_id, user=request.user)
    # The object is already created, so just redirect to the dashboard.
    return redirect('dashboard')

@login_required
def discard_wrapped(request, wrapped_id):
    wrapped = get_object_or_404(SpotifyWrapped, id=wrapped_id, user=request.user)
    wrapped.delete()
    return redirect('dashboard')
@login_required
def public_wraps(request):
    # Fetch all public wraps including the user's public wraps
    wraps = SpotifyWrapped.objects.filter(is_public=True).order_by('-created_at')
    user_wraps = SpotifyWrapped.objects.filter(user=request.user, is_public=True)
    context = {
        'wraps': wraps,
        'user_wraps': user_wraps,
    }
    return render(request, 'public_wraps.html', context)
@login_required
def toggle_visibility(request, wrapped_id):
    wrap = get_object_or_404(SpotifyWrapped, id=wrapped_id, user=request.user)
    wrap.is_public = not wrap.is_public
    wrap.save()
    return redirect('dashboard')

from deep_translator import GoogleTranslator
from django.http import JsonResponse
import json


import logging

logger = logging.getLogger(__name__)

def translate_text(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            target_lang = data.get('lang', 'en')

            logger.info(f"Received translation request: text='{text}', lang='{target_lang}'")  # Debug log

            # Use deep-translator to translate
            translated_text = GoogleTranslator(source='auto', target=target_lang).translate(text)

            logger.info(f"Translated text: {translated_text}")  # Debug log

            return JsonResponse({'translated_text': translated_text})
        except Exception as e:
            logger.error(f"Error during translation: {e}")  # Debug log
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def translate_batch(request):
    """
    Translate multiple texts to the specified target language.
    """
    if request.method == 'POST':
        try:
            # Parse the JSON body
            data = json.loads(request.body)
            texts = data.get('texts', [])
            target_lang = data.get('lang', 'en')  # Default to English if no language is provided

            # Translate each text and store results in a dictionary
            translations = {}
            for text in texts:
                translations[text] = GoogleTranslator(source='auto', target=target_lang).translate(text)

            return JsonResponse({'translations': translations})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)