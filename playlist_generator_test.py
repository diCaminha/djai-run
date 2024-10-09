import json

from business.playlist_generator import check_playlist, PlaylistRequest, generate_playlist

import unittest
from unittest.mock import patch, MagicMock

class TestPlaylistGenerator(unittest.TestCase):

    def test_check_playlist_valid(self):
        playlist_candidate = {
            "length_in_seconds": 300,
            "songs": [
                {"songName": "Song A", "artist": "Artist A", "seconds": 200},
                {"songName": "Song B", "artist": "Artist B", "seconds": 100},
            ]
        }
        seconds_required = 300
        result, message = check_playlist(playlist_candidate, seconds_required)
        self.assertTrue(result)
        self.assertEqual(message, "Playlist finally found!!")

    def test_check_playlist_invalid_structure(self):
        playlist_candidate = {
            "songs": [
                {"songName": "Song A", "artist": "Artist A", "seconds": 200},
                {"songName": "Song B", "artist": "Artist B", "seconds": 100},
            ]
        }
        seconds_required = 300
        result, message = check_playlist(playlist_candidate, seconds_required)
        self.assertFalse(result)
        self.assertEqual(message, "Payload structure incorrect.")

    def test_check_playlist_too_short(self):
        playlist_candidate = {
            "length_in_seconds": 200,
            "songs": [
                {"songName": "Song A", "artist": "Artist A", "seconds": 100},
                {"songName": "Song B", "artist": "Artist B", "seconds": 100},
            ]
        }
        seconds_required = 300
        result, message = check_playlist(playlist_candidate, seconds_required)
        self.assertFalse(result)
        self.assertEqual(message, "Total of time created by AI is smaller than required.")

    def test_check_playlist_too_long(self):
        playlist_candidate = {
            "length_in_seconds": 500,
            "songs": [
                {"songName": "Song A", "artist": "Artist A", "seconds": 300},
                {"songName": "Song B", "artist": "Artist B", "seconds": 200},
            ]
        }
        seconds_required = 300
        result, message = check_playlist(playlist_candidate, seconds_required)
        self.assertFalse(result)
        self.assertEqual(message, "Playlist created is too long.")

    @patch('business.playlist_generator.get_completion_from_ai')  # Replace 'your_module' with your module name
    def test_generate_playlist(self, mock_get_completion):
        # Mock the response from get_completion_from_ai
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = json.dumps({
            "length_in_seconds": 300,
            "songs": [
                {"songName": "Song A", "artist": "Artist A", "seconds": 150},
                {"songName": "Song B", "artist": "Artist B", "seconds": 150},
            ]
        })
        mock_get_completion.return_value = mock_completion

        playlist_req = PlaylistRequest(minutes=5, style="pop")
        result = generate_playlist(playlist_req)
        expected_result = {
            "length_in_seconds": 300,
            "songs": [
                {"songName": "Song A", "artist": "Artist A", "seconds": 150},
                {"songName": "Song B", "artist": "Artist B", "seconds": 150},
            ]
        }
        self.assertEqual(result, expected_result)

    @patch('business.playlist_generator.get_completion_from_ai')  # Replace 'your_module' with your module name
    def test_generate_playlist_with_retries(self, mock_get_completion):
        # First response: invalid playlist (too short)
        mock_completion1 = MagicMock()
        mock_completion1.choices = [MagicMock()]
        mock_completion1.choices[0].message.content = json.dumps({
            "length_in_seconds": 200,
            "songs": [
                {"songName": "Song A", "artist": "Artist A", "seconds": 100},
                {"songName": "Song B", "artist": "Artist B", "seconds": 100},
            ]
        })

        # Second response: valid playlist
        mock_completion2 = MagicMock()
        mock_completion2.choices = [MagicMock()]
        mock_completion2.choices[0].message.content = json.dumps({
            "length_in_seconds": 310,
            "songs": [
                {"songName": "Song C", "artist": "Artist C", "seconds": 155},
                {"songName": "Song D", "artist": "Artist D", "seconds": 155},
            ]
        })

        # Set side effect for successive calls
        mock_get_completion.side_effect = [mock_completion1, mock_completion2]

        playlist_req = PlaylistRequest(minutes=5, style="rock")
        result = generate_playlist(playlist_req)
        expected_result = {
            "length_in_seconds": 310,
            "songs": [
                {"songName": "Song C", "artist": "Artist C", "seconds": 155},
                {"songName": "Song D", "artist": "Artist D", "seconds": 155},
            ]
        }
        self.assertEqual(result, expected_result)
        self.assertEqual(mock_get_completion.call_count, 2)
