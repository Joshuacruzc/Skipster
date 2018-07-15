import requests, base64
from flask import redirect
import json
import ast

client_id = "e0147040c0e24397a075519bb718324d"
client_secret = '597c98f23fec464896e87e9e87c26cff'
scopes = "user-read-private"
response_type = 'code'
redirect_uri = 'http://localhost:5000/callback'

def spotify_authorize():
    url = "https://accounts.spotify.com/authorize/?client_id=%s&response_type=code&redirect_uri=%s&scope=user-read-private&state=34fFs29kd09" % (client_id, redirect_uri)
    return url

def code_for_token(request):
    params = {'grant_type': "authorization_code", 'code': request.args.get('code'), 'redirect_uri':
        redirect_uri, "client_id": client_id, "client_secret": client_secret}
    response = requests.post('https://accounts.spotify.com/api/token',
                             headers={"Content-type": "application/x-www-form-urlencoded"}, params=params)
    dict = json.loads(response.text)
    access_token = dict['access_token']
    return access_token

def get_user_profile(token):
    url = 'https://api.spotify.com/v1/me'
    response = requests.get(url, headers={"Authorization": 'Bearer ' + token})
    user_profile = json.loads(response.text)
    return user_profile

def create_playlist(token, user_id, name):
    # Description: Made by skipster, link al website
    url = 'https://api.spotify.com/v1/users/%s/playlists' % user_id
    params = {'name': name, 'description': 'Link al website and promotional gimmicks'}
    response = requests.post(url, headers={"Authorization": 'Bearer ' + token, "Content_type": 'application/json'},
                             data=json.dumps(params))
    return response
