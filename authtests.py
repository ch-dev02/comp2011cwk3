import os
import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app, db, models
from flask_login import current_user

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        #the basedir lines could be added like the original db
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()
        pass

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        pass

    # HELPER FUNCTIONS

    def signup(self, username, password):
        return self.app.post(
        '/signup',
        data=dict(username=username, password=password),
        follow_redirects=True
        )
        
    def login(self, username, password):
        return self.app.post(
        '/',
        data=dict(username=username, password=password),
        follow_redirects=True
        )
        
    def logout(self):
        return self.app.get(
        '/logout',
        follow_redirects=True
        )

    # UNIT TESTS

    def test_signup_get(self): # Basic get request to signup page to test it loads
        response = self.app.get('/signup',
                               follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h2 class="page-title">Sign Up</h2>', response.data)

    def test_signup_post(self): # Post request to signup page to test account signup
        # test valid T0 - valid signup
        response = self.signup('sc20cah', 'Callum')
        user = models.User.query.filter_by(username='sc20cah').first()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(user)
        self.assertNotIn(b'Username already exists', response.data)

        # test invalid T1 - invalid as username is already taken
        response = self.signup('sc20cah', 'Callum')
        user = models.User.query.filter_by(username='sc20cah').first()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(user)
        self.assertIn(b'Username already exists', response.data)

        # test invalid T2 - invalid as password is empty
        response = self.signup('sc20cah2', '')
        user = models.User.query.filter_by(username='sc20cah2').first()
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(user)
        self.assertIn(b'Invalid username or password', response.data)

        # test invalid T3 - invalid as username is empty
        response = self.signup('', 'Callum')
        user = models.User.query.filter_by(username='').first()
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(user)
        self.assertIn(b'Invalid username or password', response.data)

        # test invalid T4 - invalid as username and password are empty
        response = self.signup('', '')
        user = models.User.query.filter_by(username='').first()
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(user)
        self.assertIn(b'Invalid username or password', response.data)

    def test_login_get(self): # Basic get request to login page to test it loads
        response = self.app.get('/',
                               follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h2 class="page-title">Login</h2>', response.data)

    def test_login_post(self): # Post requests to login page to test login functionality
        # Pre-test ensure user exists
        self.signup('sc20cah', 'Callum')
        user = models.User.query.filter_by(username='sc20cah').first()
        self.assertIsNotNone(user)

        # test valid T1 - valid login
        with self.app:
            response = self.login('sc20cah', 'Callum')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(current_user.is_authenticated)
            self.logout()

        # test invalid T2 - invalid as account does not exist
        with self.app:
            response = self.login('sc20cax', 'Callum')
            self.assertEqual(response.status_code, 200)
            self.assertFalse(current_user.is_authenticated)

        # test invalid T3 - invalid as password is incorrect
        with self.app:
            response = self.login('sc20cah', 'Xallum')
            self.assertEqual(response.status_code, 200)
            self.assertFalse(current_user.is_authenticated)

        # test invalid T4 - invalid as password is empty
        with self.app:
            response = self.login('sc20cah', '')
            self.assertEqual(response.status_code, 200)
            self.assertFalse(current_user.is_authenticated)

        # test invalid T5 - invalid as username is empty
        with self.app:
            response = self.login('', 'Callum')
            self.assertEqual(response.status_code, 200)
            self.assertFalse(current_user.is_authenticated)

        # test invalid T6 - invalid as username and password are empty
        with self.app:
            response = self.login('', '')
            self.assertEqual(response.status_code, 200)
            self.assertFalse(current_user.is_authenticated)

    def test_logout(self):
        # Pre-test ensure user exists
        self.signup('sc20cah', 'Callum')
        user = models.User.query.filter_by(username='sc20cah').first()
        self.assertIsNotNone(user)

        # test valid T1 - valid logout
        with self.app:
            self.login('sc20cah', 'Callum')
            self.assertTrue(current_user.is_authenticated)
            response = self.logout()
            self.assertEqual(response.status_code, 200)
            self.assertFalse(current_user.is_authenticated)

if __name__ == "__main__":
    unittest.main()