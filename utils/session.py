from uuid import uuid4

import utils.sql as sql

def CreateSession():
    session = str(uuid4())
    sql.add_new_session(session)
    return session

def check_exist(session):
    return sql.session_exist(session)

def Session2User(session):
    return sql.get_user_by_session(session)["UserID"]

def bind(session, user):
    return sql.update_session_user(session, user)

def unbind(session):
    return sql.update_session_user(session, None)
