from openai import OpenAI

from SpotifyWrapped.settings import OPENAI_API_KEY

client = OpenAI()






from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


def ensure_string_list(sequence, key=None):
    """
    Converts a list of dictionaries or other objects into a list of strings.
    - If key is provided, extracts the value corresponding to the key.
    - If key is None, ensures all elements are strings.
    """
    if key:
        return [str(item[key]) for item in sequence if key in item]
    return [str(item) for item in sequence]


@csrf_exempt
def generate_psychoanalysis(top_songs, top_artists, top_genres, total_minutes):
    """
    Use OpenAI to generate a psychoanalysis based on the user's listening habits.
    """
    # Set the OpenAI API key
      # Or set using os.environ.get("OPENAI_API_KEY")

    # Format the input data
    song_names = ensure_string_list(top_songs, key='name')
    artist_names = ensure_string_list(top_artists)
    genre_names = ensure_string_list(top_genres)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "<50 words how do i think/act/and dress given that i listen to:"
                           "." + song_names[0] + artist_names[0] + genre_names[0] + "only give me a description, don't include"
                                                                                    "the inputs in your response",
            }
        ]
    )

    print(completion.choices[0].message)
    return completion.choices[0].message
