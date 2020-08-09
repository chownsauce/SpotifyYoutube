"""
Step 1: Log into Youtube
Step 2: Grab videos
Step 3: Create a new Playlist
Step 4: Search for the Song
Step 5: Add this song into the new Spotify playlist
"""

import os
import json
import requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl
import youtube_dl.utils

from secrets import spotify_token, spotify_user_id, channel_id
from exceptions import ResponseException

class CreatePlaylist:
    def __init__(self):
        self.youtube_client = self.get_youtube_client()
        self.all_song_info = {}

    # Step 1: Log into Youtube
    def get_youtube_client(self):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secret.json"

        # Get credentials and create an API client
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        return youtube

    # Step Pre-2: Grab Playlist
    def get_playlist_id(self):
        # Retrieve playlist id with spotify title
        request = self.youtube_client.playlists().list(
            part="snippet, contentDetails",
            channelId=channel_id,
            maxResults=25
        )
        response = request.execute()

        for item in response["items"]:
            playlist_title = item["snippet"]["title"]
            if playlist_title.lower() == "spotify":
                playlist_id = item["id"]

        return playlist_id

    # Step 2: Grab videos
    def get_playlist_videos(self):
        request = self.youtube_client.playlistItems().list(
            part="snippet, contentDetails",
            playlistId=self.get_playlist_id()
        )
        response = request.execute()

        #youtube_dl.utils.std_headers['User-Agent'] = "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"
        youtube_dl.utils.std_headers['User-Agent'] = "Googlebot-Video/1.0"

        for item in response["items"]:
            video_title = item["snippet"]["title"]
            video_id = item["contentDetails"]["videoId"]
            youtube_url = "https://www.youtube.com/watch?v={}".format(video_id)

            video = youtube_dl.YoutubeDL({}).extract_info(video_id, download=False)

            song_name = video["track"]
            artist = video["artist"]

            if song_name is not None and artist is not None:
                self.all_song_info[video_title] = {
                    "youtube_url": youtube_url,
                    "song_name": song_name,
                    "artist": artist,
                    "spotify_uri": self.get_spotify_uri(song_name, artist)
                }

    # Step 3: Create a new Playlist
    def create_playlist(self):
        request_body = json.dumps({
            "name": "Youtube Playlist",
            "description": "Youtube Playlist Videos",
            "public": False
        })

        query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)
        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type":"application/json",
                "Authorization": "Bearer {}".format(spotify_token)
        })

        response_json = response.json()
        return response_json["id"]

    # Step 4: Search for the Song
    # (based on song name and artist)
    def get_spotify_uri(self, song_name, artist):
        query = "https://api.spotify.com/v1/search?q=track:{}+artist:{}&type=track".format(
            song_name,
            artist
        )

        response = requests.get(
            query,
            headers={
                "Content-Type":"application/json",
                "Authorization":"Bearer {}".format(spotify_token)
            }
        )

        response_json = response.json()
        songs = response_json["tracks"]["items"]

        if songs:
            uri = songs[0]["uri"]
            return uri

    # Step 5: Add this song into the new Spotify playlist
    def add_song_to_playlist(self):
        self.get_playlist_videos()

        uris = [info["spotify_uri"]
                for song, info in self.all_song_info.items()]

        # remove null values from list
        uris = [i for i in uris if i]

        playlist_id = self.create_playlist()

        request_data = json.dumps(uris)

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id)

        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )

        if response.status_code != 200 or response.status_code != 201:
            raise ResponseException(response.status_code)

        response_json = response.json()
        return response_json

if __name__ == '__main__':
    cp = CreatePlaylist()
    cp.add_song_to_playlist()