from __future__ import annotations
from typing import List, Set, Dict, Tuple
from typing import Union, Optional, Any

import requests
from datetime import datetime
from loguru import logger

import utils.picture as picture
import utils.musicqueue as musicqueue
from utils.constant import CLIENT_ID, CLIENT_SECRET, TOKEN_URL
import utils.sql as sql
import utils.music as music

def check_exist(ID):
    return sql.user_exist(ID)

def get_user(ID):
    return sql.get_user_by_ID(ID)

def update_photo(UserID, Photo):
    return sql.update_user_photo(UserID = UserID, PicID = Photo)

def update_email(UserID, email):
    return sql.update_user_email(UserID = UserID, email = email)

def update_tokens(UserID, AccessToken, RefreshToken):
    return sql.update_user_tokens(UserID, AccessToken, RefreshToken)

def get_like(UID):
    
    lst = sql.get_user_like(UID)

    SongIDlst = []

    for item in lst:
        SongIDlst.append(item[0])
    
    return SongIDlst

def set_user_like(UID, SID):

    Time = datetime.now()
    return sql.add_new_user_like(UID, SID, Time)

def unset_user_like(UID, SID):

    return sql.delete_user_like(UID, SID)

def fetch_dc_info(AccessToken = None, RefreshToken = None, UserID = None):
    if UserID is not None:
        user = get_user(UserID)
        AccessToken = user["AccessToken"]
        RefreshToken = user["RefreshToken"]

    headers = {
        'Authorization': f'Bearer {AccessToken}'
    }
    r = requests.get("https://discordapp.com/api/users/@me", headers=headers)
    
    if r.status_code == 200:
    
        data = r.json()
        return data
    elif r.status_code == 401 and UserID is not None:
        try:
            fetch_new_token(UserID = UserID, RefreshToken = RefreshToken)
            return fetch_dc_info(UserID=UserID)
        except Exception as e:
            raise e
    else:
        r.raise_for_status()
    return

def add_user(res_data, AccessToken, RefreshToken):
    
    UserID = res_data["id"]
    UserName = res_data["username"]
    email = res_data["email"]
    ava_hash = res_data["avatar"]
    discriminator = res_data["discriminator"]

    PicID = download_photo(UserID, ava_hash, discriminator)

    success = sql.add_new_user(UserID, UserName, email, PicID, AccessToken, RefreshToken)

    return

def fetch_user(AccessToken = None, RefreshToken = None, ID = None):
    
    res_data = {}

    if ID is not None:
        res_data = fetch_dc_info(UserID=ID)
    else:
        res_data = fetch_dc_info(AccessToken=AccessToken, RefreshToken=RefreshToken)
        ID = res_data["id"]

    if not check_exist(ID):
        add_user(res_data, AccessToken, RefreshToken)
    else:
        if AccessToken is not None and RefreshToken is not None:
            update_tokens(ID, AccessToken, RefreshToken)

        update_info(ID, res_data)
    
    return get_user(ID)

def download_photo(UserID, ava_hash, discriminator):
    Photo_url = ""
    if ava_hash is None:
        remainder = int(discriminator) % 5
        Photo_url = f"https://cdn.discordapp.com/embed/avatars/{remainder}.png"
    else:
        Photo_url = f"https://cdn.discordapp.com/avatars/{UserID}/{ava_hash}?size=256"
    
    PicID = picture.uuid(Photo_url)
    if not picture.check_exist(PicID):
        picture.add_picture(Photo_url)
    return PicID

def update_info(ID, res_data = None):
    
    if res_data is None:
        res_data = fetch_dc_info(UserID=ID)

    email = res_data["email"]
    ava_hash = res_data["avatar"]
    discriminator = res_data["discriminator"]

    PicID = download_photo(ID, ava_hash, discriminator)

    user = get_user(ID)

    if user["Photo"] != PicID:
        update_photo(ID, PicID)
        if picture.picture_user_using(user["Photo"]) == False:
            picture.delete_picture(user["Photo"])

    if user["Email"] != email:
        update_email(ID, email)

    return

def fetch_new_token(UserID, RefreshToken = None):
    if RefreshToken is not None:
        pass
    else:
        RefreshToken = get_user(UserID)["RefreshToken"]

    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': RefreshToken
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post(TOKEN_URL, data=data, headers=headers)
    r.raise_for_status()
    data = r.json()
    AccessToken = data["access_token"]
    RefreshToken = data["refresh_token"]

    update_tokens(UserID, AccessToken, RefreshToken)

    return

def s_get_like(UID) -> Tuple[bool, str | Dict[str, List["music.track"] | int]]:
    
    if UID is None:
        return (False, "Not login.")
    
    SIDlst = get_like(UID)
    tracks = music.gen_track_list(UUIDs=SIDlst, UserID=UID)

    d = {
        "list": tracks,
        "total": len(tracks)
    }

    return (True, d)

def s_set_like(UID, SID, code) -> Tuple[bool, str]:

    if UID is None:
        return (False, "Not login.")
    
    if not music.check_exist(SID):
        return (False, "Value SongID invalid.")
    
    if not isinstance(code, bool):
        return (False, "Value set invalid.")

    stat = True

    if code == True:
        stat = set_user_like(UID, SID)
    else:
        stat = unset_user_like(UID, SID)

    if stat == True:
        return (True, "Success")
    else:
        logger.error("Error when set user like. User = {UID}, SID = {SID}, set = {code}")
        return (True, "Success")
    