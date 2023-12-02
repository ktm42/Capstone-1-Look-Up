from flask_sqlalchemy import SQLAlchemy 
from flask_bcrypt import Bcrypt 

db = SQLAlchemy()
bcypt = Bcrypt ()

def connect_db(app):
    """Connects to database"""

    db.app = init_app(app)

class Register(db.model):
    __tablename__ = 'registration'

    id = db.Column(db.Text, nullable = False, unique = True, autoincrement = True)
    first_name = db.Column(db.Text, nullable = False)
    last_name = db.Column(db.Text, nullable = False)
    address = db.Column(db.TextAreaField, nullable=False)
    username = db.Column(db.Text, nullable = False, unique = True)
    password = db.Column(db.Text, nullable = False)

    @classmethod
    def register(cls, username, password):
        """Registers the user with a hashed password and returns the user"""
        
        hashed = bcrypt.generate_password_hash(pwd)
        hashed_utf8 = hashed.decode('utf8')
        return cls(username=username, password=hashed_utf8)

class User(db.Model):
    __tablename__= 'users'

    id = db.Column(db.Text, nullable = False, unique = True, auotincrement = True) 
    username = db.Column(db.Text, nullable = False, unique = True)
    password = db.Column(db.Text, nullable = False)

    @classmethod
    def authenticate(cls, username, password):
        """Validates user exists and password is correct. Returns user if valid; else returns false"""

        u = User.query.filter_by(username=username).first()
        if u and bcrypt.check_password_hash(u.password, pwd):
            return u
        else:
            return False

class Coordinates(db.Model):
    __tablename__='coordinates'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    lng = db.Column(db.Integer, nullable = False)
    lat = db.Column(db.Integer, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref = 'coordinates')

