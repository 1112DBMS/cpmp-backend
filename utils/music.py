from multiprocessing import Process, Manager
import math
from time import sleep

import utils.yt as YT
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
            self.like = sql.user_song_like(UserID, SongID)
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

def fetch_song(url = None, UUID = None):
    if UUID is not None:
        pass
    else:
        UUID = YT.uuid(url=url)

    if not check_exist(UUID):
        if url is not None:
            Tries = 3
            while Tries > 0:
                try:
                    YT.add_song(url=url, download=False)
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
    else:
        print("Song exists.")

    return get_song(UUID)

def gen_track(url = None, UUID = None, UserID = None):
    Song = fetch_song(url=url, UUID=UUID)
    Track = track(Song["SongID"], Song=Song)
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
    
    if Song["Length"] >= DOWNLOAD_LENGTH_LIMIT:
        return False

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
