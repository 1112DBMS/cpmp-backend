from __future__ import annotations
from typing import List, Set, Dict, Tuple
from typing import Union, Optional, Any
from datetime import datetime

import utils.sql as sql
import utils.music as music

def get_playcount(SID):
    return sql.get_song_playcount(SID)

def s_record_and_redirect(UID, SID) -> Tuple[bool, str]:
    if not music.check_exist(SID):
        return (False, "Value song id invalid.")
    else:
        Time = datetime.now()
        success = sql.add_new_history(UID, SID, Time)
        if success == True:
            return (True, "Success")
        else:
            return (False, "sql add new history record failed.")

def s_get_topplay(UID, k, Self) -> Tuple[bool, str | Dict[str, Any]]:
    if k is None:
        k = 10
    if not isinstance(k, int) or (k > 10 or k <= 0):
        return (False, "Value topk invalid.")
    if Self not in [None, "1"]:
        return (False, "Value self invalid.")
    
    Self = True if Self == "1" else False
    
    SIDs = None
    counts = 0
    
    try:
        if Self == False:
            SIDs, counts = sql.get_all_topk(k)
        else:
            # No need to check user exist. userID is given via middleware.
            if UID is not None:
                SIDs, counts = sql.get_user_topk(UID, k)
            else:
                SIDs, counts = ([], [])

        tracks = music.gen_track_list(UUIDs=SIDs, UserID=UID)
    
        d = {
            "list": [{**x, "playCount":y}for x, y in zip(tracks, counts)],
            "total": len(tracks)
        }
        return (True, d)
    except Exception as e:
        print(e)
        return (False, str(e))
