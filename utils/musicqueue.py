from uuid import uuid4
from datetime import datetime

import utils.music as music
from utils.sql import sql_client
'''
class MyQueue:

    def __init__(self, QID = None):
        if QID is not None:
            client = sql_client()
            result = client.get_queue_rows(QID)
            client.close()
'''
def check_exist(QID):
    client = sql_client()
    result = client.queue_exist(QID)
    client.close()
    return result

def get_queue_id_by_user(UID):
    client = sql_client()
    result = client.get_qid_by_uid(UID)
    client.close()
    return result

def get_queue_rows(QID):
    client = sql_client()
    result = client.get_queue_rows(QID)
    client.close()
    return result

def get_queue_len(QID):
    client = sql_client()
    result = client.get_queue_len(QID)
    client.close()
    return result

def add_queue(QID, Name):
    client = sql_client()
    client.add_new_queue(QID, Name, 'OFF', 0)
    client.close()
    return

def push_song(QID, SongID, idx = None):
    client = sql_client()
    qlen = get_queue_len(QID)
    Time = datetime.now()
    if idx is None:
        client.add_song_to_queue(QID, qlen, SongID, Time)
    else:
        client.update_queue_song_index_down(QID, idx, qlen)
        client.add_song_to_queue(QID, idx, SongID, Time)

    client.close()
    return

def delete_song(QID, idx):
    client = sql_client()
    qlen = get_queue_len(QID)

    client.delete_song_from_queue(QID, idx)
    client.update_queue_song_index_up(QID, idx+1, qlen)
    
    client.close()
    return

def bind_queue_to_user(QID, UID):
    client = sql_client()
    client.update_queue_owner(QID, UID)
    client.close()
    return

def bind_queue_to_guild(QID, GID):
    client = sql_client()
    client.update_queue_guild(QID, None, GID)
    client.close()
    return

def get_role(QID, UID):
    client = sql_client()
    result = client.get_user_role_in_queue(QID, UID)
    client.close()
    return result

def set_role(QID, UID, Role):
    client = sql_client()

    if get_role(QID, UID) is not None:
        client.update_user_role_in_queue(QID, UID, Role)
    else:
        client.add_user_role_in_queue(QID, UID, Role)

    client.close()
    return

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
    bind_queue_to_user(QID, UID)
    set_role(QID, UID, "Owner")
    return

def set_editor(QID, UID):
    set_role(QID, UID, "Editor")
    return

def set_viewer(QID, UID):
    set_role(QID, UID, "Viewer")
    return

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

