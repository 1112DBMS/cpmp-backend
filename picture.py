from PIL import Image
import requests
import os

from uuid import uuid3, NAMESPACE_URL
from sql import sql_client
from datetime import datetime
from constant import PIC_FOLDER

def uuid(url):
    return str(uuid3(NAMESPACE_URL, url))

def check_exist(ID):
    client = sql_client()
    result = client.picture_exist(ID)
    client.close()
    return result

def get_picture(ID):
    client = sql_client()
    result = client.get_picture_by_ID(ID)
    client.close()
    return result

def picture_user_using(ID):
    client = sql_client()
    result = client.picture_user_using(ID)
    client.close()
    return result

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
    print("Add new PIC:", UUID)
    client = sql_client()
    client.add_new_picture(UUID, Time, sizeX, sizeY)
    client.close()
    return

def fetch_picture(url):
    UUID = uuid(url)

    if not check_exist(UUID):
        add_picture(url)

    return get_picture(UUID)

def delete_picture(UUID):
    if not check_exist(UUID):
        return

    client = sql_client()
    client.delete_picture(UUID)
    client.close()

    Filepath = f'{PIC_FOLDER}/{UUID}'
    if os.path.isfile(Filepath):
        os.remove(Filepath)

    print("PIC deleted:", UUID)

    return

if __name__ == '__main__':
    url = input("New pic URL:")
    add_picture(url)
