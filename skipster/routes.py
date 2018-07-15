import requests
from flask import render_template, url_for, flash, redirect,request
from skipster.forms import RegistrationForm, LoginForm
from skipster import app, db, bcrypt
from skipster.models import User, Host, Playlist
from flask_login import login_user, current_user, logout_user, login_required
from skipster.SpotifyClient import spotify_authorize, code_for_token, get_user_profile


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
        flash("Your account has been created succesfully", 'success')
        return  redirect(url)
    return render_template('register.html', title='Register', form=form)
    # if request.method == 'POST':
    #     return get_token()

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
    return render_template('account.html', user=current_user)

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
    token = code_for_token(request)
    user_profile = get_user_profile(token)
    user = User.query.get(current_user.id)
    user.spotify_id = user_profile['id']
    db.session.commit()
    return redirect(url_for('account'))
    #
    # return create_playlist(dict['access_token'], '12152455838', 'Hola Alberto').content
