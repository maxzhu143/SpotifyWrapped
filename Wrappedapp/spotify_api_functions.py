import requests

from datetime import datetime, timedelta
import requests
from django.conf import settings
from .models import SpotifyAccount
from django.utils import timezone
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

from datetime import datetime, timedelta
from django.shortcuts import redirect
from Wrappedapp.models import SpotifyWrapped, SpotifyAccount
from django.utils import timezone

openai.api_key = settings.OPENAI_API_KEY
client_id = settings.SPOTIFY_CLIENT_ID
client_secret = settings.SPOTIFY_CLIENT_SECRET
redirect_uri = settings.SPOTIFY_REDIRECT_URI

def get_valid_spotify_token(user):
    """
    Retrieves a valid Spotify access token for the given user.
    Refreshes the token if it has expired.
    """
    try:
        # Retrieve the SpotifyAccount object for the user
        spotify_account = SpotifyAccount.objects.get(user=user)

        # Check if the access token is still valid
        if spotify_account.expires_at > timezone.now():
            return spotify_account.access_token

        # Token is expired; attempt to refresh it
        refresh_url = "https://accounts.spotify.com/api/token"
        response = requests.post(refresh_url, data={
            "grant_type": "refresh_token",
            "refresh_token": spotify_account.refresh_token,
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET,
        })

        if response.status_code == 200:
            tokens = response.json()
            new_access_token = tokens.get("access_token")
            expires_in = tokens.get("expires_in", 3600)  # Default to 3600 seconds

            # Update SpotifyAccount with the new token and expiry
            spotify_account.access_token = new_access_token
            spotify_account.expires_at = timezone.now() + timedelta(seconds=expires_in)
            spotify_account.save()

            return new_access_token
        else:
            raise Exception(f"Failed to refresh token: {response.status_code} {response.text}")

    except SpotifyAccount.DoesNotExist:
        raise Exception("Spotify account not linked to this user.")

def get_user_profile(access_token):
    """Get the current user's Spotify profile information."""
    url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()



# Top Songs (Medium Term)
def get_top_songs(access_token, limit=10):
    url = "https://api.spotify.com/v1/me/top/tracks"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"time_range": "medium_term", "limit": limit}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        items = response.json().get('items', [])
        print(json.dumps(items, indent=2))  # Debug the response structure
        # Extract detailed song information for the template
        songs = []
        for track in items:
            songs.append({
                'name': track.get('name', 'Unknown Song'),  # Add safe default
                'artist': track['artists'][0]['name'] if track.get('artists') else 'Unknown Artist',
                'album': track['album']['name'] if track.get('album') else 'Unknown Album',
                'cover': track['album']['images'][0]['url'] if track.get('album') and track['album'].get('images') else 'https://via.placeholder.com/150',
                'spotify_url': track['external_urls']['spotify'] if track.get('external_urls') else '#',
                'duration_ms': track.get('duration_ms', 0)  # Add a safe default
            })
        return songs
    else:
        print(f"Error fetching top songs: {response.status_code}")
        return []  # Return an empty list as a fallback




# Top Artists (Medium Term)
def get_top_artists(access_token, limit=5):
    url = "https://api.spotify.com/v1/me/top/artists"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"time_range": "medium_term", "limit": limit}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        items = response.json().get('items', [])
        if items:
            top_artists = [
                {
                    'name': artist['name'],
                    'image_url': artist['images'][0]['url'] if artist['images'] else None,
                    'genres': ', '.join(artist['genres'][:2])  # Limit to 2 genres for brevity
                }
                for artist in items
            ]
            return top_artists
        else:
            return [{"name": "Looks like you have never listened to any artists.", "image_url": None, "genres": ""}]
    else:
        print(f"Error fetching top artists: {response.status_code}")
        return [{"name": "Error fetching data from Spotify.", "image_url": None, "genres": ""}]



# Top Genres (Medium Term)
def get_top_genres(access_token):
    top_artists = get_top_artists(access_token, limit=20)
    if isinstance(top_artists, list) and "Looks like you have never listened to any artists." in top_artists:
        return ["Looks like you have never listened to any genres."]

    genres = []
    for artist in top_artists:
        genres.extend(artist.get('genres', []))
    if not genres:
        return ["Looks like you have never listened to any genres."]

    # Count occurrences of each genre
    genre_counts = {genre: genres.count(genre) for genre in set(genres)}

    # Sort genres by count (descending) and take the top 5
    top_5_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    # Return only the genre names
    return [genre for genre, count in top_5_genres]



# Estimated Listening Time (Medium Term)
def get_total_minutes_listened(access_token):
    top_tracks = get_top_songs(access_token, limit=50)
    if isinstance(top_tracks, list) and "Looks like you have never listened to any songs." in top_tracks:
        return "Looks like you have no listening time recorded."

    play_count = 30  # Approximate number of times each track was played over the medium term
    total_ms = sum(track['duration_ms'] * play_count for track in top_tracks if isinstance(track, dict))
    return total_ms / 1000.0 / 60.0



# Estimated Sound Town (Medium Term)
def get_sound_town(top_genres):
    if isinstance(top_genres, list) and "Looks like you have never listened to any genres." in top_genres:
        return "No Sound Town available."

    town_profiles = {
        "Pop City": ["pop", "dance pop", "pop rock"],
        "Jazz Town": ["jazz", "smooth jazz", "soul"],
        "Rockville": ["rock", "hard rock", "alternative rock"],
    }
    for town, genres in town_profiles.items():
        if any(genre in top_genres for genre in genres):
            return town
    return "Unknown Sound Town"





# Artist Messages (Mocked, Medium Term)
def get_artist_thank_you(access_token):
    top_artists = get_top_artists(access_token)
    if isinstance(top_artists, list) and "Looks like you have never listened to any artists." in top_artists:
        return {"Message": "Looks like you have no artist messages."}

    messages = {artist['name']: f"Thank you for listening to {artist['name']}!" for artist in top_artists}
    return messages