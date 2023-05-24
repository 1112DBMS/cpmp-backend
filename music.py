import yt as YT

def search(query, offset, size):
    urls = [yt.watch_url for yt in YT.search(query, offset+size)[offset:]]
    tracks = YT.gen_track_list(urls = urls)
    d = {
        "data": {
            "list": tracks,
            "total": len(tracks)
        },
        "error": False
    }
    return d
