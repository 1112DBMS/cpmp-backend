import uuid
import sql

def CreateSession():
    return uuid.uuid4().hex

def Session2User(session):
    return sql.session_to_user(session)

def bind(session, user):
    sql.bind_user_to_session(session, user)
    return

def unbind(session):
    sql.unbind_user_and_session(session)
    return
