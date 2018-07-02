from flask import Flask, request, redirect
import spotipy
from spotipy import util
import urllib

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def initial():
    pass

@app.route('/register', methods = ['GET'])
def register():
    return redirect('https://accounts.spotify.com/authorize/?client_'
                 'id=e0147040c0e24397a075519bb718324d&response_type='
                 'code&redirect_uri=http://localhost:5000/index&'
                 'scope=user-read-private%20user-read-email&state=34fFs29kd09')

@app.route('/index')
def callback():
    params = urllib.urlencode({'grant_type':"authorization_code", 'code': request.args.get('code'), 'redirect_uri':
        'http:localhost:5000/index'})
    token = urllib.urlopen("https://accounts.spotify.com/api/token", params)
    print(token)

    return str(token) + 'lol'



if __name__ == '__main__':
    app.run()
