from requests import post ,get
from dotenv import load_dotenv
from base64 import b64encode
import os
import json


load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


def getToken():
    authString = (client_id + ":" + client_secret).encode("utf-8")
    authBase64 = str(b64encode(authString), "utf-8")

    authURL = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + authBase64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type": "client_credentials"}
    result = post(authURL, headers=headers, data=data)

    if result.status_code != 200:
        print("Something Went Wrong")
        return None

    jsonResult = json.loads(result.content)
    token = jsonResult["access_token"]
    return token
