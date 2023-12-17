import os
import unittest
from flask import Flask, g
from models import db, Register, User, Coordinates, connect_db, bcrypt
from app import app, CURR_USER_KEY

# Use a separate test database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'postgresql:///lookup_test')
app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection for testing
app.config['TESTING'] = True

# Ensure responses aren't cached during testing
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

class MyAppTests(unittest.TestCase):

    def setUp(self):
        """Set up the test database"""
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up the test database"""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_route(self):
        """Test the register route"""
        with self.app as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None #Simulate not logged in

            response = c.post('/register', data={
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'john_doe',
            'password': 'password',
            'address': '123 Main St'
        }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Hey there!', response.data)

            # Ensure user is added to the database
            with app.app_context():
                user = User.query.filter_by(username='john_doe').first()
                self.assertIsNotNone(user)
                self.assertEqual(user.username, 'john_doe')

                print(f'user: {user}')
                print(f"response.data: {response.data}")
                self.assertIsNotNone(user)
                self.assertEqual(user.username, 'john_doe')
                
    def test_login_route(self):
        """Test the login route"""
        with app.app_context():
            # Create a test user
            hashed_password = bcrypt.generate_password_hash('password').decode('utf-8')
            user = User(username='john_doe', password=hashed_password)
            db.session.add(user)
            db.session.commit()

            with self.app:
                response = self.app.post('/login', data={
                    'username': 'john_doe',
                    'password': 'password'
                }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Hey there!', response.data)
            self.assertIn(b'john_doe', response.data)
            self.assertIn(b'Your Addresses', response.data)

            # Ensure user is logged in
            with app.app_context():
                with self.app.session_transaction() as session:
                    self.assertTrue(CURR_USER_KEY in session)

    def test_user_homepage_route(self):
        """Test the user homepage route"""
        with self.app as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1  # Assuming a user is logged in

        response = c.get('/', follow_redirects=True)
        self.assertIn(b'Hello!', response.data)
    
if __name__ == '__main__':
    unittest.main()