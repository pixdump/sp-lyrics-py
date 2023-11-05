import re


def is_valid_type(url: str) -> dict:
    track_url_pattern = r'https://open\.spotify\.com/track/([a-zA-Z0-9]+)'
    album_url_pattern = r'https://open\.spotify\.com/album/([a-zA-Z0-9]+)'

    # Check if the URL matches the track pattern
    track_match = re.match(track_url_pattern, url)
    if track_match:
        return {"type": "track", "id": track_match.group(1)}

    # Check if the URL matches the album pattern
    album_match = re.match(album_url_pattern, url)
    if album_match:
        return {"type": "album", "id": album_match.group(1)}

    return {"type": None, "id": None}
