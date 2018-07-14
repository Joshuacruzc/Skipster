import requests, base64
from flask import redirect
import json



def get_token():
    return redirect('https://accounts.spotify.com/authorize/?client_'
             'id=2fb54226ea3f4a748b823a0ce06704c2&response_type='
             'code&redirect_uri=http://localhost/index&'
             'scope=playlist-modify-public%20user-read-email&state=34fFs29kd09')

def create_playlist(token, user_id, name):
    #Description: Made by skipster, link al website

    url = 'https://api.spotify.com/v1/users/%s/playlists' % user_id
    params = {'name': name, 'description': 'Link al website and promotional gimmicks'}
    response = requests.post(url, headers={"Authorization": 'Bearer ' + token, "Content_type": 'application/json'},
                             data=json.dumps(params))
    return response
