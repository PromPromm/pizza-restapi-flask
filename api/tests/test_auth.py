import unittest
from .. import create_app
from ..utils import db
from ..config import config_dict
from werkzeug.security import generate_password_hash, check_password_hash
from ..models.users import User
from flask_jwt_extended import create_access_token, create_refresh_token


class AuthenticationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config=config_dict['test'])
        self.appctx = self.app.app_context()
        self.appctx.push()
        self.client = self.app.test_client()
        db.create_all()


    def tearDown(self):
        db.drop_all()
        self.appctx.pop()
        self.app = None
        self.client = None
        

    def test_user_registration(self):
        data = {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "password"
            }
        response = self.client.post('/auth/signup', json=data)

        user = User.query.filter_by(email="testuser@gmail.com").first()

        assert user.username == "testuser"

        assert response.status_code == 201


    def test_user_login(self):
        data = {
            "email": "testuser@gmail.com",
            "password": "password"
        }

        response = self.client.post('/auth/login', json=data)

        assert response.status_code == 200


    def test_user_logout(self):
        token = create_access_token(identity="testuser", fresh=True)

        header = {
            "Authorization": f"Bearer {token}"
        }

        response = self.client.delete('auth/logout', headers=header)
        assert response.status_code == 200
        assert response.json == {"message": "User successfully logged out"}

    def test_user_refresh(self):
        token = create_refresh_token(identity="testuser")
        header = {
            "Authorization": f"Bearer {token}"
        }

        response = self.client.post('auth/refresh', headers=header)
        assert response.status_code == 200

