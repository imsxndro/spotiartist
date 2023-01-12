import spotipy
import spotipy.util
import requests
import sys

# Your Spotify username and API keys
username = "your username"
client_id = "your client id"
client_secret = "your client secret id"

# Request authorization from the API
scope = "playlist-modify-public"
redirect_uri = "http://localhost:8888/callback"

# Get an access token for the API
token = spotipy.util.prompt_for_user_token(
    username=username,
    scope=scope,
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri
)

# Create an instance of the API
sp = spotipy.Spotify(auth=token)

# Ask the user for the artist name
artist_name = input("Enter the artist name: ")

# Ask the user for the playlist name
playlist_name = input("Enter the playlist name: ")

try:
    # Search for the artist with the given name
    result = sp.search(q='artist:' + artist_name, type='artist')
    artist = result['artists']['items'][0]
    artist_id = artist['id']
    artist_name = artist['name']

    # Get the artist's singles
    tracks = []
    albums = sp.artist_albums(artist_id, album_type='single', limit='50')
    for album in albums['items']:
        # Get the tracks from each single
        album_tracks = sp.album_tracks(album['id'])
        if album['album_type'] != 'compilation':
            for track in album_tracks['items']:
                tracks.append(track['id'])

    # Get the artist's albums
    albums = sp.artist_albums(artist_id, album_type='album', limit='50')
    for album in albums['items']:
        # Get the tracks from each album
        album_tracks = sp.album_tracks(album['id'])
        if album['album_type'] != 'compilation':
            for track in album_tracks['items']:
                tracks.append(track['id'])

    # Get the songs where the artist is featured
    albums = sp.artist_albums(artist_id, album_type='appears_on')
    while albums:
        for album in albums['items']:
            # Get all the tracks from each song where the artist is featured
            album_tracks = sp.album_tracks(album['id'])
            if album['album_type'] != 'compilation':
                for track in album_tracks['items']:
                # Check if the chosen artist is present in the list of artists of the track
                    if artist_name in [artist['name'] for artist in track['artists']]:
                        tracks.append(track['id'])
        # Get the next page
        albums = sp.next(albums)

            # Create a list to store unique tracks
    unique_tracks = []

    # Iterate through the track list and check for duplicates
    for track in tracks:
        # Get the track details
        track_details = sp.track(track)

        # Check if the track already exists in the unique track list
        duplicate = False
        for unique_track in unique_tracks:
            if track_details['name'] == unique_track['name']:
                # If the track is a duplicate, check if the explicit version exists
                if track_details['explicit']:
                    # If it does, remove the non-explicit version and add the explicit version
                    unique_tracks.remove(unique_track)
                    unique_tracks.append(track_details)
                    duplicate = True
                else:
                    # If the explicit version does not exist, keep the existing version
                    duplicate = True

        if not duplicate:
            # If the track is not a duplicate, add it to the unique track list
            unique_tracks.append(track_details)

    # Create a new playlist and add the unique tracks
    playlist = sp.user_playlist_create(username, playlist_name)
    playlist_id = playlist["id"]
    track_ids = [track['id'] for track in unique_tracks]

    # Add the tracks in batches of 100
    for i in range(0, len(track_ids), 100):
        sp.user_playlist_add_tracks(username, playlist_id, track_ids[i:i+100])

    # Get the URL of the playlist
    url = sp.playlist(playlist_id)['external_urls']['spotify']

    print(f"The playlist '{playlist_name}' has been created and the tracks have been added.")
    print(f"The URL of the playlist is: {url}")

except:
    print("Error occured, please check your inputs and try again.")
