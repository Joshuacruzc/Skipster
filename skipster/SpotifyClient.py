from urllib import parse

import requests, base64
from flask import redirect
import json
import ast

client_id = "e0147040c0e24397a075519bb718324d"
client_secret = '597c98f23fec464896e87e9e87c26cff'
auth = (client_id,client_secret)
scopes = "user-read-private user-top-read"
scopes = parse.quote(scopes.encode('utf-8'))
response_type = 'code'
redirect_uri = 'http://localhost:5000/callback'

def spotify_authorize():
    url = "https://accounts.spotify.com/authorize/?client_id=%s&response_type=code&redirect_uri=%s&scope=%s&state=34fFs29kd09&show_dialog=true" % (client_id, redirect_uri, scopes)
    return url

def code_for_token(request):
    url = 'https://accounts.spotify.com/api/token'
    params = {'grant_type': "authorization_code", 'code': request.args.get('code'), 'redirect_uri':  redirect_uri}
    response = requests.post(url, auth=auth, data=params)
    dict = json.loads(response.text)
    access_token = dict['access_token']
    refresh_token = dict['refresh_token']
    return access_token, refresh_token

def refresh_access_token(user):
    url = 'https://accounts.spotify.com/api/token'
    params = {'grant_type': "refresh_token", 'refresh_token': user.refresh_token}
    response = requests.post(url, data = params, auth=auth)
    dict = json.loads(response.text)
    access_token = dict['access_token']
    return access_token

def get_user_profile(token):
    url = 'https://api.spotify.com/v1/me'
    response = requests.get(url, headers={"Authorization": 'Bearer ' + token})
    user_profile = json.loads(response.text)
    return user_profile

def get_user_top_tracks(token):
        url = "https://api.spotify.com/v1/me/top/tracks/?limit=2"
        response = requests.get(url, headers={"Authorization": 'Bearer ' + token})
        top_tracks = json.loads(response.text)
        return top_tracks

def create_playlist(token, user_id, name):
    # Description: Made by skipster, link al website
    url = 'https://api.spotify.com/v1/users/%s/playlists' % user_id
    params = {'name': name, 'description': 'Link al website and promotional gimmicks'}
    response = requests.post(url, headers={"Authorization": 'Bearer ' + token, "Content_type": 'application/json'}, data=json.dumps(params))
    return response


