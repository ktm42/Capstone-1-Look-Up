from flask_sqlalchemy import SQLAlchemy 
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt ()

def connect_db(app):
    """Connects to database"""

    db.app = app
    db.init_app(app)

class Register(db.Model):
    __tablename__ = 'registration'

    id = db.Column(db.Integer, primary_key= True, nullable = False, unique = True, autoincrement = True)
    first_name = db.Column(db.Text, nullable = False)
    last_name = db.Column(db.Text, nullable = False)
    address = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, nullable = False, unique = True)
    password = db.Column(db.Text, nullable = False)

    @classmethod
    def register(cls, first_name, last_name, address, username, password):
        """Registers the user with a hashed password and returns the user"""
        
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode('utf8')

        registration = Register(first_name=first_name, last_name=last_name, address=address, username=username, password=hashed_utf8)
        db.session.add(registration)
        db.session.commit()
       
        user = User(username=username, password=hashed_utf8)
        db.session.add(user)
        db.session.commit()      

        return user

class User(db.Model):
    __tablename__= 'users'

    id = db.Column(db.Integer, primary_key = True, nullable = False, unique = True, autoincrement = True) 
    username = db.Column(db.Text, nullable = False, unique = True)
    password = db.Column(db.Text, nullable = False)
  
    @classmethod
    def authenticate(cls, username, password):
        """Validates user exists and password is correct. Returns user if valid; else returns false"""

        u = cls.query.filter_by(username=username).first()
        if u:
            print(f'Stored hashed password: {u.password}')
            if bcrypt.check_password_hash(u.password, password):
                print("Authentication successful")
                return u
            else:
                print("Password does not match")
        else:
            print('User not found')
        return False

class Coordinates(db.Model):
    __tablename__='coordinates'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    latitude = db.Column(db.Float, nullable = False)
    longitude = db.Column(db.Float, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable = False)
    user = db.relationship('User', backref = 'coordinates')

    @classmethod
    def log_coords(cls, latitude, longitude, user):
         coordinates = Coordinates(latitude=latitude, longitude=longitude, user=user)
         db.session.add(coordinates)
         db.session.commit()