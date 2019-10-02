from flask_handler import *
import webbrowser
import threading
import functools

port = 5000
url = "http://127.0.0.1:{0}".format(port)

if __name__ == '__main__':
    threading.Timer(1, functools.partial( webbrowser.open, url )).start()
    start_flask_application()
