import openai
from django.views.decorators.csrf import csrf_exempt

from SpotifyWrapped import settings

openai.api_key = settings.OPENAI_API_KEY

@csrf_exempt
def generate_psychoanalysis(top_songs, top_artists, top_genres, total_minutes):
    """
    Use OpenAI to generate a psychoanalysis based on the user's listening habits.
    """
    print("hey")
    openai.api_key = settings.OPENAI_API_KEY
    # Format the input data
    song_names = ensure_string_list(top_songs, key='name')
    artist_names = ensure_string_list(top_artists)
    genre_names = ensure_string_list(top_genres)

    prompt = f"""
    Based on the following listening habits, provide a psychoanalysis of the user:

    - Top Songs: {', '.join(song_names)}
    - Top Artists: {', '.join(artist_names)}
    - Top Genres: {', '.join(genre_names)}
    - Total Minutes Listened: {total_minutes}

    What does this suggest about their personality, mood, and lifestyle preferences?
    """

    try:
        # Call OpenAI API
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=200,  # Adjust token limit as needed
            temperature=0.7,  # Adjust creativity
        )
        # Extract and return the generated psychoanalysis
        print(response.choices[0].text.strip())
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "Unable to generate psychoanalysis at this time."


def ensure_string_list(sequence, key=None):
    """
    Converts a list of dictionaries or other objects into a list of strings.
    - If key is provided, extracts the value corresponding to the key.
    - If key is None, ensures all elements are strings.
    """
    if key:
        return [str(item[key]) for item in sequence if key in item]
    return [str(item) for item in sequence]
