from __future__ import annotations
from typing import List, Set, Dict, Tuple
from typing import Union, Optional, Any
from uuid import uuid4
from datetime import datetime

import utils.music as music
import utils.sql as sql

def check_exist(QID) -> bool:
    return sql.queue_exist(QID)

def get_queue_id_by_user(UID) -> str:
    return sql.get_qid_by_uid(UID)

def get_queue_rows(QID) -> Tuple[List[str], List["datetime"]]:
    return sql.get_queue_rows(QID)

def get_queue_len(QID) -> int:
    return sql.get_queue_len(QID)

def add_queue(QID, Name) -> bool:
    return sql.add_new_queue(QID, Name, 0, 0)

def get_queue(QID) -> Dict[str, Any]:
    return sql.get_queue_info(QID)

def push_song(QID, SongID, idx = None) -> bool:
    qlen = get_queue_len(QID)
    if idx is None:
        idx = qlen
    Time = datetime.now()

    return sql.add_song_to_queue(QID, idx, qlen, SongID, Time)

def delete_song(QID, idx) -> bool:
    qlen = get_queue_len(QID)
    return sql.delete_song_from_queue(QID, idx, qlen)

def bind_queue_to_user(QID, UID) -> bool:
    return sql.update_queue_owner(QID, UID)

def bind_queue_to_guild(QID, GID) -> bool:
    return sql.update_queue_guild(QID, GID)

def get_role(QID, UID) -> str:
    return sql.get_user_role_in_queue(QID, UID)

def set_role(QID, UID, Role):
    result = None
    
    if get_role(QID, UID) is not None:
        result = sql.update_user_role_in_queue(QID, UID, Role)
    else:
        result = sql.add_user_role_in_queue(QID, UID, Role)

    return result

def line_match(QID, SID, IDX) -> bool:
    return sql.queue_line_exist(QID, SID, IDX)

def uuid() -> str:
    return str(uuid4())

##############################



##############################

def gen_queue_for_user(UID):
    QID = uuid()
    add_queue(QID, "New Queue")
    set_owner(QID, UID)
    return QID

def set_owner(QID, UID):
    res1 = bind_queue_to_user(QID, UID)
    res2 = set_role(QID, UID, "Owner")
    return (res1 and res2)

def set_editor(QID, UID):
    return set_role(QID, UID, "Editor")

def set_viewer(QID, UID):
    return set_role(QID, UID, "Viewer")

def fetch_queue_ID(UID) -> str:
    QID = get_queue_id_by_user(UID)

    if QID is None:
        QID = gen_queue_for_user(UID)
    return QID

def can_edit(QID, UID):
    permission = ["Owner", "Editor"]
    if get_role(QID, UID) in permission:
        return True
    else:
        return False

def get_queue_tracks(QID):
    queue_rows, time_rows = get_queue_rows(QID)
    tracks = music.gen_track_list(UUIDs = queue_rows)

    return [{**x, "time":y.isoformat()}for x, y in zip(tracks, time_rows)]

def remove_track(QID, SID, SIDX, UID) -> Tuple[bool, str]:
    if UID is None:
        return (False, "Not login.")
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
    else:
        if delete_song(QID, SIDX):
            return (True, "Success")
        else:
            return (False, "Unknown error")

def set_loop(UID, QID, Loop) -> Tuple[bool, str]:
    if UID is None:
        return (False, "Not login.")
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
    
if __name__ == "__main__":
    QID = fetch_queue_ID("715835031439933470")
    print(QID)
    #print(can_edit(QID, "391837295612919818"))
    #set_editor(QID, "391837295612919818")
    #print(can_edit(QID, "391837295612919818"))
    #set_viewer(QID, "391837295612919818")
    #print(can_edit(QID, "391837295612919818"))
    #push_song(QID, "09fcc836-d84e-3ef9-a935-e156b17a98ad")
    #push_song(QID, "041f0b82-f54f-342a-ad72-9984ebd41d68", 1)
    delete_song(QID, 2)
    #print(get_queue_tracks("d43750bd-d30d-4e90-bffe-adedd03a70a2"))

