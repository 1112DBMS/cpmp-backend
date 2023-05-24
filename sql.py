session_sql = {}
user_sql = {}
uploader_sql = {}
song_sql = {}
picture_sql = {}

def run_sql(cmd):
    return None

def session_to_user(session):
    if session in session_sql:
        return session_sql[session]
    else:
        return None

def bind_user_to_session(session, user):
    session_sql[session] = user

def unbind_user_and_session(session):
    if session in session_sql:
        del session_sql[session]
    return

def update_user_access_token(ID, AccessToken, RefreshToken):
    user_sql[ID]["AccessToken"] = AccessToken
    user_sql[ID]["RefreshToken"] = RefreshToken
    return

def update_user_photo(UserID, PicID):
    user_sql[UserID]["Photo"] = PicID
    return

def user_like_song_query(UserID, UUID):
    return False

def user_exist(UserID):
    return (UserID in user_sql)

def uploader_exist(UploaderID):
    return (UploaderID in uploader_sql)

def picture_exist(PicID):
    return (PicID in picture_sql)

def add_new_picture(UUID, Time, sizeX, sizeY):
    picture_sql[UUID] = {
        "Time": Time,
        "sizeX": sizeX,
        "sizeY": sizeY
    }
    return

def add_new_user(ID, Name, email, photoID, AccessToken, RefreshToken):
    user_sql[ID] = {
        "UserName": Name,
        "Email": email,
        "Photo": photoID,
        "AccessToken": AccessToken,
        "RefreshToken": RefreshToken
    }
    return

def add_new_song(ID, URL, Platform, Title, Length, Uploader, thumbnail, likecount):
    song_sql[ID] = {
        "SongID": ID,
        "OrigURL": URL,
        "Platform": Platform,
        "Title": Title,
        "Length": Length,
        "Uploader": Uploader,
        "thumbnail": thumbnail,
        "likecount": likecount
    }
    return

def add_new_uploader(ID, URL, OrigID, Name, Platform, Photo, Description):
    uploader_sql[ID] = {
        "UploaderID": ID,
        "URL": URL,
        "OrigID": OrigID,
        "Name": Name,
        "Platform": Platform,
        "Photo": Photo,
        "Description": Description
    }
    return

def get_song_by_ID(ID):
    if ID in song_sql:
        return [song_sql[ID]]
    else:
        return []

def get_uploader_by_ID(ID):
    if ID in uploader_sql:
        return [uploader_sql[ID]]
    else:
        return []

def get_user_by_ID(ID):
    if ID in user_sql:
        return [user_sql[ID]]
    else:
        return []
