import json

import requests
from flask import render_template, url_for, flash, redirect, request, jsonify
from skipster.forms import RegistrationForm, LoginForm, HostForm
from skipster import app, db, bcrypt
from skipster.models import User, Host, Playlist, Skipster, Track
from flask_login import login_user, current_user, logout_user, login_required
from skipster.SpotifyClient import code_for_token, refresh_access_token, create_playlist, spotify_authorize_url, \
    get_user_profile, search_spotify, add_tracks_to_playlist, clean_track_json, get_playlist_tracks


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Your account has been created successfully", 'success')
        return redirect(url_for('account'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('account'))
        else:
            flash('Login unsuccessful. Please check login information', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/account')
@login_required
def account():
    return render_template('account.html',user=current_user)


@app.route('/register_host/', methods=['GET', 'POST'])
@login_required
def register_host():
    form = HostForm()
    if form.validate_on_submit():
        host = Host(name=form.host.data)
        db.session.add(host)
        db.session.commit()
        user = User.query.get(current_user.id)
        host.users.append(user)
        playlist = create_playlist(form.host.data)
        playlist = Playlist(name=form.playlist.data, description=playlist['description'], host_id=host.id,
                            uri=playlist['id'])
        db.session.add(playlist)
        db.session.commit()
        flash("Your Host has been created successfully", 'success')
        return redirect(url_for('dashboard', host_id=host.id))
    return render_template('register_host.html', form=form)


@app.route('/add_tracks/<playlist_id>', methods=['GET', 'POST'])
# @login_required
def add_tracks(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    if playlist:
        if current_user in playlist.host.users:
            return render_template('add_tracks.html',playlist=playlist)


@app.route('/search_tracks', methods=['POST'])
def search_tracks():
    dict = request.form
    search_result = search_spotify(dict['query'])
    tracks = clean_track_json(search_result)
    return jsonify(tracks)


@app.route('/add_this_track', methods=['POST'])
def add_this_track():
    dict = request.form
    playlist = Playlist.query.get(dict['playlist_id'])
    track = Track.query.filter_by(uri=dict['uri'])
    if track.count() > 0:
        if track[0] not in playlist.tracks:
            result = add_tracks_to_playlist(playlist.uri, [track[0]])
            if result == 201:
                playlist.tracks.append(track[0])
                db.session.commit()
            # TODO Implement error legs in case track cannot be added in spotify
            return '%s successfully added to playlist' % track[0].name
        else:
            return 'Track %s is already in playlist' % track[0].name
    else:
        track = Track(uri=dict['uri'],
                      name=dict['name'],
                      artist=dict['artist'],
                      album=dict['album'],
                      artwork=dict['artwork'])
        result = add_tracks_to_playlist(playlist.uri, [track])
        if result == 201:
            db.session.add(track)
            playlist.tracks.append(track)
            db.session.commit()
        return '%s successfully added to playlist' % track.name


@app.route('/remove_track', methods=['POST'])
def remove_track():
    dict = request.form
    playlist = Playlist.query.get(dict['playlist_id'])
    track = Track.query.filter_by(uri=dict['uri']).first()
    playlist.tracks.remove(track)
    db.session.commit()
    return '%s successfully removed from playlist' % track[0].name


@app.route('/dashboard/<host_id>')
@login_required
def dashboard(host_id):
    host = Host.query.get(host_id)
    if host:
        if current_user in host.users:
            return render_template('dashboard.html', host=host)
        else:
            flash(f'{current_user.username} has no permission to access this host.', 'danger')
            return redirect(url_for('index'))
    else:
        flash(f'Host with Host ID: "{host_id}" does not exist or has been removed', 'danger')
        return redirect(url_for('index'))

@app.route('/spotify_authorize')
def auth():
    return redirect(spotify_authorize_url)

@app.route('/test')
def test_route():
    tracks = get_playlist_tracks(Playlist.query.all()[0].uri)
    #tracks = clean_track_json(tracks)
    return tracks


@app.route('/skip/<host_id>')
def skip(host_id):
    # interface for voting and suggesting songs
    host = Host.query.get(host_id)
    playlist = host.playlists[0]
    tracks = playlist.tracks
    return render_template('skip.html', playlist=playlist)

@app.route('/join_host/<host_id>')
def join_host(host_id):
    # join host using special code
    pass


@app.route('/callback')
def callback():
    access_token, refresh_token = code_for_token(request)
    json = get_user_profile(access_token)
    skipster = Skipster(access_token=access_token, refresh_token=refresh_token, uri=json['id'])
    db.session.add(skipster)
    db.session.commit()
    return redirect(url_for('account'))
