from openai import OpenAI

from SpotifyWrapped.settings import OPENAI_API_KEY

client = OpenAI()


completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Psychoanalyse this spotify user given his top songs." +
        }
    ]
)

print(completion.choices[0].message)