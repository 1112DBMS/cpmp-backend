from pytube import YouTube as YT, Playlist, Search
import pytube
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import os
import shutil
import uuid
import sql
import uploader
from constant import SONG_FOLDER, SITE, WORKERS
from multiprocessing import Process, Manager
from tqdm import tqdm
import math

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

def get_UUID(url = None, ID = None):
    ytObj = None
    
    if url is not None:
        ytObj = YT(url=url)
    elif ID is not None:
        ytObj = YT.from_id(ID)

    if ytObj is not None:
        return str(uuid.uuid3(uuid.NAMESPACE_URL, ytObj.watch_url))
    else:
        raise SyntaxError("No YT url nor ID is given to generate UUID!")

def download_song(url):
    ytObj = YT(url, use_oauth=True, allow_oauth_cache=True)
    song_fn = "{Id}.{ext}".format(Id=get_UUID(url=url), ext="webm")
        
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
            print(parsed_html)
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
        search.get_next_results()
        print("len =", len(search.results))
    return search.results[:max_idx]


def fetch_info(url = None, ID = None, UUID = None):
    if UUID is not None:
        pass
    else:
        UUID = get_UUID(url=url, ID=ID)
    Song = sql.get_song_by_ID(UUID)
    if not Song:
        save_info(url=url, ID=ID, download=False)
        Song = sql.get_song_by_ID(UUID)
    if len(Song) > 1:
        raise ValueError(f"Duplicated song record with same UUID = {UUID}!")
    if len(Song) < 1:
        raise ValueError(f"Song record missing with UUID = {UUID}!")
    return Song[0]

def save_info(url = None, ID = None, download = False):
    ytObj = None
    
    if url is not None:
        ytObj = YT(url=url)
    elif ID is not None:
        ytObj = YT.from_id(ID)

    if ytObj is not None:
        ytObj.use_oauth=True
        ytObj.allow_oauth_cache=True

        UUID = get_UUID(url=url, ID=ID)
        url = ytObj.watch_url
        Platform = "youtube"
        Title = ytObj.title
        Length = ytObj.length

        UploaderID = uploader.fetch_uploader(url=ytObj.channel_url, platform="youtube")["UploaderID"]
        thumbnailID = "Lorem ipsum" #TODO IMPORTANT
        likecount = 0
        sql.add_new_song(UUID, url, Platform, Title, Length, UploaderID, thumbnailID, likecount)
        if download:
            download_song(url)
    else:
        raise SyntaxError("No YT url nor ID is given to save info!")


def gen_track(url = None, ID = None, UUID = None, UserID = None):
    Song = fetch_info(url=url, ID=ID, UUID=UUID)
    Track = {
        "title": Song["Title"],
        "url": Song["OrigURL"],
        "platform": Song["Platform"],
        "thumbnail": Song["thumbnail"],
        "uploader": uploader.get_uploader(Song["Uploader"])["Name"],
        "id": Song["SongID"],
        "like": None
    }
    if UserID is not None:
        Track["like"] = sql.user_like_song_query(UserID, UUID)
    return Track

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

if __name__ == '__main__':
    link = input("keyword: ")
    #print(parse_link(link))
    links = [yt.watch_url for yt in search(link, 25)]
    print(gen_track_list(urls=links))
