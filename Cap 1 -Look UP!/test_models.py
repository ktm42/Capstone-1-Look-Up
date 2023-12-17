import os

import unittest
from flask import Flask
from models import db, connect_db, bcrypt, User, Coordinates, Register

os.environ['DATABASE_URI'] = "postgresql:///lookup_test" 

import unittest
from flask import Flask
from models import db, Register, User, Coordinates, connect_db, bcrypt

class TestModels(unittest.TestCase):

    def setUp(self):
        """Set up the test database"""
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'postgresql:///lookup_test')
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['TESTING'] = True
        self.app.config['DEBUG'] = False
        self.app.config['SECRET_KEY'] = 'secret_key'

        with self.app.app_context():
            connect_db(self.app)
            db.create_all()

    def tearDown(self):
        """Clean up the test database"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_user(self):
        """Test user registration"""
        with self.app.app_context():
            user = Register.register(
                first_name='John',
                last_name='Doe',
                address='123 Main St',
                username='john_doe',
                password='password'
            )

            self.assertIsInstance(user, User)
            self.assertEqual(user.username, 'john_doe')

    def test_authenticate_user(self):
        """Test user authentication"""
        with self.app.app_context():
            # Register a user first
            Register.register(
                first_name='John',
                last_name='Doe',
                address='123 Main St',
                username='john_doe',
                password='password'
            )

            authenticated_user = User.authenticate('john_doe', 'password')
            self.assertIsInstance(authenticated_user, User)
            self.assertEqual(authenticated_user.username, 'john_doe')

            # Test with incorrect password
            wrong_password_user = User.authenticate('john_doe', 'wrong_password')
            self.assertFalse(wrong_password_user)

            # Test with non-existent user
            non_existent_user = User.authenticate('nonexistent_user', 'password')
            self.assertFalse(non_existent_user)

    def test_log_coords(self):
        """Test logging coordinates"""
        with self.app.app_context():
            # Register a user first
            user = Register.register(
                first_name='John',
                last_name='Doe',
                address='123 Main St',
                username='john_doe',
                password='password'
            )

            # Log coordinates for the user
            Coordinates.log_coords(latitude=123.456, longitude=-78.910, user=user)

            # Check if coordinates are logged
            coordinates = Coordinates.query.filter_by(user=user).first()
            self.assertIsNotNone(coordinates)
            self.assertEqual(coordinates.latitude, 123.456)
            self.assertEqual(coordinates.longitude, -78.910)

if __name__ == '__main__':
    unittest.main()

