from werkzeug.wrappers import Request, Response
from datetime import datetime, timedelta
import json
from apscheduler.schedulers.background import BackgroundScheduler

from utils.session import CreateSession, Session2User, check_exist
from utils.constant import *

access_count = {}

def clear_access_cnt():
    global access_count
    access_count = {}
    return

sched = BackgroundScheduler(daemon=True)
sched.add_job(clear_access_cnt, 'interval', seconds=PERIOD)
sched.start()

class middleware():
    '''
    Simple WSGI middleware
    '''

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        
        request = Request(environ)

        whitelist = ["/api/login", "/api/500"]

        print("referrer:", request.referrer)
        print("URL:", request.root_url[:-1]+request.path)
        
        if request.path not in whitelist and (not isinstance(request.referrer, str) or not (request.referrer.startswith(SITE) or request.referrer.startswith("https://discord.com/") or request.referrer.startswith("http://localhost:3000/") or request.referrer.startswith("https://dev.andyjjrt.cc/"))):
            j = {
                'data': 'Cross Site Request is not allowed.',
                'error': True
            }
            res = Response(json.dumps(j), mimetype= 'application/json', status=400)
            return res(environ, start_response)

        try:
            SessionID = request.cookies['Session']
            if not check_exist(SessionID):
                raise KeyError("Generate new session.")
        except KeyError:
            #   No session specified. Create one.
            if request.path != "/api/profile":
                j = {
                    'data': '401 Unauthorized.',
                    'error': True
                }
                res = Response(json.dumps(j), mimetype= 'application/json', status=401)
                return res(environ, start_response)

            SessionID = CreateSession()
            access_count[SessionID] = 1
            
            environ['session'] = SessionID
            environ['user'] = None
            

            def set_session_response(status, response_headers, exc_info=None):
                response_headers.append(
                    (
                        "Set-Cookie",
                        "Session=%s; expires=%s; HttpOnly; Path=/; SameSite=Lax" % 
                            (environ['session'], (datetime.utcnow()+timedelta(days=365)).strftime("%a, %d %b %Y %T GMT"))
                    )
                )

                return start_response(status, response_headers, exc_info)

            return self.app(environ, set_session_response)

        if SessionID not in access_count:
            access_count[SessionID] = 1
        elif access_count[SessionID] >= REQUEST_PERIOD_THRESH:
            j = {
                'data': '429 Too Many Requests',
                'error': True
            }
            res = Response(json.dumps(j), mimetype= 'application/json', status=429)
            return res(environ, start_response)
        else:
            access_count[SessionID] += 1

        userID = Session2User(SessionID)
        
        environ['session'] = SessionID
        environ['user'] = userID

        return self.app(environ, start_response)
