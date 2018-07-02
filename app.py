from flask import Flask, request, redirect
import spotipy
from spotipy import util
import urllib
from urllib import request as urlrequest, parse
import requests, base64

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
    params = {'grant_type': "authorization_code", 'code': request.args.get('code'), 'redirect_uri':
        'http:localhost:5000/index',}
    b64Val = base64.b64encode(b"e0147040c0e24397a075519bb718324:597c98f23fec464896e87e9e87c26cff")
    token = requests.post("https://accounts.spotify.com/api/token", headers={"Authorization": "Basic %s" % b64Val},params=params)
    print(token)

    return 'lol'



if __name__ == '__main__':
    app.run()
