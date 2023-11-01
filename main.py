from requests import post, get
from dotenv import load_dotenv
from base64 import b64encode
import os
import json
from regex_helper import track_id_from_url, album_id_from_url  # noqa

load_dotenv()

CLIENT_ID = str(os.getenv("CLIENT_ID"))
CLIENT_SECRET = str(os.getenv("CLIENT_SECRET"))
LYRICS_API = str(os.getenv("LYRICS_API"))


def get_token() -> str:

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
        raise SystemExit("Something Went Wrong while getting access token")
        # print("Something Went Wrong while getting access token")
        # exit(0)

    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_auth_header(token: str) -> dict:
    return {"authorization": "Bearer " + token}


def get_track_info(token: str, track_id: str) -> tuple[bool, dict]:
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = get_auth_header(token)
    res = get(url, headers=headers)
    if res.status_code != 200:
        return False, {"error": "Something Went Wrong With Spotify API"}
    track_data = json.loads(res.content)
    return True, track_data


def get_lyrics(track_id: str) -> tuple[bool, str]:
    url = LYRICS_API + f"{track_id}&format=lrc"
    data = get(url)
    if data.status_code != 200:
        return False, "Something Went Wrong"
    lyrics_data = json.loads(data.content)
    if lyrics_data['error']:
        return False, "Error"
    lyrics = convert_to_lrc(lyrics_data)
    return True, lyrics


def convert_to_lrc(lyrics_data: dict) -> str:
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
track_id = str(track_id_from_url(spo))
success, track_info = get_track_info(token, track_id)
if success:
    print(f"Track Name: {track_info['name']}")
    print(f"Album: {track_info['album']['name']}")
    print(f"Artist: {track_info['artists'][0]['name']}")
    lyrics_available, lyrics = get_lyrics(track_id)
    if lyrics_available:
        write_to_file(lyrics, track_info['name'])
