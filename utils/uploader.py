import re
import json
from bs4 import BeautifulSoup
from pytube.contrib.channel import Channel
from uuid import uuid3, NAMESPACE_URL

import utils.sql as sql
import utils.picture as picture

def uuid(url):
    return str(uuid3(NAMESPACE_URL, url))

def get_uploader(ID):
    return sql.get_uploader_by_ID(ID)

def check_exist(ID):
    return sql.uploader_exist(ID)

def add_uploader(url, platform):
    if platform == "youtube":
        chan = Channel(url)
        UUID = uuid(url)
        URL = url
        OrigID = chan.channel_id
        Name = chan.channel_name
        Platform = platform
        

        About_html = chan.about_html

        soup = BeautifulSoup(About_html, 'html.parser')

        scripts = soup.find_all('script')
        urls = []
        for script in scripts:
            # find all avatar patterns in the script
            matches = re.findall(r'"avatar":{"thumbnails":(.*?)]}', str(script.string))
    
            for match in matches:
                # load the string as JSON
                thumbnails = json.loads(match + ']')
        
                # get the last url
                url = thumbnails[-1]['url']
                urls.append(url)
        
        PhotoID = picture.fetch_picture(urls[-1])["PicID"]

        meta_tag = soup.find('meta', {'itemprop': 'description'})
        Description = meta_tag['content'] if meta_tag else None

        success = sql.add_new_uploader(UUID, URL, OrigID, Name, Platform, PhotoID, Description)

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
    
    if not check_exist(UUID):
        add_uploader(url=url, platform=platform)
        print("Add new uploader:", UUID)
    else:
        print("Uploader exists.")

    return get_uploader(UUID)
