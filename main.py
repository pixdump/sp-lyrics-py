from requests import post, get
from dotenv import load_dotenv
from base64 import b64encode
import os
import json
import re

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
lyrics_api = os.getenv("LYRICS_API")


def get_id_from_url(spotify_url: str):
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
    auth_string = (client_id + ":" + client_secret).encode("utf-8")
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
    url = lyrics_api + f"{track_id}&format=lrc"
    lyrics_data = get(url)
    if lyrics_data.status_code != 200:
        print("Something went wrong")
        return None
    lyrics_data_json = json.loads(lyrics_data.content)
    lyrics = convert_to_lrc(lyrics_data_json)
    print(lyrics)


def convert_to_lrc(lyric_json):
    lrc_lines = []
    for line in lyric_json['lines']:
        lrc_lines.append(f"[{line['timeTag']}] {line['words']}")

    return '\n'.join(lrc_lines)


token = get_token()
spo = str(input("Enter Spotify URl: "))
track_id = get_id_from_url(spo)
track_info = get_track_info(token, track_id)
print(f"Track Name: {track_info['name']}")
print(f"Album: {track_info['album']['name']}")
print(f"Artist: {track_info['artists'][0]['name']}")
get_lyrics(track_id)
