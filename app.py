from flask import Flask
import spotipy

app = Flask(__name__)


@app.route('/')
def initial():
    if request.method == 'GET:'
        return 'Skipster \nGive us access to your account :)'


if __name__ == '__main__':
    app.run()
