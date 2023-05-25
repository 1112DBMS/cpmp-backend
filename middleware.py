from werkzeug.wrappers import Request, Response
from session import CreateSession, Session2User
from datetime import datetime, timedelta, timezone
from constant import *
import json

class middleware():
    '''
    Simple WSGI middleware
    '''

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        
        request = Request(environ)

        whitelist = ["/api/login", "/api/500", "/api/download"]

        print("referrer:", request.referrer)
        print("URL:", request.root_url[:-1]+request.path)
        
        if request.path not in whitelist and (not isinstance(request.referrer, str) or not (request.referrer.startswith(SITE) or request.referrer.startswith("https://discord.com/") or request.referrer.startswith("http://localhost:3000/"))):
            j = {
                'data': 'Cross Site Request is not allowed.',
                'error': True
            }
            res = Response(json.dumps(j), mimetype= 'application/json', status=400)
            return res(environ, start_response)

        try:
            SessionID = request.cookies['Session']
            if len(SessionID) != 36:
                raise ValueError("Generate new session.")
        except KeyError:
            #   No session specified. Create one.
            SessionID = CreateSession()
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
        except ValueError:
            print("Old session found:", SessionID)
            #   Old session detected. Unset it.
            SessionID = CreateSession()
            environ['session'] = SessionID
            environ['user'] = None
            

            def set_session_response(status, response_headers, exc_info=None):
                response_headers.append(
                    (
                        "Set-Cookie",
                        "Session=; expires=%s; path=/; SameSite=Lax" % 
                            ((datetime(1970, 1, 1, 0, 0, tzinfo=timezone.utc)).strftime("%a, %d %b %Y %T GMT"),)
                    )
                )

                return start_response(status, response_headers, exc_info)

            return self.app(environ, set_session_response)

        userID = Session2User(SessionID)
        
        environ['session'] = SessionID
        environ['user'] = userID

        return self.app(environ, start_response)
