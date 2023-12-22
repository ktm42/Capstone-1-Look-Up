from flask_sqlalchemy import SQLAlchemy 
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt ()

def connect_db(app):
    """Connects to database"""

    db.app = app
    db.init_app(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key= True, nullable = False, unique = True, autoincrement = True)
    first_name = db.Column(db.Text, nullable = False)
    last_name = db.Column(db.Text, nullable = False)
    username = db.Column(db.Text, nullable = False, unique = True)
    password = db.Column(db.Text, nullable = False)
    base_city = db.Column(db.String(3))

    @classmethod
    def register(cls, first_name, last_name, username, password):
        """Registers the user with a hashed password and returns the user"""
        
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode('utf8')

        registration = User(first_name=first_name, last_name=last_name, username=username, password=hashed_utf8)
        db.session.add(registration)
        db.session.commit()

        return registration

    @classmethod
    def authenticate(cls, username, password):
        """Validates user exists and password is correct. Returns user if valid; else returns false"""

        u = cls.query.filter_by(username=username).first()
        if u:
            print(f'Stored hashed password: {user.password}')
            if bcrypt.check_password_hash(user.password, password):
                print("Authentication successful")
                return user
            else:
                print("Password does not match")
        else:
            print('User not found')
        return False 
   

class Destination(db.Model):
    __tablename__='destinations'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    destination = db.Column(db.Text, nullable = False)
    iata_code = db.Column(db.Text, nullable = False)
    top_price = db.Column(db.Float, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable = False)
    user = db.relationship('User', backref = 'destinations')

    @classmethod
    def add_destinations(cls, destination, iata_code, price, user):
        new_destination = cls(
            destination = destination_name,
            top_price = price,
            iata_code = iata_code,
            user = user
        )

        db.session.add(new_destination)
        db.session.commit()