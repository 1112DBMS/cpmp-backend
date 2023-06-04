from datetime import datetime

import utils.sql as sql
import utils.music as music

def add_record(UID, SID):
    if not music.check_exist(SID):
        return False
    else:
        Time = datetime.now()
        success = sql.add_new_history(UID, SID, Time)
        return success

def get_playcount(SID):
    return sql.get_song_playcount(SID)

def top_tracks(k, UID=None):
    # No need to check user exist. userID is given via middleware.
    SIDs = None
    counts = 0

    if UID is None:
        SIDs, counts = sql.get_all_topk(k)
    else:
        SIDs, counts = sql.get_user_topk(UID, k)

    tracks = music.gen_track_list(UUIDs=SIDs)
    
    d = {
        "list": [{**x, "playCount":y}for x, y in zip(tracks, counts)],
        "total": len(tracks)
    }
    return d
