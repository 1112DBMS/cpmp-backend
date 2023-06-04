from server import app
from utils.constant import PORT

if __name__ == '__main__':
    print("Testing environment")
    app.run(host='127.0.0.1', port=PORT)
