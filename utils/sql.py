from __future__ import annotations
from typing import List, Set, Dict, Tuple
from typing import Union, Optional, Any

import mysql.connector
from loguru import logger
from datetime import datetime

from utils.constant import SQL_USER, SQL_PASSWORD, SQL_HOST, SQL_PORT, SQL_DB

now = datetime.now()
date = now.strftime("%Y-%m-%d")
logfile = logger.add(f'./log/{date}.log')

class sql_client:

    def __init__(self, user=SQL_USER, password=SQL_PASSWORD, host=SQL_HOST, port=SQL_PORT, database=SQL_DB):
        self._conn = mysql.connector.connect(
            host = host,
            port=port,
            user = user,
            password = password,
            database = database,
        )
        self._cursor = self._conn.cursor()

    def close(self):
        self._cursor.close()
        self._conn.close()
        return

    def execute(self, cmd: str, var: Tuple[Any, ...], write: bool) -> List[Tuple[Any, ...]] | bool:
        error: bool = False
        try:
            self._cursor.execute(cmd, var)

            if write == True:
                self._conn.commit()
            else:
                result = self._cursor.fetchall()
    
        except Exception as e:
            error = True
            self._conn.rollback()
            logger.error(e)

        if write == True:
            return not error
        else:
            return result
    
    def execute_multi(self, cmds:List[str], vars: List[Tuple[Any, ...]], write: bool) -> List[List[Tuple[Any, ...]]] | bool:
        error: bool = False
        results: List[Tuple[Any, ...]] = []
        try:
            for cmd, var in zip(cmds, vars):
                self._cursor.execute(cmd, var)
                if write == False:
                    results.append(self._cursor.fetchall())

            if write == True:
                self._conn.commit()
    
        except Exception as e:
            error = True
            self._conn.rollback()
            logger.error(e)

        if write == True:
            return not error
        else:
            return results

def add_new_user(ID, Name, email, photoID, AccessToken, RefreshToken) -> bool:
    cmd: str = 'INSERT INTO User (UserID, UserName, Email, Photo, AccessToken, RefreshToken) VALUES (%s,%s,%s,%s,%s,%s)'
    var: Tuple[Any, ...] = (ID, Name, email, photoID, AccessToken, RefreshToken)
    write: bool = True

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()

    return result

def add_new_session(session) -> bool:
    cmd: str = 'INSERT INTO Session (SessionID, UserID) VALUES (%s,%s)'
    var: Tuple[Any, ...] = (session, None)
    write: bool = True

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()

    return result

def add_new_song(SongID, URL, Platform, Title, UploaderID, ThumbnailID, Likecount, Length, Download) -> bool:
    cmd: str = 'INSERT INTO Song (SongID, OrigURL, Platform, Title, Uploader, SThumbnail, LikeCount, Length, Download) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    var: Tuple[Any, ...] = (SongID, URL, Platform, Title, UploaderID, ThumbnailID, Likecount, Length, Download)
    write: bool = True

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()

    return result

def add_new_picture(UUID, Time, sizeX, sizeY) -> bool:
    cmd: str = 'INSERT INTO Picture (PicID, Time, SizeX, SizeY) VALUES (%s,%s,%s,%s)'
    var: Tuple[Any, ...] = (UUID, Time, sizeX, sizeY)
    write: bool = True

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()

    return result

def add_new_uploader(ID, URL, OrigID, Name, Platform, Photo, Description) -> bool:
    cmd: str = 'INSERT INTO Uploader (UploaderID, URL, OrigID, Name, UPlatform, Description, UPhoto) VALUES (%s,%s,%s,%s,%s,%s,%s)'
    var: Tuple[Any, ...] = (ID, URL, OrigID, Name, Platform, Description, Photo)
    write: bool = True

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()

    return result

def add_new_queue(QID, Name, Loop, Lock) -> bool:
    cmd: str = 'INSERT INTO Queue (QueueID, Name, LoopStat, Locked) VALUES (%s,%s,%s,%s)'
    var: Tuple[Any, ...] = (QID, Name, Loop, Lock)
    write: bool = True

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()

    return result

def add_user_role_in_queue(QID, UID, Role) -> bool:
    cmd: str = 'INSERT INTO Role (QID, UID, Role) VALUES (%s,%s,%s)'
    var: Tuple[Any, ...] = (QID, UID, Role)
    write: bool = True

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()

    return result

def add_new_history(UID, SID, Time) -> bool:
    cmd: str = 'INSERT INTO History (HUser, HSong, Timestamp) VALUES (%s,%s,%s)'
    var: Tuple[Any, ...] = (UID, SID, Time)
    write: bool = True

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()

    return result

def user_exist(UserID):
    cmd: str = 'SELECT EXISTS (SELECT * FROM User WHERE UserID = %s) AS is_exists'
    var: Tuple[Any, ...] = (UserID,)
    write: bool = False

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()
 
    if result[0][0] == 1:
        return True
    else:
        return False

def session_exist(SessionID):
    cmd: str = 'SELECT EXISTS (SELECT * FROM Session WHERE SessionID = %s) AS is_exists'
    var: Tuple[Any, ...] = (SessionID,)
    write: bool = False

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()
 
    if result[0][0] == 1:
        return True
    else:
        return False

def song_exist(SongID):
    cmd: str = 'SELECT EXISTS (SELECT * FROM Song WHERE SongID = %s) AS is_exists'
    var: Tuple[Any, ...] = (SongID,)
    write: bool = False

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()

    if result[0][0] == 1:
        return True
    else:
        return False

def uploader_exist(UploaderID):
    cmd: str = 'SELECT EXISTS (SELECT * FROM Uploader WHERE UploaderID = %s) AS is_exists'
    var: Tuple[Any, ...] = (UploaderID,)
    write: bool = False

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()
   
    if result[0][0] == 1:
        return True
    else:
        return False

def picture_exist(PicID):
    cmd: str = 'SELECT EXISTS (SELECT * FROM Picture WHERE PicID = %s) AS is_exists'
    var: Tuple[Any, ...] = (PicID,)
    write: bool = False

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()

    if result[0][0] == 1:
        return True
    else:
        return False
    
def queue_exist(QID):
    cmd: str = 'SELECT EXISTS (SELECT * FROM Queue WHERE QueueID = %s) AS is_exists'
    var: Tuple[Any, ...] = (QID,)
    write: bool = False

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()

    if result[0][0] == 1:
        return True
    else:
        return False

def queue_line_exist(QID, SID, IDX):
    cmd: str = 'SELECT EXISTS (SELECT * FROM QIndex WHERE QID = %s AND QSongID = %s AND `Index` = %s) AS is_exists'
    var: Tuple[Any, ...] = (QID, SID, IDX)
    write: bool = False

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()

    if result[0][0] == 1:
        return True
    else:
        return False

def picture_user_using(PicID):
    cmd: str = 'SELECT EXISTS (SELECT * FROM User WHERE Photo = %s) AS is_exists'
    var: Tuple[Any, ...] = (PicID,)
    write: bool = False

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()

    if result[0][0] == 1:
        return True
    else:
        return False
    
def user_song_like(UserID, SongID):
    cmd: str = 'SELECT EXISTS (SELECT * FROM Like WHERE LUser = %s AND LSong = %s) AS is_exists'
    var: Tuple[Any, ...] = (UserID, SongID)
    write: bool = False

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()

    if result[0][0] == 1:
        return True
    else:
        return False
    
def get_user_by_ID(UserID):
    cmd: str = 'SELECT * FROM User WHERE UserID = %s'
    var: Tuple[Any, ...] = (UserID,)
    write: bool = False

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()

    data = {
        "UserID": result[0][0],
        "UserName": result[0][1],
        "Email": result[0][2],
        "Photo": result[0][3],
        "AccessToken": result[0][4],
        "RefreshToken": result[0][5]
    }
    return data

def get_user_by_session(session):
    cmd: str = 'SELECT * FROM Session WHERE SessionID = %s'
    var: Tuple[Any, ...] = (session,)
    write: bool = False

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()

    data = {
        "UserID": result[0][1]
    }
    return data

def get_song_by_ID(SongID):
    cmd: str = 'SELECT * FROM Song WHERE SongID = %s'
    var: Tuple[Any, ...] = (SongID,)
    write: bool = False

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()

    data = {
        "SongID": result[0][0],
        "OrigURL": result[0][1],
        "Platform": result[0][2],
        "Title": result[0][3],
        "Uploader": result[0][4],
        "Thumbnail": result[0][5],
        "LikeCount": result[0][6],
        "Length": result[0][7],
        "Download": result[0][8]
    }
    return data

def get_uploader_by_ID(UploaderID):
    cmd: str = 'SELECT * FROM Uploader WHERE UploaderID = %s'
    var: Tuple[Any, ...] = (UploaderID,)
    write: bool = False

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()
    
    data = {
        "UploaderID": result[0][0],
        "URL": result[0][1],
        "OrigID": result[0][2],
        "Name": result[0][3],
        "Platform": result[0][4],
        "Description": result[0][5],
        "Photo": result[0][5]
    }
    return data

def get_picture_by_ID(PicID):
    cmd: str = 'SELECT * FROM Picture WHERE PicID = %s'
    var: Tuple[Any, ...] = (PicID,)
    write: bool = False

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()

    data = {
        "PicID": result[0][0],
        "Time": result[0][1],
        "SizeX": result[0][2],
        "SizeY": result[0][3]
    }
    return data

def get_qid_by_uid(ID):
    cmd: str = 'SELECT QID FROM User WHERE UserID = %s'
    var: Tuple[Any, ...] = (ID,)
    write: bool = False

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()

    if len(result) == 0:
        return None
    else:
        return result[0][0]

def get_queue_rows(QID) -> Tuple[List[str], List["datetime"]]:
    cmd: str = 'SELECT * FROM QIndex WHERE QID = %s order by `Index`'
    var: Tuple[Any, ...] = (QID,)
    write: bool = False

    client = sql_client()
    results = client.execute(cmd, var, write)
    client.close()
  
    return ([result[2] for result in results], [result[3] for result in results])

def get_queue_len(QID) -> int:
    cmd: str = 'SELECT COUNT(*) FROM QIndex WHERE QID = %s'
    var: Tuple[Any, ...] = (QID,)
    write: bool = False

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()

    return result[0][0]

def get_queue_info(QID) -> Dict[str, Any]:
    cmd: str = 'SELECT * FROM Queue WHERE QueueID = %s'
    var: Tuple[Any, ...] = (QID,)
    write: bool = False

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()
    
    data = {
        "QueueID": result[0][0],
        "Name": result[0][1],
        "Loop": result[0][2],
        "Locked": result[0][3]
    }
    return data

def get_user_role_in_queue(QID, UID):
    cmd: str = 'SELECT Role FROM Role WHERE QID = %s AND UID = %s'
    var: Tuple[Any, ...] = (QID, UID)
    write: bool = False

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()

    if len(result) == 0:
        return None
    else:
        return result[0][0]

def get_user_topk(UID, k):
    cmd: str = 'SELECT HSong, Count(*) as `Count`, MAX(`Timestamp`) as `Timestamp` FROM History WHERE HUser = %s GROUP BY HSong order by `Count` desc, `Timestamp` desc limit %s'
    var: Tuple[Any, ...] = (UID, k)
    write: bool = False

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()
    
    if len(result) == 0:
        return ([], [])
    else:
        return tuple(map(list, zip(*result)))[:2]

def get_all_topk(k):
    cmd: str = 'SELECT HSong, Count(*) as `Count` FROM History GROUP BY HSong order by `Count` desc limit %s'
    var: Tuple[Any, ...] = (k,)
    write: bool = False

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()
    
    if len(result) == 0:
        return ([], 0)
    else:
        return tuple(map(list, zip(*result)))

def get_song_playcount(SID):
    cmd: str = 'SELECT Count(*) as `Count` FROM History WHERE HSong = %s'
    var: Tuple[Any, ...] = (SID,)
    write: bool = False

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()
    return result[0][0]

def update_session_user(session, user) -> bool:
    cmd: str = 'UPDATE Session SET UserID = %s WHERE SessionID = %s'
    var: Tuple[Any, ...] = (user, session)
    write: bool = True

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()
    return result

def update_song_download(SongID, download) -> bool:
    cmd: str = 'UPDATE Song SET Download = %s WHERE SongID = %s'
    var: Tuple[Any, ...] = (download, SongID)
    write: bool = True

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()
    return result

def update_user_photo(UserID, PicID) -> bool:
    cmd: str = 'UPDATE User SET Photo = %s WHERE UserID = %s'
    var: Tuple[Any, ...] = (PicID, UserID)
    write: bool = True

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()
    return result

def update_user_email(UserID, email) -> bool:
    cmd: str = 'UPDATE User SET Email = %s WHERE UserID = %s'
    var: Tuple[Any, ...] = (email, UserID)
    write: bool = True

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()
    return result

def update_uploader_description(UploaderID, Description) -> bool:
    cmd: str = 'UPDATE Uploader SET Description = %s WHERE UploaderID = %s'
    var: Tuple[Any, ...] = (Description, UploaderID)
    write: bool = True

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()
    return result

def update_user_tokens(UserID, AccTok, RefTok) -> bool:
    cmd: str = 'UPDATE User SET AccessToken = %s, RefreshToken = %s WHERE UserID = %s'
    var: Tuple[Any, ...] = (AccTok, RefTok, UserID)
    write: bool = True

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()
    return result

def add_song_to_queue(QID, start, end, SID, Time) -> bool:
    cmds: List[str] = [
        'UPDATE QIndex SET `Index` = `Index` - POW(2, 31) WHERE QID = %s AND `Index` >= %s AND `Index` < %s',
        'UPDATE QIndex SET `Index` = `Index` + POW(2, 31) + 1 WHERE QID = %s AND `Index` < 0',
        'INSERT INTO QIndex (`QID`, `Index`, `QSongID`, `Time`) VALUES (%s,%s,%s,%s)'
    ]
    vars: List[Tuple[Any, ...]] = [
        (QID, start, end),
        (QID,),
        (QID, start, SID, Time)
    ]
    write: bool = True

    client = sql_client()
    result = client.execute_multi(cmds, vars, write)
    client.close()
    return result

def delete_song_from_queue(QID, start, end) -> bool:
    cmds: List[str] = [
        'DELETE FROM QIndex WHERE `QID` = %s AND `Index` = %s',
        'UPDATE QIndex SET `Index` = `Index` - POW(2, 31) WHERE QID = %s AND `Index` >= %s AND `Index` < %s',
        'UPDATE QIndex SET `Index` = `Index` + POW(2, 31) - 1 WHERE QID = %s AND `Index` < 0'
    ]
    vars: List[Tuple[Any, ...]] = [
        (QID, start),
        (QID, start+1, end),
        (QID,)
    ]
    write: bool = True

    client = sql_client()
    result = client.execute_multi(cmds, vars, write)
    client.close()
    return result

def update_queue_owner(QID, UID) -> bool:
    cmd: str = 'UPDATE User SET QID = %s WHERE UserID = %s'
    var: Tuple[Any, ...] = (QID, UID)
    write: bool = True

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()
    return result

def update_queue_guild(QID, GID) -> bool:
    cmd: str = 'UPDATE Guild SET QID = %s WHERE GuildID = %s'
    var: Tuple[Any, ...] = (QID, GID)
    write: bool = True

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()
    return result

def update_user_role_in_queue(QID, UID, Role) -> bool:
    cmd: str = 'UPDATE Role SET Role = %s WHERE QID = %s AND UID = %s'
    var: Tuple[Any, ...] = (Role, QID, UID)
    write: bool = True

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()
    return result

def update_queue_loop(QID: str, Loop: int) -> bool:
    cmd: str = 'UPDATE Queue SET LoopStat = %s WHERE QueueID = %s'
    var: Tuple[Any, ...] = (Loop, QID)
    write: bool = True

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()
    return result

def delete_picture(PicID) -> bool:
    cmd = 'DELETE FROM Picture WHERE PicID = %s'
    var: Tuple[Any, ...] = (PicID,)
    write: bool = True

    client = sql_client()
    result = client.execute(cmd, var, write)
    client.close()
    return result
