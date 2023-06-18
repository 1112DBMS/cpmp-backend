from typing import List, Set, Dict, Tuple
from typing import Union, Optional, Any

import flask
from flask import make_response as mkres
import requests
import json
from loguru import logger

from utils.constant import *
from utils.middleware import middleware
import utils.session as session
import utils.music as music
import utils.user as user
import utils.musicqueue as musicqueue
import utils.history as history

from datetime import datetime, time

logfile = logger.add(f'./log/{datetime.now().strftime("%Y-%m-%d")}.log', rotation=time.min)

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
    OAUTH_URL = flask.request.headers.get('referer').split('?')[0]
    
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': OAUTH_URL
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
    if not flask.request.is_json:
        return res400()
    
    data = flask.request.get_json()

    SongID = data.get('id', None)

    stat, info = music.s_download(SongID)

    return Mymkres(stat, info)

@app.route("/api/track", methods=['POST'])
def get_track():
    UserID = flask.request.environ['user']

    if not flask.request.is_json:
        return res400()
    
    data = flask.request.get_json()

    SongID = data.get('id', None)
    URL = data.get('url', None)
    
    stat, info = music.s_get_track(URL, SongID, UserID)

    return Mymkres(stat, info)

@app.route("/api/play", methods=['GET'])
def record_and_redirect():
    UserID = flask.request.environ['user']

    SongID = flask.request.args.get('id', None)
    
    stat, info = history.s_record_and_redirect(UserID, SongID)

    if stat == True:
        return flask.redirect(f"/songs/{SongID}", code=303)
    else:
        return Mymkres(stat, info)

@app.route("/api/top", methods=['GET'])
def get_topplay():
    UserID = flask.request.environ['user']

    Self = flask.request.args.get('self', None)
    k = flask.request.args.get('k', None)
    
    stat, info = history.s_get_topplay(UserID, k, Self)

    return Mymkres(stat, info)

@app.route("/api/queue", methods=['GET'])
def get_queue():
    UserID = flask.request.environ['user']
    QID = flask.request.args.get('id', None)

    stat, info = musicqueue.s_get_queue(QID, UserID)

    return Mymkres(stat, info)

@app.route("/api/queue", methods=['POST'])
def post_queue():
    
    UserID = flask.request.environ['user']

    if not flask.request.is_json:
        return res400()

    data = flask.request.get_json()

    SongID = data.get('id', None)
    QID = data.get('queue', None)
    SongIDX = data.get('idx', None)

    stat, info = musicqueue.s_post_queue(QID, SongID, SongIDX, UserID)

    return Mymkres(stat, info)

@app.route("/api/queue", methods=['DELETE'])
def delete_queue():
    UserID = flask.request.environ['user']

    if not flask.request.is_json:
        return res400()

    data = flask.request.get_json()

    TrackID = data.get('id', None)
    SongIDX = data.get('idx', None)
    QID = data.get('queue', None)
    
    stat, info = musicqueue.s_delete_queue(QID, TrackID, SongIDX, UserID)

    return Mymkres(stat, info)

@app.route("/api/queue/loop", methods=['POST'])
def set_loop():
    UserID = flask.request.environ['user']

    if not flask.request.is_json:
        return res400()

    data = flask.request.get_json()

    Loop = data.get("loop", None)
    QID = data.get('queue', None)

    stat, info = musicqueue.s_set_loop(QID, UserID, Loop)

    return Mymkres(stat, info)

@app.route("/api/queue/next", methods=['POST'])
def queue_next():
    UserID = flask.request.environ['user']

    if not flask.request.is_json:
        return res400()

    data = flask.request.get_json()

    QID = data.get('queue', None)

    stat, info = musicqueue.s_queue_next(QID, UserID)

    return Mymkres(stat, info)

#########################################
#                                       #
#               Responds                #
#                                       #
#########################################

def Mymkres(stat: bool, info: Any):
    if stat == True:
        return res200(info)
    else:
        if info == "400":
            return res400()
        elif info == "501":
            return res501()
        elif info == "Not login.":
            return res401()
        elif info.startswith("Value") and info.endswith("invalid."):
            return res400(info)
        elif info.endswith("not matched."):
            return res400(info)
        elif info == "No permission.":
            return res403()
        else:
            logger.error(info)
            return res500()

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

@app.route("/api/501", methods=['GET'])
def res501(text: str = "501 Not Implemented."):
    return mkres(MyResponse(text, error=True).json(), 501)
