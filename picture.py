from PIL import Image
import requests
from uuid import uuid3, NAMESPACE_URL
import sql
from datetime import datetime
from constant import PIC_FOLDER

def uuid(url):
    return str(uuid3(NAMESPACE_URL, url))

def check_exist(ID):
    return sql.picture_exist(ID)

def add_picture(url):
    UUID = uuid(url)
    Filepath = f'{PIC_FOLDER}/{UUID}'
    r = requests.get(url, allow_redirects=True, stream=True)
    with open(Filepath, 'wb') as file:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
    img = Image.open(Filepath)
    sizeX, sizeY = img.size
    Time = datetime.now()
    sql.add_new_picture(UUID, Time, sizeX, sizeY)
    return
