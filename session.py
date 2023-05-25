from uuid import uuid4
import sql
from sql import sql_client

def CreateSession():
    session = str(uuid4())
    client = sql_client()
    client.add_new_session(session)
    client.close()
    return session

def Session2User(session):
    client = sql_client()
    result = client.get_user_by_session(session)
    client.close()
    return result["UserID"]
    #return sql.session_to_user(session)

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
