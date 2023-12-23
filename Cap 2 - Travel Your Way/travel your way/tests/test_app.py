import unittest
from flask import session
from app import app, db, User, Destination

class AppTestCase(unittest.TestCase):
    def setUp(self):
        """Set up the test environment"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///travel_your_way_test'

        self.client = app.test_client()

        with app.app_context():
            db.create_all()

            test_user = User(
                first_name='John',
                last_name='Doe',
                username='test_user',
                password='password'
            )
            db.session.add(test_user)
            db.session.commit()

    def tearDown(self):
        """Clean up after the test"""
        with app.app_context():
            db.drop_all()

    def test_homepage(self):
        """Test the homepage route"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_register(self):
        """Test user registration"""
        response = self.client.post('/register', data=dict(
            first_name='John',
            last_name='Doe',
            username='john_doe',
            password='password',
            confirm='password'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        response = self.client.get('/user', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hello john_do', response.data)

    def test_login(self):
        """Test user login"""
        # Register a user first
        self.client.post('/register', data=dict(
            first_name='John',
            last_name='Doe',
            username='john_doe',
            password='password',
            confirm='password'
        ), follow_redirects=True)

        # Log in with the registered user
        response = self.client.post('/login', data=dict(
            username='john_doe',
            password='password'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Log out', response.data)

    def test_logout(self):
        """Test user logout"""
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logout successful', response.data)

    def test_user_homepage(self):
        """Test user homepage route"""
        
        with app.app_context():
        # Log in with test user
            response = self.client.post('/login', data=dict(
                username='john_doe',

                password='password'
            ), follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Log in to edit', response.data)

    def test_add_destination(self):
        """Test adding a destination"""
        # Log in with a user
        self.client.post('/register', data=dict(
        first_name='John',
        last_name='Doe',
        username='john_doe',
        password='password',
        confirm='password'
    ), follow_redirects=True)

        response = self.client.post('/add_destination', data=dict(
            destination='Paris',
            top_price=500,
            base_city='CDG'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Destination added!', response.data)

        # Check if the destination is added to the user's list
        with app.app_context():
            user = User.query.filter_by(username='john_doe').first()
            self.assertTrue(user.destinations)  

    def test_delete_user(self):
        """Test deleting a user"""
        # Log in with a user
        self.client.post('/register', data=dict(
        first_name='John',
        last_name='Doe',
        username='john_doe',
        password='password',
        confirm='password'
    ), follow_redirects=True)

        response = self.client.post('/delete', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Successfully deleted', response.data)

    def test_delete_destination(self):
        """Test deleting a destination"""
        # Register a user
        response_register = self.client.post('/register', data=dict(
            first_name='John',
            last_name='Doe',
            username='john_doe',
            password='password',
            confirm='password'
        ), follow_redirects=True)

        # Check if registration was successful
        self.assertEqual(response_register.status_code, 200)
        self.assertIn(b'Hello john_doe', response_register.data)

        # Log in with the registered user
        response_login = self.client.post('/login', data=dict(
            username='john_doe',
            password='password'
        ), follow_redirects=True)

        # Check if login was successful
        self.assertEqual(response_login.status_code, 200)
        self.assertIn(b'Hello john_doe', response_login.data)

        # Add a destination
        response_add_destination = self.client.post('/add_destination', data=dict(
            destination='Paris',
            top_price=500,
            base_city='CDG'
        ), follow_redirects=True)

        # Check if adding destination was successful
        self.assertEqual(response_add_destination.status_code, 200)
        self.assertIn(b'Destination added!', response_add_destination.data)

        # Get the destination ID
        with app.app_context():
            user = User.query.filter_by(username='john_doe').first()
            self.assertIsNotNone(user, "User not found in the database")
            destination_id = user.destinations[0].id

        # Make the delete request within the application context
        response_delete_destination = self.client.post(f'/delete_destination/{destination_id}', follow_redirects=True)

        # Check if deleting destination was successful
        self.assertEqual(response_delete_destination.status_code, 200)
        self.assertIn(b'Your Destinations', response_delete_destination.data)


if __name__ == '__main__':
    unittest.main()
