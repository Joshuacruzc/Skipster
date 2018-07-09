import requests, base64


def create_playlist(token, user_id, name):
    #Description: Made by skipster, link al website

    url = 'https//api.spotify.com/v1/users/%s/playlists' % user_id
    params = {'name': name, 'description': 'Link al website and promotional gimmicks'}
    response = requests.post(url, headers={"Content-type": "application/json", "Authorization": token}, params=params)
    return response
