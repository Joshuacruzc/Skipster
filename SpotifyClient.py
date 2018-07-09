import requests, base64
from flask import jsonify
import json


def create_playlist(token, user_id, name):
    #Description: Made by skipster, link al website

    url = 'https://api.spotify.com/v1/users/%s/playlists' % user_id
    params = {'name': name, 'description': 'Link al website and promotional gimmicks'}
    response = requests.post(url, headers={"Authorization": 'Bearer ' + token, "Content_type": 'application/json'},
                             data=json.dumps(params))
    return response
