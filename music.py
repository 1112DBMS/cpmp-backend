from multiprocessing import Process, Manager
import math
from time import sleep

import yt as YT
import uploader
import sql
from sql import sql_client
from constant import WORKERS

def uuid(url):
    return str(uuid3(NAMESPACE_URL, url))

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
        
        if UserID is not None:
            client = sql_client()
            self.like = client.user_song_like(UserID, SongID)
            client.close()
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
            "like": self.Like
        }
        return data

def check_exist(ID):
    client = sql_client()
    result = client.song_exist(ID)
    client.close()
    return result

def get_song(ID):
    client = sql_client()
    result = client.get_song_by_ID(ID)
    client.close()
    return result

def set_download(ID, state):
    client = sql_client()
    client.update_song_download(ID, state)
    client.close()
    return 

def fetch_song(url = None, ID = None, UUID = None):
    if UUID is not None:
        pass
    else:
        UUID = YT.uuid(url=url, ID=ID)

    if not check_exist(UUID):
        YT.add_song(url=url, ID=ID, download=False)
        print("Add new song:", UUID)
    else:
        print("Song exists.")

    return get_song(UUID)

def gen_track(url = None, ID = None, UUID = None, UserID = None):
    Song = fetch_song(url=url, ID=ID, UUID=UUID)
    Track = track(Song["SongID"], Song=Song)
    return Track.to_dict()

def gen_track_list(urls = None, IDs = None, UUIDs = None, UserID = None):

    def worker(return_lst, idx, url = None, ID = None, UUID = None, UserID = None):
        return_lst[idx] = gen_track(url=url, ID=ID, UUID=UUID, UserID=UserID)
        return

    manager = Manager()
    arr_len = 0
    
    if urls is not None:
        arr_len = len(urls)
    elif IDs is not None:
        arr_len = len(IDs)
    elif UUIDs is not None:
        arr_len = len(UUIDs)
    
    if arr_len == 0:
        raise ValueError("Length of requested track list cannot be 0.")

    if urls is None:
        urls = [None]*arr_len
    if IDs is None:
        IDs = [None]*arr_len
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
            p[idx] = (Process(target=worker, args=(Tracklst, idx, urls[idx], IDs[idx], UUIDs[idx], UserID)))
            p[idx].start()
            idx_list.append(idx)

        for idx in idx_list:
            p[idx].join()
    return list(Tracklst)

def search(query, offset, size):
    d = None
    error = False
    result = YT.search(query, offset+size)
    if len(result) > offset:
        urls = [yt.watch_url for yt in result[offset:]]
        tracks = gen_track_list(urls = urls)
        d = {
            "list": tracks,
            "total": len(tracks)
        }
    else:
        d = "Not enough search results."
        error = True
    return (d, error)

def download(UUID):
    if not check_exist(UUID):
        return False
    Song = get_song(UUID)
    if Song["Platform"] == "youtube":
        if Song["Download"] == 0:
            set_download(UUID, 1)
            try:
                YT.download_song(Song["OrigURL"])
                set_download(UUID, 2)
            except:
                set_download(UUID, 0)
        elif Song["Download"] == 1:
            while Song["Download"] == 1:
                sleep(1)
                Song = get_song(UUID)
                print(f'Download state for {UUID} is {Song["Download"]}')

    return True
