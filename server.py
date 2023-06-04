from typing import List, Set, Dict, Tuple
from typing import Union, Optional

import os
import flask
from flask import make_response as mkres
import requests
import urllib.parse
import json

from utils.constant import *
from utils.middleware import middleware
import utils.session as session
import utils.music as music
import utils.user as user
import utils.sql as sql
import utils.musicqueue as musicqueue
import utils.history as history

app = flask.Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

app.wsgi_app = middleware(app.wsgi_app)

class MyResponse:
    def __init__(self, data, error = False):
        self.d = {
            "data": data,
            "error": error
        }
        return
    def json(self):
        return json.dumps(self.d, indent=4)

@app.route("/api/logout", methods=['GET'])
def logout():
    if session.check_exist(flask.request.environ['session']):
        session.unbind(flask.request.environ['session'])
        return MyResponse("Success").json()
    else:
        return MyResponse("Unknown session.", error=True).json()

@app.route("/api/oauth", methods=['GET'])
def oauth():
    code = flask.request.args.get('code')
    #state = flask.request.args.get('state')
    OAUTH_URL_=flask.request.headers.get('referer').split('?')[0]
    if OAUTH_URL_ == "https://discord.com/":
        OAUTH_URL_ = OAUTH_URL
    print(OAUTH_URL_)
    
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': OAUTH_URL_
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    r = requests.post(TOKEN_URL, data=data, headers=headers)
    
    if r.status_code == 200:
        JSON = r.json()
        UserID = user.fetch_user(JSON["access_token"], JSON["refresh_token"])["UserID"]
        session.bind(flask.request.environ['session'], UserID)
        return MyResponse("Success").json()

    elif r.status_code//100 == 4:
        return MyResponse("Failed to fetch discord user token.", error=True).json()
    
    elif r.status_code//100 == 5:
        return MyResponse("Discord API server error.", error=True).json()

    else:
        return MyResponse(f"Unknown error. http code = {r.status_code}", error=True).json()

@app.route("/api/profile", methods=['GET'])
def profile():
    UserID = flask.request.environ['user']
    
    data = None

    if user.check_exist(UserID):
        user.update_info(UserID)
        User = user.get_user(UserID)
        data = {
            "username": User["UserName"],
            "email": User["Email"],
            "avatar": User["Photo"],
            "userId": UserID
        }
    
    return MyResponse(data).json()

@app.route("/api/search", methods=['POST'])
def search():
    
    res = None

    if flask.request.is_json:
        data = flask.request.get_json()
        query_str = data.get('keyword', None)
        offset = data.get('offset', 0)
        length = data.get('len', 10)

        try:
            offset = int(offset)
            length = int(length)
            
            if offset > 90 or length > 30 or offset < 0 or length <= 0:
                raise ValueError("Wrong data range")

            if query_str is None:
                res = MyResponse("No keyword specified.", error=True)
        
            else:
                d, error = music.search(query_str, offset, length)
                res = MyResponse(d, error=error)
        except ValueError:
            res = MyResponse("Wrong data range", error=True)
        
    else:
        return res400()

    return res.json()

@app.route("/api/download", methods=['POST'])
def download():
    res = None

    if flask.request.is_json:
        data = flask.request.get_json()

        SongID = data.get('id', None)

        if SongID is not None:

            if music.download(SongID) == True:
                res = MyResponse("Success")
            
            else:
                res = MyResponse("Given song id is invalid.", error=True)

        else:
            res = MyResponse("No song id is given.", error=True)

    else:
        res = MyResponse("Wrong usage.", error=True)

    return res.json()

@app.route("/api/track", methods=['POST'])
def get_track():
    res = None

    if flask.request.is_json:
        data = flask.request.get_json()

        SongID = data.get('id', None)
        URL = data.get('url', None)

        if SongID is not None or URL is not None:
            try:
                res = MyResponse(music.gen_track(url = URL, UUID = SongID, UserID = None))
            except Exception as e:
                res = MyResponse("Invalid UUID or url is given.", error=True)
                print(e)
        else:
            res = MyResponse("No id nor url is given.", error=True)

    else:
        return res400()

    return res.json()

@app.route("/api/play", methods=['GET'])
def play_redirect():
    UserID = flask.request.environ['user']

    SongID = flask.request.args.get('id', None)
    
    if history.add_record(UserID, SongID):
        return flask.redirect(f"/songs/{SongID}", code=303)
    else:
        return res400()

@app.route("/api/top", methods=['GET'])
def get_topplay():
    UserID = flask.request.environ['user']

    Self = True if flask.request.args.get('self') == "1" else False
    k = flask.request.args.get('k', 10)
    
    try:
        k = int(k)
        if k > 10 or k <= 0:
            raise ValueError("Wrong data range")
        
    except ValueError:
        return res400()

    if UserID is None and Self == True:
        return MyResponse({"list":None,"total":0}).json()
    if Self == True:
        return MyResponse(history.top_tracks(k, UID=UserID)).json()
    else:
        return MyResponse(history.top_tracks(k)).json()

@app.route("/api/queue", methods=['GET'])
def get_queue():
    UserID = flask.request.environ['user']

    if UserID is None:
        return mkres(MyResponse("You must login first.", error=True).json(), 401)
    
    QID = flask.request.args.get('id', musicqueue.fetch_queue_ID(UserID))

    if not musicqueue.check_exist(QID):
        return MyResponse("Invalid queue id.", error=True).json()

    tracks = musicqueue.get_queue_tracks(QID)
    
    data = {
        "list": tracks,
        "total": len(tracks),
        "loop": musicqueue.get_queue(QID)["Loop"]
    }

    return MyResponse(data).json()

@app.route("/api/queue", methods=['POST'])
def post_queue():
    
    UserID = flask.request.environ['user']

    if UserID is None:
        return mkres(MyResponse("You must login first.", error=True).json(), 401)

    if not flask.request.is_json:
        return res400()

    data = flask.request.get_json()

    TrackID = data.get('id', None)
    
    if TrackID is None or not music.check_exist(TrackID):
        return MyResponse("Invalid track id.", error=True).json()
    
    QID = data.get('queue', musicqueue.fetch_queue_ID(UserID))

    if not musicqueue.check_exist(QID):
        return MyResponse("Invalid queue id.", error=True).json()

    if not musicqueue.can_edit(QID, UserID):
        return res403()
    
    try:
        musicqueue.push_song(QID, TrackID)
    except Exception as e:
        print(e)
        return res500()

    return res200()

@app.route("/api/queue", methods=['DELETE'])
def delete_queue():
    UserID = flask.request.environ['user']

    if UserID is None:
        return mkres(MyResponse("You must login first.", error=True).json(), 401)
    
    if not flask.request.is_json:
        return res400()

    data = flask.request.get_json()

    TrackID = data.get('id', None)
    SongIDX = data.get('idx', None)
    QID = data.get('queue', musicqueue.fetch_queue_ID(UserID))

    if SongIDX is None or TrackID is None:
        return MyResponse("No track specified.", error=True).json()

    stat, info = musicqueue.remove_track(QID, TrackID, SongIDX, UserID)
    if stat == True:
        return MyResponse("Success").json()
    else:
        if info == "Invalid QID":
            return MyResponse("Invalid Queue id.", error=True).json()
        elif info == "Forbidden":
            return res403()
        elif info == "ID IDX not match":
            return MyResponse("Id not matched.", error=True).json()

    return res500()

@app.route("/api/queue/loop", methods=['POST'])
def set_loop():
    UserID: Optional[str] = flask.request.environ['user']

    if not flask.request.is_json:
        return res400()

    data: Dict[str, str] = flask.request.get_json()

    Loop: str = data.get("loop", None)
    QID: str = data.get('queue', musicqueue.fetch_queue_ID(UserID))

    stat, info = musicqueue.set_loop(UserID, QID, Loop)

    if stat == False:
        if info == "Not login.":
            return res401()
        elif info == "Invalid queue id.":
            return res400(info)
        elif info == "Loop value not given.":
            return res400(info)
        elif info == "No permission":
            return res403()
        elif info == "500":
            return res500()

    else:
        return res200()
    


#########################################
#                                       #
#               Responds                #
#                                       #
#########################################

@app.route("/api/200", methods=['GET'])
def res200(text: str = "Success", error: bool = False):
    return mkres(MyResponse(text, error=error).json(), 200)

@app.route("/api/400", methods=['GET'])
def res400(text: str = "400 Bad Request."):
    return mkres(MyResponse(text, error=True).json(), 400)

@app.route("/api/401", methods=['GET'])
def res401(text: str = "You must login first."):
    return mkres(MyResponse(text, error=True).json(), 401)

@app.route("/api/403", methods=['GET'])
def res403(text: str = "403 Forbidden."):
    return mkres(MyResponse(text, error=True).json(), 403)

@app.route("/api/500", methods=['GET'])
def res500(text: str = "500 Internal Server Error."):
    return mkres(MyResponse(text, error=True).json(), 500)