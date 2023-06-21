import os
import requests
from PIL import Image
from uuid import uuid3, NAMESPACE_URL
from datetime import datetime

import utils.sql as sql
from utils.constant import PIC_FOLDER

def uuid(url):
    return str(uuid3(NAMESPACE_URL, url))

def check_exist(ID):
    return sql.picture_exist(ID)

def get_picture(ID):
    return sql.get_picture_by_ID(ID)

def picture_user_using(ID):
    return sql.picture_user_using(ID)

def add_picture(url):
    UUID = uuid(url)
    if check_exist(UUID):
        return
    Filepath = f'{PIC_FOLDER}/{UUID}'
    r = requests.get(url, allow_redirects=True, stream=True)
    with open(Filepath, 'wb') as file:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
    img = Image.open(Filepath)
    sizeX, sizeY = img.size
    Time = datetime.now()
    success = sql.add_new_picture(UUID, Time, sizeX, sizeY)
    return success

def fetch_picture(url):
    UUID = uuid(url)

    if not check_exist(UUID):
        add_picture(url)

    return get_picture(UUID)

def delete_picture(UUID):
    if not check_exist(UUID):
        return

    success = sql.delete_picture(UUID)

    if success:
        Filepath = f'{PIC_FOLDER}/{UUID}'
        if os.path.isfile(Filepath):
            os.remove(Filepath)

        return True
    else:
        return False

if __name__ == '__main__':
    url = input("New pic URL:")
    add_picture(url)
    