from flask import Flask, request, redirect
from spotipy import oauth2
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
                 'id=2fb54226ea3f4a748b823a0ce06704c2&response_type='
                 'code&redirect_uri=http://localhost/index&'
                 'scope=user-read-private%20user-read-email&state=34fFs29kd09')

@app.route('/index')
def callback():
    params = {'grant_type': "authorization_code", 'code': request.args.get('code'), 'redirect_uri':
        'http://localhost/index',"client_id": '2fb54226ea3f4a748b823a0ce06704c2', "client_secret":'5f57b22c53294d54befc2dd5667c1268' }
    b64Val = base64.urlsafe_b64encode(b"2fb54226ea3f4a748b823a0ce06704c2:5f57b22c53294d54befc2dd5667c1268")
    token = requests.post('https://accounts.spotify.com/api/token', headers={"Content-type": "application/x-www-form-urlencoded"},params=params)
    print(token.json())

    return 'lol'



if __name__ == '__main__':
    app.run()
