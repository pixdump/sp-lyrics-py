import re
from typing import Tuple, Union  # noqa


def track_id_from_url(spotify_url: str) -> Union[str, None]:
    id_pattern = r'/track/(\w+)'
    match = re.search(id_pattern, spotify_url)

    if match:
        track_id = str(match.group(1))
        print("Track ID:", track_id)
        return track_id


def album_id_from_url(spotify_url: str):
    """Use Regex to get Album Id from Spotify URL"""

    id_pattern = r'/album/(\w+)'
    match = re.search(id_pattern, spotify_url)  # Use re.search to find the match

    if match:
        album_id = str(match.group(1))
        print("Track ID:", album_id)
        return album_id
    else:
        print("No match found.")
        return None


def is_valid_type(url: str) -> str:

    track_url_pattern = r'https://open\.spotify\.com/track/([a-zA-Z0-9]+)'
    album_url_pattern = r'https://open\.spotify\.com/album/([a-zA-Z0-9]+)'

    # Check if the URL matches the track pattern
    track_match = re.match(track_url_pattern, url)
    if track_match:
        return "Track"  # Extract the track ID

    # Check if the URL matches the album pattern
    album_match = re.match(album_url_pattern, url)
    if album_match:
        return "Album"  # Extract the album ID

    return "Invalid"
