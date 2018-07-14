from flask import render_template, url_for, flash, redirect
from skipster.forms import RegistrationForm, LoginForm
from skipster import app, db, bcrypt
from skipster.models import User, Host, Playlist
from flask_login import login_user, current_user, logout_user, login_required

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
        flash("Your account has been created succesfully", 'success')
        return  redirect(url_for('login'))
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
            login_user(user, form.remember.data)
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


# @app.route('/index')
# def callback():
#     params = {'grant_type': "authorization_code", 'code': request.args.get('code'), 'redirect_uri':
#         'http://localhost/index',"client_id": '2fb54226ea3f4a748b823a0ce06704c2', "client_secret":'5f57b22c53294d54befc2dd5667c1268' }
#     b64Val = base64.urlsafe_b64encode(b"2fb54226ea3f4a748b823a0ce06704c2:5f57b22c53294d54befc2dd5667c1268")
#     response = requests.post('https://accounts.spotify.com/api/token', headers={"Content-type": "application/x-www-form-urlencoded"}, params=params)
#
#     dict = ast.literal_eval(response.text)
#     return create_playlist(dict['access_token'], '12152455838', 'Hola Alberto').content
