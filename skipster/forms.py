from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from skipster.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(),Length(min=3, max=20),])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password',
                                     validators =[DataRequired(), EqualTo('password')])
    # spotify_link = BooleanField('Link to Spotify Account?')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('username is already taken')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('An account with this email has already been registered')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=8)])
    # remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class HostForm(FlaskForm):
    host = StringField('Host Name',
                           validators=[DataRequired(), Length(min=3, max=50), ])
    playlist = StringField('Playlist Name',
                           validators=[DataRequired(), Length(min=3, max=50), ])
    submit = SubmitField('Create Playlist')