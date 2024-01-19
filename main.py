from requests import post, get
from dotenv import load_dotenv
import PySimpleGUI as sg
import os
from typing import Tuple
from time import sleep
from regex_helper import is_valid_type

load_dotenv()

CLIENT_ID = str(os.getenv("CLIENT_ID"))
CLIENT_SECRET = str(os.getenv("CLIENT_SECRET"))
LYRICS_API = str(os.getenv("LYRICS_API"))


ERR_DEFAULT = {"error": "Something Went Wrong With Spotify API"}


class SpotifyHelper:
    def __init__(self) -> None:
        self.client_id: str = CLIENT_ID
        self.client_secret: str = CLIENT_SECRET
        self.access_token: str = ""
        self.helper = Helpers()
        self.gui = GUI_helpers()

    def __call__(self) -> None:
        if len(self.access_token) == 0:
            self.get_token()

    def get_token(self) -> None:
        auth_url = "https://accounts.spotify.com/api/token"
        data = {"grant_type": "client_credentials"}
        result = post(auth_url, data=data, auth=(
            self.client_id, self.client_secret))

        if result.status_code != 200:
            self.gui.message_box(
                msg="Something Went Wrong while getting access token")
            exit(0)
        self.access_token = result.json()['access_token']

    def get_auth_header(self) -> dict[str, str]:
        return {"authorization": "Bearer " + self.access_token}

    def process_track(self, track_id) -> None:
        success, track_info = self.get_track_info(track_id)
        if success:
            self.helper.print_track_info(track_info)
            self.helper.fetch_and_write_lyrics(track_id, track_info['name'])
        else:
            self.gui.message_box("Error Getting Track Info")

    def get_track_info(self, track_id: str) -> Tuple[bool, dict]:
        url = f"https://api.spotify.com/v1/tracks/{track_id}"
        res = get(url, headers=self.get_auth_header())
        if res.status_code != 200:
            print(res.text)
            return False, ERR_DEFAULT
        track_data = res.json()
        return True, track_data

    def get_album_tracks(self, album_id: str) -> Tuple[bool, dict]:
        url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
        res = get(url, headers=self.get_auth_header())
        if res.status_code != 200:
            return False, ERR_DEFAULT
        album_data = res.json()
        return True, album_data

    def process_album(self, album_id: str) -> None:
        success, album_info = self.get_album_tracks(album_id)
        if success:
            track_names, track_ids = self.helper.get_tracks_list(album_info)
            self.gui.message_box(f"Found Album tracks:\n{track_names}")
            for track_id in track_ids:
                sleep(3)
                self.process_track(track_id)
        else:
            self.gui.message_box("Error Getting Album Info")


class Helpers:
    def __init__(self) -> None:
        self.gui = GUI_helpers()

    def print_track_info(self, track_info: dict) -> None:
        print(f"Track Name: {track_info['name']}")
        print(f"Album: {track_info['album']['name']}")
        print(f"Artist: {track_info['artists'][0]['name']}\n")

    def get_tracks_list(self, data: dict) -> Tuple[str, list]:
        names, track_ids = [], []
        for item in data["items"]:
            names.append(item["name"])
            track_ids.append(item["id"])
        names = "\n".join(names)
        return names, track_ids

    def convert_to_lrc(self, lyrics_data: dict) -> str:
        lrc_lines = []
        for line in lyrics_data['lines']:
            if lyrics_data['syncType'].lower() == 'unsynced':
                lrc_lines.append(line['words'])
                continue
            lrc_lines.append(f"[{line['timeTag']}] {line['words']}")
        return '\n'.join(lrc_lines)

    def fetch_and_write_lyrics(self, track_id, track_name) -> None:
        lyrics_available, lyrics = self.get_lyrics(track_id)
        if lyrics_available:
            self.write_to_file(lyrics, track_name)
            self.gui.message_box(
                msg=f"Successfully Fetched Lyrics for {track_name}")
        else:
            self.gui.message_box("Error Getting Lyrics")

    def get_lyrics(self, track_id: str) -> Tuple[bool, str]:
        url = LYRICS_API + f"{track_id}&format=lrc"
        data = get(url)
        if data.status_code != 200:
            return False, "Something Went Wrong"
        lyrics_data = data.json()
        if lyrics_data['error']:
            return False, "Error"
        lyrics = self.convert_to_lrc(lyrics_data)
        return True, lyrics

    def write_to_file(self, lyrics: str, track_name: str) -> None:
        p = os.path.join(os.getcwd(), f"{track_name}.lrc")
        with open(p, 'w', encoding='utf-8') as lrc_file:
            lrc_file.write(lyrics)


class GUI_helpers:
    def __init__(self) -> None:
        pass

    def input_dialog_box(self) -> Tuple[str, str]:
        sg.theme("Black")
        while True:
            layout = [[sg.Text('Enter Spotify URL'), sg.InputText()],
                      [sg.Button('Ok'), sg.Button('Cancel')]]
            window = sg.Window('Lyrics', layout)

            event, values = window.read()  # type: ignore
            if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
                window.close()
                exit(0)

            url_info = is_valid_type(values[0])
            if url_info['type'] is not None:
                window.close()
                return url_info['type'].lower(), url_info['id']
            sg.popup("Invalid Spotify URL. Please try again.")
            window.close()
        # return self.input_dialog_box()

    def message_box(self, msg: str) -> None:
        window = sg.Window('Lyrics')
        sg.popup(msg)
        window.close()


def main() -> None:
    spotify = SpotifyHelper()
    gui = GUI_helpers()
    if len(CLIENT_ID) == 0 or len(CLIENT_SECRET) == 0 or len(LYRICS_API) == 0:
        gui.message_box("Important Details missing Please Check your .env")
        exit(1)
    url_type, id_from_url = gui.input_dialog_box()
    spotify()
    if url_type == "track":
        spotify.process_track(id_from_url)
    elif url_type == "album":
        spotify.process_album(id_from_url)


if __name__ == "__main__":
    main()
