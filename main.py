from requests import post, get
from dotenv import load_dotenv
from base64 import b64encode
import os
import json
import re

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
LYRICS_API = os.getenv("LYRICS_API")


def track_id_from_url(spotify_url: str):
    """Use Regex to get Track Id from Spotify URL"""

    pattern = r'/track/(\w+)'
    match = re.search(pattern, spotify_url)  # Use re.search to find the match

    if match:
        track_id = match.group(1)
        print("Track ID:", track_id)
        return track_id
    else:
        print("No match found.")
        return None


def get_token():
    auth_string = (CLIENT_ID + ":" + CLIENT_SECRET).encode("utf-8")
    auth_base64 = str(b64encode(auth_string), "utf-8")

    auth_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type": "client_credentials"}
    result = post(auth_url, headers=headers, data=data)

    if result.status_code != 200:
        print("Something Went Wrong")
        return None

    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_auth_header(token: str):
    return {"authorization": "Bearer " + token}


def get_track_info(token: str, track_id: str):
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = get_auth_header(token)
    res = get(url, headers=headers)
    if res.status_code != 200:
        print("Something Went Wrong")
    track_data = json.loads(res.content)
    return track_data


def get_lyrics(track_id: str):
    url = LYRICS_API + f"{track_id}&format=lrc"
    data = get(url)
    if data.status_code != 200:
        print("Something went wrong")
        return None
    lyrics_data = json.loads(data.content)
    lyrics = convert_to_lrc(lyrics_data)
    return lyrics


def convert_to_lrc(lyrics_data: dict):
    lrc_lines = []
    if lyrics_data['syncType'] == 'UNSYNCED':
        for line in lyrics_data['lines']:
            lrc_lines.append(line['words'])
    else:
        for line in lyrics_data['lines']:
            lrc_lines.append(f"[{line['timeTag']}] {line['words']}")

    return '\n'.join(lrc_lines)


def write_to_file(lyrics: str, track_name: str):
    with open(f"{track_name}.lrc", 'w', encoding='utf-8') as lrc_file:
        lrc_file.write(lyrics)


token = get_token()
spo = str(input("Enter Spotify URl: "))
track_id = track_id_from_url(spo)
track_info = get_track_info(token, track_id)
print(f"Track Name: {track_info['name']}")
print(f"Album: {track_info['album']['name']}")
print(f"Artist: {track_info['artists'][0]['name']}")
lyrics = get_lyrics(track_id)
write_to_file(lyrics, track_info['name'])
