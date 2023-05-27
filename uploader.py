import sql
from sql import sql_client
import picture
import re
import json
from bs4 import BeautifulSoup
from pytube.contrib.channel import Channel

from uuid import uuid3, NAMESPACE_URL

def uuid(url):
    return str(uuid3(NAMESPACE_URL, url))

def get_uploader(ID):
    client = sql_client()
    result = client.get_uploader_by_ID(ID)
    client.close()
    return result

def check_exist(ID):
    client = sql_client()
    result = client.uploader_exist(ID)
    client.close()
    return result

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

        client = sql_client()
        client.add_new_uploader(UUID, URL, OrigID, Name, Platform, PhotoID, Description)
        client.close()

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
