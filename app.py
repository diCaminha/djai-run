from flask import Flask, request, jsonify
from flask_cors import CORS

from playlist_generator import generate_playlist, PlaylistRequest

app = Flask(__name__)

CORS(app)

@app.route("/playlists/generate", methods=["POST"])
def create_playlist():
    req_data = request.get_json()
    playlist_request = PlaylistRequest(
        minutes=req_data["minutes"],
        genre=req_data["genre"])

    playlist = generate_playlist(playlist_request)
    print(playlist)
    response = {
        "message": "Playlist generated successfully",
        "data": playlist
    }
    return jsonify(response)

@app.route("/register", methods=["POST"])
def register_spotify():
    req_data = request.get_json()
    print(req_data)

if __name__ == '__main__':
    app.run(port=5000)