import sql
import picture
from uuid import uuid3, NAMESPACE_URL
from pytube.contrib.channel import Channel

def uuid(url):
    return str(uuid3(NAMESPACE_URL, url))

def get_uploader(ID):
    if check_exist(ID):
        uploader = sql.get_uploader_by_ID(ID)
        return uploader[0]
    else:
        return None

def check_exist(ID):
    return sql.uploader_exist(ID)

def save_uploader(url, platform):
    if platform == "youtube":
        chan = Channel(url)
        UUID = uuid(url)
        URL = url
        OrigID = chan.channel_id
        Name = chan.channel_name
        Platform = platform
        
        Photo = "Lorem ipsum"   #TODO CRITICAL

        Description = chan.about_html

        sql.add_new_uploader(UUID, URL, OrigID, Name, Platform, Photo, Description)
    elif platform == "spotify":
        pass #TODO
    else:
        raise ValueError(f"Unknown platform = {platform}!")
    return

def fetch_uploader(url = None, UUID = None, platform = "default"):
    if UUID is not None:
        pass
    elif url is not None:
        UUID = uuid(url)
    uploader = get_uploader(UUID)
    if uploader is None:
        save_uploader(url=url, platform=platform)
        uploader = get_uploader(UUID)
    return uploader
