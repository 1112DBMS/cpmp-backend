from dotenv import load_dotenv
import os

load_dotenv()

SITE = os.getenv('SITE')
API_ENDPOINT = "https://discord.com/api"

#OAUTH_URL = SITE + "/oauthCallback"
OAUTH_URL = SITE + "/api/oauth"

AUTH_URL = "https://discord.com/oauth2/authorize"
TOKEN_URL = API_ENDPOINT + "/oauth2/token"
REVOKE_TOKEN_URL = API_ENDPOINT + "/oauth2/token/revoke"

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

SONG_FOLDER = os.getenv('SONG_FOLDER')
PIC_FOLDER = os.getenv('PIC_FOLDER')

WORKERS = 100
