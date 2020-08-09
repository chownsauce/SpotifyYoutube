# SpotifyYoutube
Create Spotify playlists from Youtube playlists.   
Retrieves the Youtube playlist titled "spotify" to create a Spotify playlist.

## Setup:
1) Install All Dependencies   
`pip3 install -r requirements.txt`

2) Retrieve Spotify ID and Oauth Token
   * To retrieve your Spotify ID, go here: [Account Overview]
   * To retrieve your Oauth Token, go here: [Get Oauth] and click the **Get Token** button
   * You will need too generate an Oauth Token ever so often as they can quickly expire 
   
3) Enable OAuth for Youtube and download the OAuth client_secret_###.json file
   * Instructions can be found here: [Youtube Data API]
   * When creating the OAuth client ID, choose **Desktop app** as the Application type

4) Run the application
`python3 create_playlist.py`   
   * Navigate to the URL when asked to authorize the application. 
   * Log in to your Youtube account that contains the playlist titled 'spotify'
   * Spotify will attempt to add all songs to the playlist, but there is no guarantee that all songs will be added

[Account Overview]: <https://www.spotify.com/us/account/overview/>
[Get Oauth]: <https://developer.spotify.com/console/post-playlists/>
[Youtube Data API]: <https://developers.google.com/youtube/v3/getting-started/>
