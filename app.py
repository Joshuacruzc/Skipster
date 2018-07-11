from flask import Flask, request, redirect, render_template, url_for
import requests, base64
from SpotifyClient import *
import json
import ast
import os
from flask_sqlalchemy import SQLAlchemy
from models import Host

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route('/', methods=['GET', 'POST'])
def initial():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method =='GET':
        return render_template('register.html')
    if request.method == 'POST':
        return get_token()

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('dashboard'))
    return render_template('login.html', error=error)


@app.route('/dashnoard/<negocio_id>')
def dashboard(negocio_id):
    return render_template('dashboard.html', user = negocio_id)

@app.route('/index')
def callback():
    params = {'grant_type': "authorization_code", 'code': request.args.get('code'), 'redirect_uri':
        'http://localhost/index',"client_id": '2fb54226ea3f4a748b823a0ce06704c2', "client_secret":'5f57b22c53294d54befc2dd5667c1268' }
    b64Val = base64.urlsafe_b64encode(b"2fb54226ea3f4a748b823a0ce06704c2:5f57b22c53294d54befc2dd5667c1268")
    response = requests.post('https://accounts.spotify.com/api/token', headers={"Content-type": "application/x-www-form-urlencoded"}, params=params)

    dict = ast.literal_eval(response.text)
    return create_playlist(dict['access_token'], '12152455838', 'Hola Alberto').content


if __name__ == '__main__':
    app.run()
