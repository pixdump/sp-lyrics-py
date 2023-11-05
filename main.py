from requests import post, get
from dotenv import load_dotenv
from base64 import b64encode
import PySimpleGUI as sg
from os import getenv
from typing import Tuple
from time import sleep
from regex_helper import track_id_from_url, album_id_from_url, is_valid_type

load_dotenv()

CLIENT_ID = str(getenv("CLIENT_ID"))
CLIENT_SECRET = str(getenv("CLIENT_SECRET"))
LYRICS_API = str(getenv("LYRICS_API"))


def get_token() -> Tuple[bool, str]:
    auth_string = (CLIENT_ID + ":" + CLIENT_SECRET).encode("utf-8")
    auth_base64 = str(b64encode(auth_string), "utf-8")

    success = True
    auth_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type": "client_credentials"}
    result = post(auth_url, headers=headers, data=data)

    if result.status_code != 200:
        success, msg = False, "Something Went Wrong while getting access token"
        return success, msg

    token = result.json()['access_token']
    return success, token


def get_auth_header(token: str) -> dict:
    return {"authorization": "Bearer " + token}


def get_track_info(token: str, track_id: str) -> Tuple[bool, dict]:
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = get_auth_header(token)
    res = get(url, headers=headers)
    if res.status_code != 200:
        return False, {"error": "Something Went Wrong With Spotify API"}
    track_data = res.json()
    return True, track_data


def get_album_tracks(token: str, album_id: str):
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    headers = get_auth_header(token)
    res = get(url, headers=headers)
    if res.status_code != 200:
        return False, {"error": "Something Went Wrong With Spotify API"}
    album_data = res.json()
    return True, album_data


def get_tracks_list(data: dict):
    names, track_ids = [], []
    for item in data["items"]:
        names.append(item["name"])
        track_ids.append(item["id"])
    names = "\n".join(names)
    # print(names)
    return names, track_ids


def get_lyrics(track_id: str) -> Tuple[bool, str]:
    url = LYRICS_API + f"{track_id}&format=lrc"
    data = get(url)
    if data.status_code != 200:
        return False, "Something Went Wrong"
    lyrics_data = data.json()
    if lyrics_data['error']:
        return False, "Error"
    lyrics = convert_to_lrc(lyrics_data)
    return True, lyrics


def convert_to_lrc(lyrics_data: dict) -> str:
    lrc_lines = []
    if lyrics_data['syncType'].lower() == 'unsynced':
        for line in lyrics_data['lines']:
            lrc_lines.append(line['words'])
    else:
        for line in lyrics_data['lines']:
            lrc_lines.append(f"[{line['timeTag']}] {line['words']}")

    return '\n'.join(lrc_lines)


def write_to_file(lyrics: str, track_name: str) -> None:
    with open(f"{track_name}.lrc", 'w', encoding='utf-8') as lrc_file:
        lrc_file.write(lyrics)


def input_dialog_box() -> Tuple[str, str]:
    sg.theme("Black")
    layout = [[sg.Text('Enter Spotify URL'), sg.InputText()],
              [sg.Button('Ok'), sg.Button('Cancel')]]
    window = sg.Window('Lyrics', layout)

    event, values = window.read()  # type: ignore
    if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
        window.close()
        exit(0)
    url_type = is_valid_type(values[0])
    if url_type == "Invalid":
        sg.popup("Invalid Spotify URL. Please try again.")
        window.close()
        return input_dialog_box()
    else:
        window.close()
        return url_type, values[0]


def message_box(msg: str) -> None:
    window = sg.Window('Lyrics')
    sg.popup(msg)
    window.close()


def main() -> None:
    url_type, spotify_url = input_dialog_box()
    success, token = get_token()
    if not success:
        message_box(msg=token)
        exit(0)
    if url_type.lower() == "track":
        track_id = str(track_id_from_url(spotify_url))
        success, track_info = get_track_info(token, track_id)
        if success:
            print(f"Track Name: {track_info['name']}")
            print(f"Album: {track_info['album']['name']}")
            print(f"Artist: {track_info['artists'][0]['name']}")
            lyrics_available, lyrics = get_lyrics(track_id)
            if lyrics_available:
                write_to_file(lyrics, track_info['name'])
                message_box(msg=f"Successfully Fetched Lyrics for {track_info['name']}")
            else:
                message_box("Error Getting Lyrics")
    if url_type.lower() == "album":
        album_id = str(album_id_from_url(spotify_url))
        success, album_info = get_album_tracks(token, album_id)
        if success:
            track_names, track_ids = get_tracks_list(data=album_info)
            message_box(f"Found Album tracks: \n{track_names}")
            for track in track_ids:
                success, track_info = get_track_info(token, track)
                sleep(3)
                if success:
                    print(f"Track Name: {track_info['name']}")
                    print(f"Album: {track_info['album']['name']}")
                    print(f"Artist: {track_info['artists'][0]['name']}")
                    lyrics_available, lyrics = get_lyrics(track)
                    if lyrics_available:
                        write_to_file(lyrics, track_info['name'])
                        message_box(msg=f"Successfully Fetched Lyrics for {track_info['name']}")
                    else:
                        message_box("Error Getting Lyrics")
                else:
                    message_box("Error Getting Track Info")


main()
