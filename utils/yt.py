from __future__ import annotations
from typing import List, Set, Dict, Tuple
from typing import Union, Optional, Any
from pytube import YouTube as YT, Playlist, Search
from bs4 import BeautifulSoup
import os
from uuid import uuid3, NAMESPACE_URL

import utils.sql as sql
import utils.uploader as uploader
from utils.constant import SONG_FOLDER, SITE
import utils.picture as picture

def uuid(url):
    ytObj = YT(url=url)
    return str(uuid3(NAMESPACE_URL, ytObj.watch_url))

def download_song(url):
    ytObj = YT(url, use_oauth=True, allow_oauth_cache=True)
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

def search(query, max_idx):
    search = Search(query)
    while len(search.results) < max_idx:
        try:
            search.get_next_results()
        except IndexError:
            return search.results[:max_idx]
    return search.results[:max_idx]

def add_song(url = None, download = False):
    ytObj = YT(url=url, use_oauth=True, allow_oauth_cache=True)

    UUID = uuid(url=ytObj.watch_url)
    url = ytObj.watch_url
    Platform = "youtube"
    Title = ytObj.title
    Length = ytObj.length

    UploaderID = uploader.fetch_uploader(url=ytObj.channel_url, platform="youtube")["UploaderID"]

    thumbnailID = picture.fetch_picture(url=ytObj.thumbnail_url)["PicID"]

    likecount = 0

    Download = 0
    if download:
        download_song(url)
        Download = 2

    success = sql.add_new_song(UUID, url, Platform, Title, UploaderID, thumbnailID, likecount, Length, Download)

    return
