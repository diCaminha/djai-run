import json

from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import requests
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from playlist_generator import generate_playlist, PlaylistRequest

app = Flask(__name__)

CORS(app)

load_dotenv()


def __get_access_token(authorization_header):
    if authorization_header and authorization_header.startswith('Bearer '):
        return authorization_header.split(' ')[1]

def __get_song_uris(song_info_list, sp):
    song_uris = []
    for song in song_info_list:
        query = f"track:{song['track']} artist:{song['artist']}"
        result = sp.search(q=query, type='track', limit=1)
        tracks = result['tracks']['items']
        if tracks:
            song_uri = tracks[0]['uri']
            song_uris.append(song_uri)
        else:
            print(f"Song '{song['track']}' by '{song['artist']}' not found.")
    return song_uris

@app.route("/playlists/generate", methods=["POST"])
def create_playlist():
    authorization_header = request.headers.get('Authorization')
    access_token = __get_access_token(authorization_header)

    req_data = request.get_json()
    playlist_request = PlaylistRequest(
        minutes=req_data["minutes"],
        genre=req_data["genre"])

    playlist_str = generate_playlist(playlist_request).replace("```","").replace("```","")
    playlist = json.loads(playlist_str)

    SCOPE = 'playlist-modify-public'

    # Authenticate with Spotify
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                                                   client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                                                   redirect_uri=req_data["redirect_uri"],
                                                   scope=SCOPE))

    user = sp.current_user()
    user_id = user['id']

    song_info_list = []

    for song in playlist:
        song_obj_spotify = {"track": song["songName"], "artist": song["artist"]}
        song_info_list.append(song_obj_spotify)

    song_uris = __get_song_uris(song_info_list, sp)

    playlist_name = f"{playlist_request.minutes} minutes of {playlist_request.genre}"
    playlist_description = 'Djai created a list for you! ;)'

    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True, description=playlist_description)
    playlist_id = playlist['id']

    sp.playlist_add_items(playlist_id=playlist_id, items=song_uris)
    print(f"Playlist '{playlist_name}' created successfully with {len(song_uris)} songs.")

    print(playlist)

    return playlist

@app.route("/register", methods=["POST"])
def register_spotify():
    req_data = request.get_json()
    print(req_data)

    payload = {
        "grant_type": "authorization_code",
        "code": req_data["code"],
        "redirect_uri": req_data["redirect_uri"]
    }

    auth_header = base64.b64encode(f"{os.getenv("SPOTIFY_CLIENT_ID")}:{os.getenv("SPOTIFY_SECRET_KEY")}".encode('utf-8')).decode('utf-8')
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + auth_header
    }
    response = requests.post("https://accounts.spotify.com/api/token", data=payload, headers=headers)
    if response.status_code == 200:
        token_info = response.json()
        print(token_info)
        return {"data": token_info}
    else:
        return 'An error occurred', response.status_code


if __name__ == '__main__':
    app.run(port=5000)