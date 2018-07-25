import requests
from flask import render_template, url_for, flash, redirect,request
from skipster.forms import RegistrationForm, LoginForm, HostForm
from skipster import app, db, bcrypt
from skipster.models import User, Host, Playlist
from flask_login import login_user, current_user, logout_user, login_required
from skipster.SpotifyClient import spotify_authorize, code_for_token, get_user_profile, refresh_access_token, \
    get_user_top_tracks, create_playlist


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
        if form.spotify_link.data == True:
           url =  spotify_authorize()
        flash("Your account has been created successfully", 'success')
        return  redirect(url)
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
    user = current_user
    top_tracks = get_user_top_tracks(user)
    example_url =  top_tracks['items'][1]['album']['images'][0]['url']
    return render_template('account.html', user=current_user, example_url=example_url)


@app.route('/register_host/', methods=['GET', 'POST'])
@login_required
def register_host():
    top_tracks = get_user_top_tracks(current_user)
    form = HostForm()
    if form.validate_on_submit():
        host = Host(name=form.host.data)
        db.session.add(host)
        db.session.commit()
        host = Host.query.get(host.id)
        user = User.query.get(current_user.id)
        host.users.append(user)
        playlist = create_playlist(current_user, form.host.data)
        playlist = Playlist(name = form.playlist.data, description=playlist['description'], host_id= host.id, spotify_uri= playlist['id'])
        db.session.add(playlist)
        db.session.commit()
        flash("Your playlist has been created successfully", 'success')
    return render_template('register_host.html', form= form, spotify_data = top_tracks)

# @app.route('/add_tracks/<playlist_id>', methods=['GET', 'POST'])
# @login_required
# def add_tracks(playlist_id):
#     playlist = Playlist.query.get(playlist_id)
#     if playlist:
#         if current_user in playlist
@app.route('/dashboard/<host_id>')
@login_required
def dashboard(host_id):
    host = Host.query.get(host_id)
    if host:
        if current_user in host.user:
            return render_template('dashboard.html', host=host)
        else:
            flash(f'{current_user.username} has no permission to access this host.', 'danger')
            return redirect(url_for('index'))
    else:
        flash(f'Host with Host ID: "{host_id}" does not exist or has been removed', 'danger')
        return redirect(url_for('index'))

@app.route('/callback')
def callback():
    user = current_user
    access_token, refresh_token = code_for_token(request)
    user_profile = get_user_profile(access_token)
    user.spotify_id = user_profile['id']
    user.refresh_token = refresh_token
    db.session.commit()
    return redirect(url_for('account'))
    #
    # return create_playlist(dict['access_token'], '12152455838', 'Hola Alberto').content
