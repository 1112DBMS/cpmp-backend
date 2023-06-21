from __future__ import annotations
from typing import List, Set, Dict, Tuple
from typing import Union, Optional, Any
from multiprocessing import Process, Manager
import math
from time import sleep
import re

import utils.yt as YT
import utils.spotify as spot
import utils.uploader as uploader
import utils.history as history
import utils.sql as sql
from utils.constant import WORKERS, DOWNLOAD_LENGTH_LIMIT

class track:

    def __init__(self, SongID = None, UserID = None, Song = None):
        if Song is None:
            Song = get_song(SongID)

        Uploader = uploader.get_uploader(Song["Uploader"])

        self.Title = Song["Title"]
        self.URL = Song["OrigURL"]
        self.Platform = Song["Platform"]
        self.Thumbnail = Song["Thumbnail"]
        self.Uploader = Uploader["Name"]
        self.UploaderID = Uploader["UploaderID"]
        self.SongID = Song["SongID"]
        self.Download = True if Song["Download"] == 2 else False
        self.Like = None
        self.UserID = UserID
        self.Playcount = history.get_playcount(self.SongID)
        
        if UserID is not None:
            self.Like = sql.user_song_like(UserID, SongID)
        return
    
    def to_dict(self):
        data = {
            "title": self.Title,
            "url": self.URL,
            "platform": self.Platform,
            "thumbnail": self.Thumbnail,
            "uploader": self.Uploader,
            "uploaderId": self.UploaderID,
            "id": self.SongID,
            "download": self.Download,
            "like": self.Like,
            "playCount": self.Playcount
        }
        return data

def check_exist(ID):
    return sql.song_exist(ID)

def get_song(ID):
    return sql.get_song_by_ID(ID)

def set_download(ID, state):
    return sql.update_song_download(ID, state)

def is_yt(url) -> bool:

    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    
    youtube_regex_match = re.match(youtube_regex, url)

    if not youtube_regex_match:
        return False
    else:
        return True

def fetch_song(url = None, UUID = None):
    if UUID is not None:
        pass
    else:
        if is_yt(url):
            UUID = YT.uuid(url=url)
        else:
            UUID = spot.uuid(url=url)

    if check_exist(UUID):
        return get_song(UUID)

    if url is not None:
        Tries = 3
        while Tries > 0:
            try:
                if is_yt(url):
                    YT.add_song(url=url, download=False)
                else:
                    spot.add_song(url=url, download=False)
                break
            except ConnectionResetError:
                sleep(0.1)
                print(f"Retry pulling {url}")
                Tries -= 1
        if Tries == 0:
            raise ConnectionResetError(f"Out of tries when fetching {url}")
            
        print("Add new song:", UUID)
    else:
        raise ValueError("No url is given to generate song.")

    return get_song(UUID)

def gen_track(url = None, UUID = None, UserID = None):
    Song = fetch_song(url=url, UUID=UUID)
    Track = track(Song["SongID"], Song=Song, UserID=UserID)
    return Track.to_dict()

def gen_track_list(urls = None, UUIDs = None, UserID = None):

    def worker(return_lst, idx, url = None, UUID = None, UserID = None):
        return_lst[idx] = gen_track(url=url, UUID=UUID, UserID=UserID)
        return

    manager = Manager()
    arr_len = 0
    
    if urls is not None:
        arr_len = len(urls)
    elif UUIDs is not None:
        arr_len = len(UUIDs)
    '''
    if arr_len == 0:
        raise ValueError("Length of requested track list cannot be 0.")
    '''
    if urls is None:
        urls = [None]*arr_len
    if UUIDs is None:
        UUIDs = [None]*arr_len

    Tracklst = manager.list([None]*arr_len)
    p = [None]*arr_len
    
    for i in range(math.ceil(arr_len/WORKERS)):
        idx_list = []
        for j in range(WORKERS):
            idx = i*WORKERS+j
            if idx >= arr_len:
                break
            p[idx] = (Process(target=worker, args=(Tracklst, idx, urls[idx], UUIDs[idx], UserID)))
            p[idx].start()
            idx_list.append(idx)

        for idx in idx_list:
            p[idx].join()
    return list(Tracklst)

def search(query, offset, size, plat, UID):
    
    if offset > 60 or offset < 0:
        return (False, "Value offset invalid.")
    
    if size <= 0 or size > 30:
        return (False, "Value len invalid.")

    if query is None:
        return (False, "Value keyword invalid.")

    urls = []

    if plat == "youtube":
        
        result = YT.search(query, offset+size)
        
        if len(result) <= offset:
            return (False, "Not enough search results.")
        
        urls = [yt.watch_url for yt in result[offset:]]

    elif plat == "spotify":

        result = spot.search(query, offset, size)
        urls = [item["external_urls"]["spotify"] for item in result]

    tracks = gen_track_list(urls = urls, UserID=UID)

    d = {
        "list": tracks,
        "total": len(tracks)
    }

    return (True, d)

def s_get_track(url, SID, UID) -> Tuple[bool, str | Dict[str, Any]]:
    if SID is None and url is None:
        return (False, "400")
    try:
        info = gen_track(url = url, UUID = SID, UserID = UID)
        return (True, info)
    except Exception as e:
        print(e)
        return (False, "Value song id or url invalid.")
    
def s_download(SID) -> Tuple[bool, str]:
    if SID is None:
        return (False, "400")

    if not check_exist(SID):
        return (False, "Value song id invalid.")
    
    try:
        Song = get_song(SID)
        
        if Song["Length"] >= DOWNLOAD_LENGTH_LIMIT:
            return (False, "No permission.")
        
        if Song["Platform"] == "youtube":

            if Song["Download"] == 0:
                set_download(SID, 1)
                try:
                    YT.download_song(Song["OrigURL"])
                    set_download(SID, 2)
                except Exception as e:
                    set_download(SID, 0)
                    raise e
                
            elif Song["Download"] == 1:
                while Song["Download"] == 1:
                    sleep(1)
                    Song = get_song(SID)

            return (True, "Success")
        
        elif Song["Platform"] == "spotify":

            if Song["Download"] == 0:
                set_download(SID, 1)
                try:
                    spot.download_song(Song["OrigURL"])
                    set_download(SID, 2)
                except Exception as e:
                    set_download(SID, 0)
                    raise e
                
            elif Song["Download"] == 1:
                while Song["Download"] == 1:
                    sleep(1)
                    Song = get_song(SID)

            return (True, "Success")
        else:
            return (False, "Unknown Platform")
        
    except Exception as e:
        print(e)
        return (False, str(e))