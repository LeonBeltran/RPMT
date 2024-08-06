from rpmt import app
from waitress import serve
import webbrowser
import threading

def open_browser():
    webbrowser.open_new('http://127.0.0.1:8080')  # Replace with your desired address

if __name__ == '__main__':
    threading.Timer(1, open_browser).start()  # Open browser after 1 second
    serve(app, host="0.0.0.0", port=8080)