import json

from flask import render_template, url_for, flash, redirect, request, jsonify
from skipster.forms import RegistrationForm, LoginForm, HostForm
from skipster import app, db, bcrypt
from skipster.models import User, Host, Playlist, Track, PlaylistTrack
from flask_login import login_user, current_user, logout_user, login_required
from skipster.SpotifyClient import code_for_token, refresh_access_token, create_playlist, spotify_authorize_url, \
    get_user_profile, search_spotify, add_tracks_to_playlist, clean_track_json, get_playlist_tracks, \
    remove_tracks_from_playlist


@app.route('/', methods=['GET', 'POST'])
def index():
    # Displays index Page, HTML Template should contain information about the skipster app
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Register a new user (without a link to a spotify account)
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
    # Logs in existing user
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
    # Logs out current user
    logout_user()
    return redirect(url_for('index'))


@app.route('/account')
@login_required
def account():
    # Can contain preference information or spotify profile information for regular users and their hosts
    return render_template('account.html',user=current_user)


@app.route('/register_host', methods=['GET', 'POST'])
@login_required
def register_host():
    # Creates a new host and corresponding playlist, user must be linked to spotify account in order to register a host
    user = current_user
    if user.uri:
        form = HostForm()
        if form.validate_on_submit():
            host = Host(name=form.host.data)
            db.session.add(host)
            db.session.commit()
            user = current_user
            host.users.append(user)
            playlist = create_playlist(form.playlist.data, user)
            playlist = Playlist(name=form.playlist.data, description=playlist['description'], host_id=host.id,
                                uri=playlist['id'])
            db.session.add(playlist)
            db.session.commit()
            flash("Your Host has been created successfully", 'success')
            return redirect(url_for('dashboard', host_id=host.id))
        return render_template('register_host.html', form=form)
    else:
        return redirect(url_for('auth'))

@app.route('/add_tracks/<playlist_id>', methods=['GET', 'POST'])
@login_required
def add_tracks(playlist_id):
    # Displays page where user can vote tracks for a specific Playlist
    playlist = Playlist.query.get(playlist_id)
    if playlist:
        return render_template('add_tracks.html',playlist=playlist)
    else:
        flash('This playlist is not available at the moment')
        return redirect(url_for('index'))


@app.route('/search_tracks', methods=['POST'])
@login_required
def search_tracks():
    # Called using ajax, search for tracks in spotify given a query
    user = current_user
    dict = request.form
    search_result = search_spotify(dict['query'], user)
    tracks = clean_track_json(search_result)
    return jsonify(tracks)


@app.route('/refresh_playlist', methods=['POST'])
@login_required
def refresh_playlist(playlist_id):
    # Refreshes playlist, currently only allows up to 20 songs in the playlist, will add the top 20 with highest
    # affinity and remove the rest from the spotify playlist while keeping the relationship in the database but inactive
    user = current_user
    playlist = Playlist.query.get(playlist_id)
    playlist_tracks = PlaylistTrack.query.filter_by(playlist=playlist_id).order_by('affinity')
    count =20
    add_list = list()
    remove_list = list()
    for track in playlist_tracks:
        count-=1
        if count > 0:
            if not track.is_active:
                track.is_active = True
                add_list.append(Track.query.get(track.track))
        else:
            if track.is_active:
                track.is_active = False
                remove_list.append(Track.query.get(track.track))

    if add_list:
        result = add_tracks_to_playlist(playlist.uri, add_list, user)
    if remove_list:
        remove_tracks_from_playlist(playlist.uri, remove_list, user)
    return ''

@app.route('/add_this_track', methods=['POST'])
def add_this_track():
    # Adds a track directly to playlist (only host owners should access this)
    dict = request.form
    playlist = Playlist.query.get(dict['playlist_id'])
    track = Track.query.filter_by(uri=dict['uri']).first()
    if track:
        if track not in playlist.tracks:
            result = add_tracks_to_playlist(playlist.uri, [track], current_user)
            if result == 201:
                playlist.tracks.append(track)
                db.session.commit()
            # TODO Implement error legs in case track cannot be added in spotify
            return '%s successfully added to playlist' % track.name
        else:
            return 'Track %s is already in playlist' % track.name
    else:
        track = Track(uri=dict['uri'],
                      name=dict['name'],
                      artist=dict['artist'],
                      album=dict['album'],
                      artwork=dict['artwork'])
        result = add_tracks_to_playlist(playlist.uri, [track], current_user)
        if result == 201:
            db.session.add(track)
            playlist.tracks.append(track)
            db.session.commit()
        return '%s successfully added to playlist' % track.name


# TODO finish remove_track endpoint
# @app.route('/remove_track', methods=['POST'])
# #
# def remove_track():
#     dict = request.form
#     playlist = Playlist.query.get(dict['playlist_id'])
#     track = Track.query.filter_by(uri=dict['uri']).first()
#     playlist.tracks.remove(track)
#     db.session.commit()
#     return '%s successfully removed from playlist' % track.name


@app.route('/vote', methods=['POST'])
def vote_for_track():
    # Called using ajax, currently one vote equals +1 affinity
    dict = request.form
    playlist = Playlist.query.get(dict['playlist_id'])
    track = Track.query.filter_by(uri=dict['uri']).first()
    if not track:
        track = Track(uri=dict['uri'],
                      name=dict['name'],
                      artist=dict['artist'],
                      album=dict['album'],
                      artwork=dict['artwork'])

        db.session.add(track)
    if track not in playlist.tracks:
        playlist.tracks.append(track)
    # track = playlist.tracks[-1]
    playlist_track_relationship = PlaylistTrack.query.filter_by(track=track.id, playlist=playlist.id).first()
    playlist_track_relationship.affinity += 1
    db.session.commit()
    refresh_playlist(playlist.id)
    return ''


@app.route('/dashboard/<host_id>')
@login_required
def dashboard(host_id):
    # Shows user's Host's playlists
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
@login_required
def auth():
    # sends you to spotify's oauth endpoint
    return redirect(spotify_authorize_url)


# @app.route('/join_host/<host_id>')
# def join_host(host_id):
#     # join host using special code
#     pass


@app.route('/callback')
def callback():
    # Binds user to spotify account
    user = current_user
    access_token, refresh_token = code_for_token(request)
    json = get_user_profile(access_token)
    user.access_token = access_token
    user.refresh_token = refresh_token
    user.uri = json['id']
    db.session.commit()
    return redirect(url_for('register_host'))
