from __future__ import annotations
from typing import List, Set, Dict, Tuple
from typing import Union, Optional, Any
from uuid import uuid4
from datetime import datetime
from random import shuffle

import utils.music as music
import utils.sql as sql

def check_exist(QID) -> bool:
    return sql.queue_exist(QID)

def get_queue_id_by_user(UID) -> str:
    return sql.get_qid_by_uid(UID)

def get_queue_row(QID, IDX) -> Tuple[str, "datetime"]:
    return sql.get_queue_row(QID, IDX)

def get_queue_rows(QID) -> Tuple[List[str], List["datetime"]]:
    return sql.get_queue_rows(QID)

def get_queue_len(QID) -> int:
    return sql.get_queue_len(QID)

def add_queue(QID, Name) -> bool:
    return sql.add_new_queue(QID, Name, 0, 0)

def get_queue(QID) -> Dict[str, Any]:
    return sql.get_queue_info(QID)

def push_song(QID, SongID, idx) -> bool:
    qlen = get_queue_len(QID)
    Time = datetime.now()

    return sql.add_song_to_queue(QID, idx, qlen, SongID, Time)

def delete_song(QID, idx) -> bool:
    qlen = get_queue_len(QID)
    return sql.delete_song_from_queue(QID, idx, qlen)

def loop_queue(QID) -> bool:
    SID, _ = get_queue_row(QID, 0)
    qlen = get_queue_len(QID)
    Time = datetime.now()

    return sql.rotate_queue_loop_all(QID, SID, qlen, Time)

def loop_one(QID) -> bool:
    Time = datetime.now()
    return sql.rotate_queue_loop_one(QID, Time)

def bind_queue_to_user(QID, UID) -> bool:
    return sql.update_queue_owner(QID, UID)

def bind_queue_to_guild(QID, GID) -> bool:
    return sql.update_queue_guild(QID, GID)

def get_role(QID, UID) -> str:
    return sql.get_user_role_in_queue(QID, UID)

def set_role(QID, UID, Role) -> bool:
    result = None
    
    if get_role(QID, UID) is not None:
        result = sql.update_user_role_in_queue(QID, UID, Role)
    else:
        result = sql.add_user_role_in_queue(QID, UID, Role)

    return result

def line_match(QID, SID, IDX) -> bool:
    return sql.queue_line_exist(QID, SID, IDX)

def set_indexes(QID, IDXs) -> bool:
    return sql.update_queue_idxs(QID, IDXs)

def uuid() -> str:
    return str(uuid4())

##############################



##############################

def gen_queue_for_user(UID) -> str:
    QID = uuid()
    add_queue(QID, "New Queue")
    set_owner(QID, UID)
    return QID

def set_owner(QID, UID) -> bool:
    res1 = bind_queue_to_user(QID, UID)
    res2 = set_role(QID, UID, "Owner")
    return (res1 and res2)

def set_editor(QID, UID) -> bool:
    return set_role(QID, UID, "Editor")

def set_viewer(QID, UID) -> bool:
    return set_role(QID, UID, "Viewer")

def fetch_queue_ID(UID) -> str:
    QID = get_queue_id_by_user(UID)

    if QID is None:
        QID = gen_queue_for_user(UID)
    return QID

def can_edit(QID, UID) -> bool:
    permission = ["Owner", "Editor"]
    if get_role(QID, UID) in permission:
        return True
    else:
        return False

def can_view(QID, UID) -> bool:
    permission = ["Owner", "Editor", "Viewer"]
    if get_role(QID, UID) in permission:
        return True
    else:
        return False

##############################



##############################

def s_get_queue(QID, UID) -> Tuple[bool, str | List[Dict[str, Any]]]:
    if UID is None:
        return (False, "Not login.")
    if QID is None:
        QID = fetch_queue_ID(UID)
    if not check_exist(QID):
        return (False, "Value queue id invalid.")
    if not can_view(QID, UID):
        return (False, "No permission.")
    
    queue_rows, time_rows = get_queue_rows(QID)

    try:
        tracks = music.gen_track_list(UUIDs = queue_rows, UserID=UID)
        data = {
            "list": [{**x, "time":y.isoformat()}for x, y in zip(tracks, time_rows)],
            "total": len(tracks),
            "loop": get_queue(QID)["Loop"]
        }
        return (True, data)
    except Exception as e:
        print(e)
        return (False, str(e))

def s_post_queue(QID, SID, IDX, UID) -> Tuple[bool, str]:
    if UID is None:
        return (False, "Not login.")
    if SID is None or not music.check_exist(SID):
        return (False, "Value song id invalid.")
    if QID is None:
        QID = fetch_queue_ID(UID)
    if not check_exist(QID):
        return (False, "Value queue id invalid.")
    if not can_edit(QID, UID):
        return (False, "No permission.")
    
    qlen = get_queue_len(QID)
    if IDX is None:
        IDX = qlen
    
    if not isinstance(IDX, int) or IDX < 0 or IDX > qlen:
        return (False, "Value song idx invalid.")

    success = push_song(QID, SID, IDX)

    if success:
        return (True, "Success")
    else:
        return (False, "Unknown error")

def s_delete_queue(QID, SID, SIDX, UID) -> Tuple[bool, str]:
    if UID is None:
        return (False, "Not login.")
    if QID is None:
        QID = fetch_queue_ID(UID)
    if not check_exist(QID):
        return (False, "Value queue id invalid.")
    if SID is None:
        return (False, "Value song id invalid.")
    if SIDX is None:
        return (False, "Value song idx invalid.")
    if not can_edit(QID, UID):
        return (False, "No permission.")
    if not line_match(QID, SID, SIDX):
        return (False, "Idx not matched.")
    
    success = delete_song(QID, SIDX)

    if success:
        return (True, "Success")
    else:
        return (False, "Unknown error")

def s_set_loop(QID, UID, Loop) -> Tuple[bool, str]:
    if UID is None:
        return (False, "Not login.")
    if QID is None:
        QID = fetch_queue_ID(UID)
    if not check_exist(QID):
        return (False, "Value queue id invalid.")
    if Loop not in [0, 1, 2]:
        return (False, "Value loop invalid.")
    if not can_edit(QID, UID):
        return (False, "No permission.")
    
    success = sql.update_queue_loop(QID, Loop)

    if success == True:
        return (True, "Success")
    else:
        return (False, "Unknown error")

def s_queue_next(QID, UID) -> Tuple[bool, str]:
    if UID is None:
        return (False, "Not login.")
    if QID is None:
        QID = fetch_queue_ID(UID)
    if not check_exist(QID):
        return (False, "Value queue id invalid.")
    if not can_edit(QID, UID):
        return (False, "No permission.")
    try:
        Queue = get_queue(QID)
        success = False
        if Queue["Loop"] == 0:
            success = delete_song(QID, 0)
        elif Queue["Loop"] == 1:
            success = loop_queue(QID)
        elif Queue["Loop"] == 2:
            success = loop_one(QID)
            
        if success:
            return (True, "Success")
        else:
            raise RuntimeError("Error when rotating song.")
    except Exception as e:
        return (False, str(e))

def s_queue_shuffle(QID, UID) -> Tuple[bool, str]:
    if UID is None:
        return (False, "Not login.")
    if QID is None:
        QID = fetch_queue_ID(UID)
    if not check_exist(QID):
        return (False, "Value queue id invalid.")
    if not can_edit(QID, UID):
        return (False, "No permission.")
    
    Qlen = get_queue_len(QID)

    if Qlen <= 2:
        return (True, "Success")
    
    idx_lst = list(range(1, Qlen))
    shuffle(idx_lst)
    idx_lst.insert(0, 0)

    stat = set_indexes(QID, idx_lst)

    if stat:
        return (True, "Success")
    else:
        return (False, "Shuffle error occurs")