from uuid import uuid4

from utils.sql import sql_client

def CreateSession():
    session = str(uuid4())
    client = sql_client()
    client.add_new_session(session)
    client.close()
    return session

def check_exist(session):
    client = sql_client()
    result = client.session_exist(session)
    client.close()
    return result

def Session2User(session):
    client = sql_client()
    result = client.get_user_by_session(session)
    client.close()
    return result["UserID"]

def bind(session, user):
    client = sql_client()
    client.update_session_user(session, user)
    client.close()
    return

def unbind(session):
    client = sql_client()
    client.update_session_user(session, None)
    client.close()
    return
