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

@app.route("/api/hello", methods=['GET'])
def hello():
    data = {'session': flask.request.environ['session'], 'user': flask.request.environ['user']}
    return data


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
            AccessToken = User["AccessToken"],
            RefreshToken = User["RefreshToken"],
            Photo = f'{SITE}/public/{User["Photo"]}',
            AUTH_URL=AUTH_URL,
            CLIENT_ID=CLIENT_ID,
            STATE=flask.request.environ['session'],
            OAUTH_URL=urllib.parse.quote(OAUTH_URL)
            #SITE=SITE
        )

@app.route("/api/logout", methods=['GET'])
def logout():
    session.unbind(flask.request.environ['session'])
    data = {
        "data": "Success",
        "error": False
    }
    return json.dumps(data, indent = 4)

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
        UserID = user.create_user(JSON["access_token"], JSON["refresh_token"])
        session.bind(flask.request.environ['session'], UserID)
        data = {
            "data": "Success",
            "error": False
        }
        return json.dumps(data, indent = 4)
    elif r.status_code//100 == 4:
        data = {
            'data': "Failed to fetch discord user token.",
            'error': True
        }
        return json.dumps(data, indent = 4)
    elif r.status_code//100 == 5:
        data = {
            'data': "Discord API server error.",
            'error': True
        }
        return json.dumps(data, indent = 4)
    else:
        data = {
            'data': f"Unknown error. http code = {r.status_code}",
            'error': True
        }
        return json.dumps(data, indent = 4)

@app.route("/api/profile", methods=['GET'])
def profile():
    UserID = flask.request.environ['user']
    data = None
    
    if user.check_exist(UserID):
        user.update_info(UserID)
        User = user.get_user(UserID)
        data = {
            "data": {
                "username": User["UserName"],
    	        "email": User["Email"],
    	        "avatar": User["Photo"],
	        "userId": UserID
            },
            "error": False
        }
    else:
        data = {
            "data": None,
            "error": False
        }
    return json.dumps(data, indent = 4)


@app.route("/api/search", methods=['POST'])
def search():
    res_data = {}
    if flask.request.is_json:
        data = flask.request.get_json()
        query_str = data.get('keyword', None)
        offset = data.get('offset', 10)
        length = data.get('len', 10)
        print("offset:", offset)
        print("length:", length)
        if query_str is None:
            res_data = {
                'data': "No keyword specified.",
                'error': True
            }
        else:
            res_data = music.search(query_str, offset, length)
    else:
        res_data = {
            'data': "Wrong usage.",
            'error': True
        }
    return json.dumps(res_data, indent = 4)

@app.route("/api/download", methods=['POST'])
def download():
    res_data = {}
    if flask.request.is_json:
        data = flask.request.get_json()

        SongID = data.get('id', None)

        if SongID is not None:
            if music.download(SongID) == True:
                res_data = {
                    "data": "Success",
                    "error": False
                }
            else:
                res_data = {
                    "data": "Given song id is invalid.",
                    "error": True
                }
        else:
            res_data = {
                "data": "No song id is given.",
                "error": True
            }
    else:
        res_data = {
            'data': "Wrong usage.",
            'error': True
        }

    return json.dumps(res_data, indent = 4)


@app.route("/api/500", methods=['GET'])
def resp500():
    return flask.make_response("As you wish.", 500)





@app.route("/get_sound", methods=['GET'])
def get_sound():
    wanted_id = flask.request.args.get('id')
    if wanted_id is not None:
        #db.execute("")
        return flask.send_from_directory(app.config['UPLOAD_FOLDER'],
                               wanted_id)
        return "Your id is <strong>{id}</strong>.".format(id=wanted_id)
    return "Send you a sound with random id."

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/post_orig", methods=['POST', 'GET'])
def post_orig():
    if flask.request.method == 'POST':
        file = flask.request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                   filename))
            return flask.redirect(flask.url_for('get_sound',
                                    id=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
    
