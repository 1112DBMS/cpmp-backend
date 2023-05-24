import sql
import requests
import uuid
import picture
from constant import CLIENT_ID, CLIENT_SECRET, TOKEN_URL

def add_user(ID, Name, Email, Photo, AccessToken, RefreshToken):
    sql.add_new_user(ID, Name, Email, Photo, AccessToken, RefreshToken)

def check_exist(ID):
    return sql.user_exist(ID)

def get_user(ID):
    user = sql.get_user_by_ID(ID)
    return user[0]

def fetch_user(AccessToken = None, RefreshToken = None, UserID = None):
    if UserID is not None:
        user = get_user(UserID)
        AccessToken = user["AccessToken"]
        RefreshToken = user["RefreshToken"]

    headers = {
        'Authorization': 'Bearer %s' % (AccessToken)
    }
    r = requests.get("https://discordapp.com/api/users/@me", headers=headers)
    r.raise_for_status()
    
    data = r.json()
    print(data)

    return data

def update_token(ID, AccessToken = None, RefreshToken = None):
    if AccessToken is not None and RefreshToken is not None:
        pass
    else:
        RefreshToken = sql.get_user_by_ID(ID)["RefreshToken"]
        data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post(TOKEN_URL, data=data, headers=headers)
        r.raise_for_status()
        data = r.json()
        AccessToken = data["access_token"]
        RefreshToken = data["refresh_token"]

    sql.update_user_access_token(
        ID=ID,
        AccessToken=AccessToken,
        RefreshToken=RefreshToken
    )
    return

def update_photo(UserID, Photo = None):
    if Photo is None:
        User = fetch_user(UserID=UserID)
        ava_hash = User["avatar"]
        Photo_url = None
        
        if ava_hash is None:
            remainder = int(User['discriminator']) % 5
            Photo_url = f"https://cdn.discordapp.com/embed/avatars/{remainder}.png"
        else:
            Photo_url = f"https://cdn.discordapp.com/avatars/{UserID}/{ava_hash}"
        Photo = picture.uuid(Photo_url)
        picture.add_picture(Photo_url)
    sql.update_user_photo(UserID = UserID, PicID = Photo)
    return
