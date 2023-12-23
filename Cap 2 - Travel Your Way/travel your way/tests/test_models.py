import os
import unittest
from flask import Flask
from models import db, User, Destination, connect_db

os.environ['DATABASE_URI'] = "postgresql:///travel_your_way_test"

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        """Set up the test database"""
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'postgresql:///travel_your_way_test')
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['TESTING'] = True
        self.app.config['DEBUG'] = False
        self.app.config['SECRET_KEY'] = 'secret_key'

        with self.app.app_context():
            db.init_app(self.app)
            db.create_all()

    def tearDown(self):
        """Clean up after the test"""
        with self.app.app_context():
            db.drop_all()

    def test_register_user(self):
        """Test user registration"""
        with self.app.app_context():
            user = User.register('John', 'Doe', 'john_doe', 'password')
            db.session.commit()

            self.assertEqual(user.first_name, 'John')
            self.assertEqual(user.last_name, 'Doe')
            self.assertEqual(user.username, 'john_doe')
            self.assertTrue(user.password.startswith('$2b$'))

    def test_authenticate_user(self):
        """Test user authentication"""
        with self.app.app_context():
            User.register('John', 'Doe', 'john_doe', 'password')
            db.session.commit()

            authenticated_user = User.authenticate('john_doe', 'password')
            self.assertIsNotNone(authenticated_user)

            incorrect_password_user = User.authenticate('john_doe', 'wrong_password')
            self.assertFalse(incorrect_password_user)

            non_existing_user = User.authenticate('non_existing_user', 'password')
            self.assertFalse(non_existing_user)

class DestinationModelTestCase(unittest.TestCase):
    def setUp(self):
        """Set up the test environment"""
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'postgresql:///travel_your_way_test')
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['TESTING'] = True
        self.app.config['DEBUG'] = False
        self.app.config['SECRET_KEY'] = 'secret_key'

        with self.app.app_context():
            db.init_app(self.app)
            db.create_all()

    def tearDown(self):
        """Clean up after the test"""
        with self.app.app_context():
            db.drop_all()

    def test_add_destinations(self):
        """Test adding a destination"""
        with self.app.app_context():
            user = User.register('John', 'Doe', 'john_doe', 'password')
            db.session.commit()

            destination = Destination.add_destinations('Paris', 'CDG', 500, user)
            db.session.commit()

            self.assertEqual(destination.destination, 'Paris')
            self.assertEqual(destination.iata_code, 'CDG')
            self.assertEqual(destination.top_price, 500)
            self.assertEqual(destination.user, user)

if __name__ == '__main__':
    unittest.main()


