import mysql.connector
from constant import SQL_USER, SQL_PASSWORD, SQL_HOST, SQL_PORT, SQL_DB

session_sql = {}
user_sql = {}
uploader_sql = {}
song_sql = {}

class sql_client:

    def __init__(self, user=SQL_USER, password=SQL_PASSWORD, host=SQL_HOST, port=SQL_PORT, database=SQL_DB):
        self._conn = mysql.connector.connect(
            host = host,
            port=port,
            user = user,
            password = password,
            database = database,
        )
        self._cursor = self._conn.cursor()

    def close(self):
        self._cursor.close()
        self._conn.close()
        return

    def add_new_user(self, ID, Name, email, photoID, AccessToken, RefreshToken):
        try:
            self._cursor.execute(
                'INSERT INTO User (UserID, UserName, Email, Photo, AccessToken, RefreshToken) VALUES (%s,%s,%s,%s,%s,%s)',
                (ID, Name, email, photoID, AccessToken, RefreshToken)
            )
            self._conn.commit()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()

        return

    def add_new_session(self, session):
        try:
            self._cursor.execute(
                'INSERT INTO Session (SessionID, UserID) VALUES (%s,%s)',
                (session, None)
            )
            self._conn.commit()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()

        return

    def add_new_song(self, SongID, URL, Platform, Title, UploaderID, ThumbnailID, Likecount, Length, Download):
        try:
            self._cursor.execute(
                'INSERT INTO Song (SongID, OrigURL, Platform, Title, Uploader, SThumbnail, LikeCount, Length, Download) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                (SongID, URL, Platform, Title, UploaderID, ThumbnailID, Likecount, Length, Download)
            )
            self._conn.commit()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()

        return

    def add_new_picture(self, UUID, Time, sizeX, sizeY):
        try:
            self._cursor.execute(
                'INSERT INTO Picture (PicID, Time, SizeX, SizeY) VALUES (%s,%s,%s,%s)',
                (UUID, Time, sizeX, sizeY)
            )
            self._conn.commit()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()

        return

    def add_new_uploader(self, ID, URL, OrigID, Name, Platform, Photo, Description):
        try:
            self._cursor.execute(
                'INSERT INTO Uploader (UploaderID, URL, OrigID, Name, UPlatform, Description, UPhoto) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                (ID, URL, OrigID, Name, Platform, Description, Photo)
            )
            self._conn.commit()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()
            print(e)

        return

    def user_exist(self, UserID):
        try:
            self._cursor.execute(
                'SELECT EXISTS (SELECT * FROM User WHERE UserID = %s) AS is_exists',
                (UserID,)
            )
            result = self._cursor.fetchall()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()
        
        if result[0][0] == 1:
            return True
        else:
            return False

    def session_exist(self, SessionID):
        try:
            self._cursor.execute(
                'SELECT EXISTS (SELECT * FROM Session WHERE SessionID = %s) AS is_exists',
                (SessionID,)
            )
            result = self._cursor.fetchall()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()
        
        if result[0][0] == 1:
            return True
        else:
            return False

    def song_exist(self, SongID):
        try:
            self._cursor.execute(
                'SELECT EXISTS (SELECT * FROM Song WHERE SongID = %s) AS is_exists',
                (SongID,)
            )
            result = self._cursor.fetchall()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()
        
        if result[0][0] == 1:
            return True
        else:
            return False

    def uploader_exist(self, UploaderID):
        try:
            self._cursor.execute(
                'SELECT EXISTS (SELECT * FROM Uploader WHERE UploaderID = %s) AS is_exists',
                (UploaderID,)
            )
            result = self._cursor.fetchall()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()
        
        if result[0][0] == 1:
            return True
        else:
            return False

    def picture_exist(self, PicID):
        try:
            self._cursor.execute(
                'SELECT EXISTS (SELECT * FROM Picture WHERE PicID = %s) AS is_exists',
                (PicID,)
            )
            result = self._cursor.fetchall()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()

        if result[0][0] == 1:
            return True
        else:
            return False
        
    def picture_user_using(self, PicID):
        try:
            self._cursor.execute(
                'SELECT EXISTS (SELECT * FROM User WHERE Photo = %s) AS is_exists',
                (PicID,)
            )
            result = self._cursor.fetchall()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()

        if result[0][0] == 1:
            return True
        else:
            return False
        
    def user_song_like(self, UserID, SongID):
        try:
            self._cursor.execute(
                'SELECT EXISTS (SELECT * FROM Like WHERE LUser = %s AND LSong = %s) AS is_exists',
                (UserID, SongID)
            )
            result = self._cursor.fetchall()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()

        if result[0][0] == 1:
            return True
        else:
            return False
        
    def get_user_by_ID(self, UserID):
        try:
            self._cursor.execute(
                'SELECT * FROM User WHERE UserID = %s',
                (UserID,)
            )
            result = self._cursor.fetchall()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()
        
        data = {
            "UserID": result[0][0],
            "UserName": result[0][1],
            "Email": result[0][2],
            "Photo": result[0][3],
            "AccessToken": result[0][4],
            "RefreshToken": result[0][5]
        }
        return data

    def get_user_by_session(self, session):
        try:
            self._cursor.execute(
                'SELECT * FROM Session WHERE SessionID = %s',
                (session,)
            )
            result = self._cursor.fetchall()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()
        
        data = {
            "UserID": result[0][1]
        }
        return data

    def get_song_by_ID(self, SongID):
        try:
            self._cursor.execute(
                'SELECT * FROM Song WHERE SongID = %s',
                (SongID,)
            )
            result = self._cursor.fetchall()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()
        
        data = {
            "SongID": result[0][0],
            "OrigURL": result[0][1],
            "Platform": result[0][2],
            "Title": result[0][3],
            "Uploader": result[0][4],
            "Thumbnail": result[0][5],
            "LikeCount": result[0][6],
            "Length": result[0][7],
            "Download": result[0][8]
        }
        return data

    def get_uploader_by_ID(self, UploaderID):
        try:
            self._cursor.execute(
                'SELECT * FROM Uploader WHERE UploaderID = %s',
                (UploaderID,)
            )
            result = self._cursor.fetchall()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()
        
        data = {
            "UploaderID": result[0][0],
            "URL": result[0][1],
            "OrigID": result[0][2],
            "Name": result[0][3],
            "Platform": result[0][4],
            "Description": result[0][5],
            "Photo": result[0][5]
        }
        return data

    def get_all_uploader(self):
        try:
            self._cursor.execute(
                'SELECT * FROM Uploader'
            )
            results = self._cursor.fetchall()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()
            print(e)

        return_data = []
        for result in results:
            data = {
                "UploaderID": result[0],
                "URL": result[1],
                "OrigID": result[2],
                "Name": result[3],
                "Platform": result[4],
                "Description": result[5],
                "Photo": result[5]
            }
            return_data.append(data)
        return return_data

    def get_picture_by_ID(self, PicID):
        try:
            self._cursor.execute(
                'SELECT * FROM Picture WHERE PicID = %s',
                (PicID,)
            )
            result = self._cursor.fetchall()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()
        
        data = {
            "PicID": result[0][0],
            "Time": result[0][1],
            "SizeX": result[0][2],
            "SizeY": result[0][3],
        }
        return data

    def update_session_user(self, session, user):
        try:
            self._cursor.execute(
                'UPDATE Session SET UserID = %s WHERE SessionID = %s',
                (user, session)
            )
            self._conn.commit()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()
            print(e)

        return

    def update_song_download(self, SongID, download):
        try:
            self._cursor.execute(
                'UPDATE Song SET Download = %s WHERE SongID = %s',
                (download, SongID)
            )
            self._conn.commit()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()
            print(e)

        return

    def update_user_photo(self, UserID, PicID):
        try:
            self._cursor.execute(
                'UPDATE User SET Photo = %s WHERE UserID = %s',
                (PicID, UserID)
            )
            self._conn.commit()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()
            print(e)

        return

    def update_user_email(self, UserID, email):
        try:
            self._cursor.execute(
                'UPDATE User SET Email = %s WHERE UserID = %s',
                (email, UserID)
            )
            self._conn.commit()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()
            print(e)

        return

    def update_uploader_description(self, UploaderID, Description):
        try:
            self._cursor.execute(
                'UPDATE Uploader SET Description = %s WHERE UploaderID = %s',
                (Description, UploaderID)
            )
            self._conn.commit()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()
            print(e)

        return

    def delete_picture(self, PicID):
        try:
            self._cursor.execute(
                'DELETE FROM Picture WHERE PicID = %s',
                (PicID,)
            )
            self._conn.commit()
        except Exception as e:
            # Roll back the transaction if any operation failed
            self._conn.rollback()
            print(e)

        return

def update_user_access_token(ID, AccessToken, RefreshToken):
    user_sql[ID]["AccessToken"] = AccessToken
    user_sql[ID]["RefreshToken"] = RefreshToken
    return

def user_like_song_query(UserID, UUID):
    return False
