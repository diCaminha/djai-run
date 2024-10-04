from openai import OpenAI
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

client = OpenAI(api_key=os.getenv('OPEN_AI_KEY'))

MINUTES = 30
GENRE = "hiphop"
START_RITHM = "soft"
FINISH_RITHM = "hard"

system_prompt = """
    You are an amazing DJ that can choose the best songs to create a playlist.
    Your speciality is in creating playlist of songs for runners to run listening to it, 
    according with his personal desired.
    
    You should return the response in list in a json format with objects in the list like this:
    {
        "songName": <NAME OF THE SONG>,
        "artist": <ARTIST OR GROUP NAME>,
        "minutes": <TOTAL MINUTES OF THE SONG>
    }
    
    The response should contain only the list of songs, nothing else.
"""

user_prompt = f"""
    I want you to create a playlist using the following requests:
    The total of minutes suming all the songs should be very close to {MINUTES}, and cannot be fewer than {MINUTES} minutes.
    The genre of the songs should be {GENRE}
    The progression of the rhythm of the musics on the playlist should start with {START_RITHM} to {FINISH_RITHM} songs.
"""


completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": system_prompt},
        {
            "role": "user",
            "content": user_prompt
        }
    ]
)

print(completion.choices[0].message.content)