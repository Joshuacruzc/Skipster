from skipster import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

HostUser_table = db.Table('HostUser',
                          db.Column('host_id', db.Integer, db.ForeignKey('host.id'), nullable=False),
                          db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
                          db.PrimaryKeyConstraint('host_id', 'user_id'))
class Host(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    playlists = db.relationship('Playlist', backref='player', lazy=True)
    users = db.relationship('User', backref='host', secondary='HostUser')

    def __repr__(self):
        return f"Host('{self.name}')"

class User(db.Model, UserMixin):
    id = db.Column('id', db.Integer, primary_key=True)
    username = db.Column( db.String(20), unique=True, nullable=False)
    password = db.Column( db.String(60), nullable=False)
    email = db.Column( db.String(50), unique=True)
    profile_picture = db.Column(db.String(20), nullable = False, default = 'default.jpg')
    registered_on = db.Column(db.DateTime, nullable= False, default=datetime.utcnow)
    hosts = db.relationship('Host', backref='user', secondary='HostUser')
    spotify_id = db.Column(db.String(150), nullable=True)
    refresh_token =db.Column(db.String(300), nullable =True )

    def __repr__(self):
        return f"User('{self.username}')"


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    host_id = db.Column(db.Integer, db.ForeignKey('host.id'), nullable=False)
    spotify_uri = db.Column(db.String(150), nullable=True)
    def __repr__(self):
        return f"Playlist('{self.name}')"
