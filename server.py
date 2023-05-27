import os
import flask
import requests
from constant import *
from middleware import middleware
import session
import music
import user
import sql

import urllib.parse
import json

app = flask.Flask(__name__, template_folder=os.path.abspath('./page/'))

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

app.wsgi_app = middleware(app.wsgi_app)

#DB = sql.sql_client(user=SQL_USER, password=SQL_PASSWORD, host=SQL_HOST, port=SQL_PORT, database=SQL_DB)

class MyResponse:
    def __init__(self, data, error = False):
        self.d = {
            "data": data,
            "error": error
        }
        return
    def json(self):
        return json.dumps(self.d, indent=4)


@app.route("/api/login", methods=['GET'])
def login():
    UserID = flask.request.environ['user']
    User = None
    
    if user.check_exist(UserID):
        User = user.get_user(UserID)
    else:
        User = {
            "UserName": "Guest",
            "Email": "test@ebg.tw",
            "Photo": "Default",
            "AccessToken": "Lorem_ipsum",
            "RefreshToken": "Lorem ipsum"
        }

    return flask.render_template('login.html',
            Name=User["UserName"],
            Session=flask.request.environ['session'],
            Photo = f'{SITE}/public/{User["Photo"]}',
            AUTH_URL=AUTH_URL,
            CLIENT_ID=CLIENT_ID,
            STATE=flask.request.environ['session'],
            OAUTH_URL=urllib.parse.quote(OAUTH_URL)
            #SITE=SITE
        )

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
            
            if offset > 90 or length > 20 or offset < 0 or length <= 0:
                raise ValueError("Wrong data range")

            if query_str is None:
                res = MyResponse("No keyword specified.", error=True)
        
            else:
                d, error = music.search(query_str, offset, length)
                res = MyResponse(d, error=error)
        except ValueError:
            res = MyResponse("Wrong data range", error=True)
        
    else:
        res = MyResponse("Wrong usage.", error=True)

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


@app.route("/api/500", methods=['GET'])
def resp500():
    return flask.make_response("As you wish.", 500)
