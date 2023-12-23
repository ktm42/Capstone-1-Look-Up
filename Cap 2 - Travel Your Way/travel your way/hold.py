
    def test_delete_user(self):
        """Test deleting a user"""
        # Log in with a user
        self.client.post('/login', data=dict(
            username='john_doe',
            password='password'
        ), follow_redirects=True)

        response = self.client.post('/delete', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Successfully deleted', response.data)

    def test_delete_destination(self):
        """Test deleting a destination"""
        # Log in with a user
        self.client.post('/login', data=dict(
            username='john_doe',
            password='password'
        ), follow_redirects=True)

        # Add a destination first
        self.client.post('/add_destination', data=dict(
            destination='Paris',
            top_price=500,
            base_city='CDG'
        ), follow_redirects=True)

        # Get the destination ID
        user = User.query.filter_by(username='john_doe').first()
        destination_id = user.destinations[0].id

        response = self.client.post(f'/delete_destination/{destination_id}', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Destination deleted', response.data)