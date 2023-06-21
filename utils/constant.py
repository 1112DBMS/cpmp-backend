from dotenv import load_dotenv
import os

load_dotenv()

#################################
#                               #
#         load secrets          #
#                               #
#################################

SITE = os.getenv('SITE')
PORT = os.getenv('API_PORT')

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

SONG_FOLDER = os.getenv('SONG_FOLDER')
PIC_FOLDER = os.getenv('PIC_FOLDER')

SQL_HOST = os.getenv('SQL_HOST')
SQL_PORT = os.getenv('SQL_PORT')
SQL_USER = os.getenv('SQL_USER')
SQL_PASSWORD = os.getenv('SQL_PASSWORD')
SQL_DB = os.getenv('SQL_DB')

#################################
#                               #
#          constants            #
#                               #
#################################

API_ENDPOINT = "https://discord.com/api"

TOKEN_URL = API_ENDPOINT + "/oauth2/token"
REVOKE_TOKEN_URL = API_ENDPOINT + "/oauth2/token/revoke"

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_ENDPOINT = "https://api.spotify.com/v1"
SPOTIFY_DOWN_ENDPOINT = "https://api.spotifydown.com"

#################################
#                               #
#            limits             #
#                               #
#################################

WORKERS = 100

REQUEST_PERIOD_THRESH = 30
PERIOD = 60

DOWNLOAD_LENGTH_LIMIT = 3600