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
    song_string = ""
    for song_name in song_names:
        song_string = song_string + " " + song_name

    artist_names = ensure_string_list(top_artists)
    artist_string = ""
    for artist_name in artist_names:
        artist_string = artist_string + " " + artist_name


    genre_names = ensure_string_list(top_genres)
    genre_string = ""
    for genre_name in genre_names:
        genre_string = genre_string + " " + genre_name

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "<50 words how do i think/act/and dress given i listen to:\n"
                + song_string + "\n" + artist_string + "\n" + genre_string + "\n"
                + str(total_minutes) + " minutes recently. "
                + "Give me description, don't include the inputs in your response. "
                + "Also first two word should be one word to describe listener with."
                + "lowercase respective article adjective in front of it (a/an)"
                + "seperate grammar from the rest of the description"
            }
        ]
    )
    content = completion.choices[0].message.content
    my_one_word = "" + content.split(" ")[0] + " " + content.split(" ")[1]
    remaining_text = " ".join(content.split(" ")[2:])
    return remaining_text, my_one_word
