import requests


# Top Songs (Medium Term)
def get_top_songs(access_token, limit=10):
    url = "https://api.spotify.com/v1/me/top/tracks"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"time_range": "medium_term", "limit": limit}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        items = response.json().get('items', [])
        return items if items else ["Looks like you have never listened to any songs."]
    else:
        print(f"Error fetching top songs: {response.status_code}")
        return ["Looks like you have never listened to any songs."]


# Top Artists (Medium Term)
def get_top_artists(access_token, limit=5):
    url = "https://api.spotify.com/v1/me/top/artists"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"time_range": "medium_term", "limit": limit}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        items = response.json().get('items', [])
        return items if items else ["Looks like you have never listened to any artists."]
    else:
        print(f"Error fetching top artists: {response.status_code}")
        return ["Looks like you have never listened to any artists."]


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

    genre_counts = {genre: genres.count(genre) for genre in set(genres)}
    return sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)


# Estimated Listening Time (Medium Term)
def get_total_minutes_listened(access_token):
    top_tracks = get_top_songs(access_token, limit=50)
    if isinstance(top_tracks, list) and "Looks like you have never listened to any songs." in top_tracks:
        return "Looks like you have no listening time recorded."

    play_count = 30  # Approximate number of times each track was played over the medium term
    total_ms = sum(track['duration_ms'] * play_count for track in top_tracks if isinstance(track, dict))
    return f"{total_ms / 1000 / 60:.2f} minutes" if total_ms > 0 else "Looks like you have no listening time recorded."


# Listening Personality (Medium Term)
def determine_listening_personality(access_token):
    top_songs = get_top_songs(access_token)
    top_artists = get_top_artists(access_token)
    if isinstance(top_songs, list) and "Looks like you have never listened to any songs." in top_songs:
        return ["No listening personality data available."]

    traits = []
    if len(top_songs) > 50:
        traits.append("Explorer")
    if any(artist['popularity'] > 80 for artist in top_artists if isinstance(artist, dict)):
        traits.append("Trend Follower")
    if len(set(song['name'] for song in top_songs if isinstance(song, dict))) < len(top_songs) * 0.5:
        traits.append("Replayer")
    return traits or ["Unique Listener"]


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


# Top Podcasts (Medium Term)
def get_top_podcasts(access_token, limit=5):
    url = "https://api.spotify.com/v1/me/top/shows"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers, params={"time_range": "medium_term", "limit": limit})
    if response.status_code == 200:
        items = response.json().get('items', [])
        return items if items else ["Looks like you have never listened to any podcasts."]
    else:
        print(f"Error fetching top podcasts: {response.status_code}")
        return ["Looks like you have never listened to any podcasts."]


# Artist Messages (Mocked, Medium Term)
def get_artist_thank_you(access_token):
    top_artists = get_top_artists(access_token)
    if isinstance(top_artists, list) and "Looks like you have never listened to any artists." in top_artists:
        return {"Message": "Looks like you have no artist messages."}

    messages = {artist['name']: f"Thank you for listening to {artist['name']}!" for artist in top_artists}
    return messages
