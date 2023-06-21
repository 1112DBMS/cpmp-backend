from __future__ import annotations
from typing import List, Set, Dict, Tuple
from typing import Union, Optional, Any

from uuid import uuid3, NAMESPACE_URL
from datetime import datetime, timedelta
from pytube import YouTube as YT
from bs4 import BeautifulSoup
import requests
import os

import utils.picture as picture
import utils.uploader as uploader
import utils.sql as sql
from utils.constant import SPOTIFY_API_ENDPOINT, SPOTIFY_TOKEN_URL, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_DOWN_ENDPOINT
from utils.constant import SONG_FOLDER

SPOT_TOK = None
TOK_TIME = datetime.min

def uuid(url):
    return str(uuid3(NAMESPACE_URL, url))

def get_token():
    global TOK_TIME, SPOT_TOK

    if datetime.now() > TOK_TIME:
    
        data = {
            'client_id': SPOTIFY_CLIENT_ID,
            'client_secret': SPOTIFY_CLIENT_SECRET,
            'grant_type': 'client_credentials'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    
        r = requests.post(SPOTIFY_TOKEN_URL, data=data, headers=headers)
    
        SPOT_TOK = r.json().get('access_token')
        TOK_TIME = datetime.now() + timedelta(seconds=3599)
    
    return SPOT_TOK

def fetch_track_info(url):
    
    acc_tok = get_token()
    id = url.split('/')[-1]

    headers = {
        'Authorization': f'Bearer {acc_tok}'
    }

    r = requests.get(SPOTIFY_API_ENDPOINT + f"/tracks/{id}", headers=headers)

    return r.json()

def fetch_artist_info(url):
    
    acc_tok = get_token()
    id = url.split('/')[-1]

    headers = {
        'Authorization': f'Bearer {acc_tok}'
    }

    r = requests.get(SPOTIFY_API_ENDPOINT + f"/artists/{id}", headers=headers)

    return r.json()

def download_song(url):
    
    id = url.split("/")[-1]
    UUID = uuid(url)

    headers = {
        "authority": "api.spotifydown.com",
        "origin": "api.spotifydown.com",
        "referer": "api.spotifydown.com"
    }
    
    r = requests.get(f"{SPOTIFY_DOWN_ENDPOINT}/getID/{id}", headers=headers)

    ytid = r.json()["id"]
    yturl = f"https://youtube.com/watch?v={ytid}"

    ytObj = YT(yturl, use_oauth=True, allow_oauth_cache=True)
    song_fn = "{Id}".format(Id=uuid(url=url))
        
    if os.path.isfile(f"{SONG_FOLDER}/{song_fn}"):
        return
    
    stream_datas = list(ytObj.streams.filter(only_audio=True))

    max_itag = ""
    max_kbps = -1
    max_type = ""

    for i in range(len(stream_datas)):
        parsed_html = BeautifulSoup(str(stream_datas[i]), "html.parser")
        kbps = int(parsed_html.find('stream:')["abr"][:-4])
        if kbps > max_kbps:
            max_kbps = kbps
            max_itag = parsed_html.find('stream:')["itag"]
            #max_type = parsed_html.find('stream:')["mime_type"].split("/")[1]

    ys = ytObj.streams.get_by_itag(max_itag)
    ys.download(output_path = SONG_FOLDER, filename = song_fn)
    
    return

def search(query, offset, size):

    acc_tok = get_token()

    headers = {
        'Authorization': f'Bearer {acc_tok}'
    }
    params = {
        'q': query,
        'type': "track",
        'limit': size,
        'offset': offset
    }
    
    r = requests.get(f"{SPOTIFY_API_ENDPOINT}/search", params=params, headers=headers)
    j = r.json()

    return j["tracks"]["items"]

def add_song(url = None, download = False):

    spotObj = fetch_track_info(url)
    UUID = uuid(url)
    Platform = "spotify"
    Title = spotObj["name"]
    Length = spotObj["duration_ms"]//1000


    UploaderID = uploader.fetch_uploader(url=spotObj["artists"][0]["external_urls"]["spotify"], platform="spotify")["UploaderID"]

    thumbnailID = picture.fetch_picture(url=spotObj["album"]["images"][0]["url"])["PicID"]

    likecount = 0

    Download = 0
    if download:
        download_song(url)
        Download = 2

    success = sql.add_new_song(UUID, url, Platform, Title, UploaderID, thumbnailID, likecount, Length, Download)

    return