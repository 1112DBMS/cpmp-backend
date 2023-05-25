from pytube import YouTube as YT, Playlist, Search
import pytube
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import os
import shutil
from uuid import uuid3, NAMESPACE_URL
from tqdm import tqdm

import sql
from sql import sql_client
import uploader
from constant import SONG_FOLDER, SITE
import picture

'''
#####################################

        Below are Old Stuffs

#####################################

Songs_Path = "/Music"

def get_a_song(link):
    
    yt = YT(link, use_oauth=True, allow_oauth_cache=True)

    print("Title: ", yt.title)

    song_fn = "{Id}.{ext}".format(Id=yt.video_id, ext="webm")
    print(yt.watch_url)
    print(song_fn)
        
    if os.path.isfile("{dir}/{fn}".format(dir=Songs_Path, fn=song_fn)):
        print("File exist, skipping...")

    else:
        stream_datas = list(yt.streams.filter(only_audio=True))

        max_itag = ""
        max_kbps = -1
        max_type = ""
    
        for i in range(len(stream_datas)):
            parsed_html = BeautifulSoup(str(stream_datas[i]), "html.parser")
            print(parsed_html)
            kbps = int(parsed_html.find('stream:')["abr"][:-4])
            if kbps > max_kbps:
                max_kbps = kbps
                max_itag = parsed_html.find('stream:')["itag"]
                max_type = parsed_html.find('stream:')["mime_type"].split("/")[1]

        ys = yt.streams.get_by_itag(max_itag)
        ys.download(output_path = Songs_Path, filename = song_fn)

    return "{dir}/{fn}".format(dir=Songs_Path, fn=song_fn)

def parse_playlist(links):
    playlst = Playlist(links)
    return list(playlst.video_urls)

def parse_link(link):
    try:
        lst = parse_playlist(link)
        return lst
    except Exception as e:
        print(e)
        print("try single song")
        try:
            get_a_song(link)
            return link
        except Exception as e:
            print(e)
            print("Unknown link")
            return None

#####################################

        Above are Old Stuffs

#####################################
'''

def uuid(url = None, ID = None):
    ytObj = None
    
    if url is not None:
        ytObj = YT(url=url)
    elif ID is not None:
        ytObj = YT.from_id(ID)

    if ytObj is not None:
        return str(uuid3(NAMESPACE_URL, ytObj.watch_url))
    else:
        raise SyntaxError("No YT url nor ID is given to generate UUID!")

def download_song(url):
    ytObj = YT(url, use_oauth=True, allow_oauth_cache=True)
    song_fn = "{Id}.{ext}".format(Id=uuid(url=url), ext="webm")
        
    if os.path.isfile(f"{SONG_FOLDER}/{song_fn}"):
        print("File exist, skipping...")
        return
    else:
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
    print("len =", len(search.results))
    while len(search.results) < max_idx:
        try:
            search.get_next_results()
        except IndexError:
            return search.results[:max_idx]
    return search.results[:max_idx]

def add_song(url = None, ID = None, download = False):
    ytObj = None
    
    if url is not None:
        ytObj = YT(url=url)
    elif ID is not None:
        ytObj = YT.from_id(ID)

    if ytObj is not None:
        ytObj.use_oauth=True
        ytObj.allow_oauth_cache=True

        UUID = uuid(url=url, ID=ID)
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

        client = sql_client()
        client.add_new_song(UUID, url, Platform, Title, UploaderID, thumbnailID, likecount, Length, Download)
        client.close()
    else:
        raise SyntaxError("No YT url nor ID is given to add song!")
