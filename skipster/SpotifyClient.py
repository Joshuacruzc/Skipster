from urllib import parse
import requests
import json

from skipster import db
from skipster.models import Skipster, Track

client_id = "e0147040c0e24397a075519bb718324d"
client_secret = '597c98f23fec464896e87e9e87c26cff'
auth = (client_id,client_secret)
scopes = "user-read-private user-top-read playlist-modify-public"
scopes = parse.quote(scopes.encode('utf-8'))
response_type = 'code'
redirect_uri = 'http://localhost:5000/callback'
spotify_authorize_url = "https://accounts.spotify.com/authorize/?client_id=%s&response_type=code&redirect_uri=%s&scope=%s&state=34fFs29kd09&show_dialog=true" % (client_id, redirect_uri, scopes)


def code_for_token(request):
    url = 'https://accounts.spotify.com/api/token'
    params = {'grant_type': "authorization_code", 'code': request.args.get('code'), 'redirect_uri':  redirect_uri}
    response = requests.post(url, auth=auth, data=params)
    dict = json.loads(response.text)
    access_token = dict['access_token']
    refresh_token = dict['refresh_token']
    return access_token, refresh_token


def refresh_access_token(host_id=None):
    localSkipster = Skipster.query.all()[0]
    refresh_token = localSkipster.refresh_token
    url = 'https://accounts.spotify.com/api/token'
    params = {'grant_type': "refresh_token", 'refresh_token': refresh_token}
    response = requests.post(url, data = params, auth=auth)
    dict = json.loads(response.text)
    localSkipster.access_token = dict['access_token']
    db.session.commit()


def get_user_profile(token):
    url = 'https://api.spotify.com/v1/me'
    response = requests.get(url, headers={"Authorization": 'Bearer ' + token})
    user_profile = json.loads(response.text)
    return user_profile


def create_playlist(name):
    # Description: Made by skipster, link al website
    refresh_access_token()
    localSkipster = Skipster.query.all()[0]
    url = 'https://api.spotify.com/v1/users/%s/playlists' % localSkipster.uri
    params = {'name': name, 'description': 'Link al website and promotional gimmicks'}
    response = requests.post(url, headers={"Authorization": 'Bearer ' + localSkipster.access_token, "Content_type": 'application/json'}, data=json.dumps(params))
    playlist = json.loads(response.text)
    return playlist

def search_spotify(search_text):
    refresh_access_token()
    localSkipster = Skipster.query.all()[0]
    url = 'https://api.spotify.com/v1/search'
    params = {'q': search_text, 'type': 'track'}
    response = requests.get(url,headers={"Authorization": 'Bearer ' + localSkipster.access_token}, params=params )
    result = json.loads(response.text)
    return result

def add_tracks_to_playlist(playlist_id, tracks):
    refresh_access_token()
    localSkipster = Skipster.query.all()[0]
    url = "https://api.spotify.com/v1/playlists/%s/tracks" % playlist_id
    params = {'uris': track.uri for track in tracks}
    response = requests.post(url, headers={"Authorization": 'Bearer ' + localSkipster.access_token,
                                         "Content_type": 'application/json'}, params=params)
    return response.status_code

def remove_tracks_from_playlist(playlist_id, tracks):
    refresh_access_token()
    localSkipster = Skipster.query.all()[0]
    url = "https://api.spotify.com/v1/playlists/%s/tracks" % playlist_id
    params = {'tracks':[{'uri': track.uri for track in tracks}]}
    response = requests.delete(url, headers={"Authorization": 'Bearer ' + localSkipster.access_token,
                                           "Content_type": 'application/json'}, params=params)
    return response.status_code

def clean_track_json(json):
    tracks = list()
    for track in json['tracks']['items']:
        uri = track['uri']
        name = track['name']
        artist = track['artists'][0]['name']
        album =  track['album']['name']
        artwork =  track['album']['images'][0]['url']
        tracks.append({'uri':uri, 'name':name, 'artist':artist, 'album':album, 'artwork':artwork})
    return tracks

def get_playlist_tracks(playlist_id):
    refresh_access_token()
    localSkipster = Skipster.query.all()[0]
    url = "https://api.spotify.com/v1/playlists/%s/tracks" % playlist_id
    response = requests.get(url,headers={"Authorization": 'Bearer ' + localSkipster.access_token})
    tracks = json.loads(response.text)
    return response.text