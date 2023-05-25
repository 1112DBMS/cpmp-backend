from sql import sql_client
import requests
import uuid
import picture
from constant import CLIENT_ID, CLIENT_SECRET, TOKEN_URL

def create_user(AccessToken, RefreshToken):
        
    res_data = fetch_user(AccessToken=AccessToken, RefreshToken=RefreshToken)
    
    UserID = res_data["id"]
    UserName = res_data["username"]
    email = res_data["email"]
    ava_hash = res_data["avatar"]
    discriminator = res_data["discriminator"]

    PicID = download_photo(UserID, ava_hash, discriminator)

    if check_exist(UserID):
        print("User exists.")
        pass
    else:
        print("Creating user:", UserID, UserName)
        client = sql_client()
        client.add_new_user(UserID, UserName, email, PicID, AccessToken, RefreshToken)
        client.close()

    return UserID

def check_exist(ID):
    client = sql_client()
    result = client.user_exist(ID)
    client.close()
    return result

def get_user(ID):
    client = sql_client()
    result = client.get_user_by_ID(ID)
    client.close()
    return result

def fetch_user(AccessToken = None, RefreshToken = None, UserID = None):
    if UserID is not None:
        user = get_user(UserID)
        AccessToken = user["AccessToken"]
        RefreshToken = user["RefreshToken"]

    headers = {
        'Authorization': 'Bearer %s' % (AccessToken)
    }
    r = requests.get("https://discordapp.com/api/users/@me", headers=headers)
    
    if r.status_code == 200:
    
        data = r.json()
        return data
    elif r.status_code//100 == 4:
        r.raise_for_status()
    else:
        r.raise_for_status()
    return

def download_photo(UserID, ava_hash, discriminator):
    Photo_url = ""
    if ava_hash is None:
        remainder = int(discriminator) % 5
        Photo_url = f"https://cdn.discordapp.com/embed/avatars/{remainder}.png"
    else:
        Photo_url = f"https://cdn.discordapp.com/avatars/{UserID}/{ava_hash}"
    
    PicID = picture.uuid(Photo_url)
    if not picture.check_exist(PicID):
        print("New Pic:", PicID)
        picture.add_picture(Photo_url)
    else:
        print("Picture exists.")
    return PicID

def update_info(ID):
    return
    user.update_token(UserID, AccessToken, RefreshToken)
    UserData = fetch_user(UserID=ID)
    user.update_photo(UserID)
    # TODO: update on GET /api/profile.
    #   Update Tokens, avatar and email.

'''
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

def update_photo(UserID, Photo):
    sql.update_user_photo(UserID = UserID, PicID = Photo)
    return
'''
