import json
from functools import reduce

from openai import OpenAI
from dotenv import load_dotenv
import os
import logging

# Load the .env file
load_dotenv()

client = OpenAI(api_key=os.getenv('OPEN_AI_KEY'))


class PlaylistRequest:
    def __init__(self, minutes, style):
        self.minutes = minutes
        self.style = style


def check_playlist(playlist_candidate, seconds_required):
    if "length_in_seconds" not in playlist_candidate or "songs" not in playlist_candidate:
        logging.info("Payload structure incorrect.")
        return False, "Payload structure incorrect."

    sum_real_total_seconds = reduce(lambda acc, song: acc + song['seconds'], playlist_candidate["songs"], 0)

    if sum_real_total_seconds < seconds_required:
        logging.info("Total of time created by AI is smaller than required.")
        return False, "Total of time created by AI is smaller than required."

    if sum_real_total_seconds > (seconds_required + 100):
        logging.info("Playlist created is too long.")
        return False, "Playlist created is too long."

    logging.info("Playlist finally found!!")
    return True, "Playlist finally found!!"


def get_completion_from_ai(conversation):
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation
    )


def generate_playlist(playlist_req: PlaylistRequest):
    user_sample = f"""
                I need you to create a music playlist where the total duration of all songs combined is as close 
                as possible to {playlist_req.minutes*60} seconds without going under. 
                The playlist should follow the {playlist_req.style} genre. 
                Provide song titles, artist names, and each song's duration in seconds. 
                
                Rules to follow:
                - Prioritize well-known songs that fit the genre and keep the duration as accurate as possible. 
                - Ensure the sum of the song durations is at least the given time limit, but try not to exceed it by much.
                - If you're unsure of a song's real duration, exclude it from the list. Prioritize accuracy for the song lengths, and only use songs that match their real duration. 
                - Total of seconds: {int(playlist_req.minutes)*60}
                - Style: {playlist_req.style}.
            """ + """
            
                - the response should be exaclty on this json structure:
                {
                    "length_in_seconds": <sum all seconds attribute and put the sum here>,
                    "songs": [
                        {
                            "songName": <NAME OF THE SONG>,
                            "artist": <ARTIST OR GROUP NAME>,
                            "seconds": <TOTAL LENGTH IN SECONDS>
                        },
                        {
                            "songName": <NAME OF THE SONG>,
                            "artist": <ARTIST OR GROUP NAME>,
                            "seconds": <TOTAL LENGTH IN SECONDS>
                        },
                        {
                            "songName": <NAME OF THE SONG>,
                            "artist": <ARTIST OR GROUP NAME>,
                            "seconds": <TOTAL LENGTH IN SECONDS>
                        }
                    ]
                }
            """



    conversation = [
        {
            "role": "user",
            "content": user_sample}
    ]
    count_tries = 0
    while count_tries < 4:
        try:
            completion = get_completion_from_ai(conversation)
            playlist_candidate = json.loads(
                completion.choices[0].message.content.replace("json```", "").replace("```", "").replace("json", ""))

            length_playlist_in_sec = int(playlist_req.minutes) * 60

            playlist_validated, message = check_playlist(playlist_candidate, length_playlist_in_sec)
            if playlist_validated:
                return playlist_candidate
            else:
                conversation.append({
                    "role": "assistant",
                    "content": completion.choices[0].message.content
                })
                conversation.append({
                    "role": "user",
                    "content": f"It's wrong. {message}. Please check the playlist and fix it. Follow the rules I gave you on creating the playlist. "
                               f"And then return only the json object that I ask you, "
                               f"dont need to apologyze or send another message beyond the json structure"
                })
        except Exception as e:
            logging.error(e)
            count_tries+= 1
