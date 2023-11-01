import re


def track_id_from_url(spotify_url: str):
    pattern = r'/track/(\w+)'
    match = re.search(pattern, spotify_url)  # Use re.search to find the match

    if match:
        track_id = match.group(1)
        print("Track ID:", track_id)
        return track_id
    else:
        print("No match found.")
        return None


def album_id_from_url(spotify_url: str):
    """Use Regex to get Album Id from Spotify URL"""

    pattern = r'/album/(\w+)'
    match = re.search(pattern, spotify_url)  # Use re.search to find the match

    if match:
        album_id = match.group(1)
        print("Track ID:", album_id)
        return album_id
    else:
        print("No match found.")
        return None
