from uuid import uuid4
from datetime import datetime

import utils.music as music
import utils.sql as sql

def check_exist(QID):
    return sql.queue_exist(QID)

def get_queue_id_by_user(UID):
    return sql.get_qid_by_uid(UID)

def get_queue_rows(QID):
    return sql.get_queue_rows(QID)

def get_queue_len(QID):
    return sql.get_queue_len(QID)

def add_queue(QID, Name):
    return sql.add_new_queue(QID, Name, 0, 0)

def get_queue(QID):
    return sql.get_queue_info(QID)

def push_song(QID, SongID, idx = None):
    qlen = get_queue_len(QID)
    Time = datetime.now()

    if idx is None:
        return sql.add_song_to_queue(QID, qlen, SongID, Time)
    else:
        res1 = sql.update_queue_song_index_down(QID, idx, qlen)
        res2 = sql.add_song_to_queue(QID, idx, SongID, Time)
        return (res1 and res2)

def delete_song(QID, idx):
    qlen = get_queue_len(QID)

    res1 = sql.delete_song_from_queue(QID, idx)
    res2 = sql.update_queue_song_index_up(QID, idx+1, qlen)

    return (res1 and res2)

def bind_queue_to_user(QID, UID):
    return sql.update_queue_owner(QID, UID)

def bind_queue_to_guild(QID, GID):
    return sql.update_queue_guild(QID, GID)

def get_role(QID, UID):
    return sql.get_user_role_in_queue(QID, UID)

def set_role(QID, UID, Role):
    result = None
    
    if get_role(QID, UID) is not None:
        result = sql.update_user_role_in_queue(QID, UID, Role)
    else:
        result = sql.add_user_role_in_queue(QID, UID, Role)

    return result

def line_match(QID, SID, IDX):
    return sql.queue_line_exist(QID, SID, IDX)

def uuid():
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

def fetch_queue_ID(UID):
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

def remove_track(QID, SID, SIDX, UID):
    if not check_exist(QID):
        return (False, "Invalid QID")
    if not can_edit(QID, UID):
        return (False, "Forbidden")
    if not line_match(QID, SID, SIDX):
        return (False, "ID IDX not match")
    else:
        delete_song(QID, SIDX)
        return (True, "Success")
    return (False, "Unknown error")

def set_loop(UID, QID, Loop):
    if UID is None:
        return (False, "Not login.")
    if not check_exist(QID):
        return (False, "Invalid queue id.")
    if Loop is None:
        return (False, "Loop value not given.")
    if not can_edit(QID, UID):
        return (False, "No permission.")
    
    success = sql.update_queue_loop(QID, Loop)

    if success == True:
        return (True, "Success")
    else:
        return (False, "500")
    
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

