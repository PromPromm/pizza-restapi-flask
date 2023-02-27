import unittest
from .. import create_app
from ..utils import db
from ..config import config_dict
from ..models.orders import Order
from flask_jwt_extended import create_access_token

class UserTestCase(unittest.TestCase):
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

    def test_get_user_specific_order(self):
        token = create_access_token(identity="testuser")
        
        header = {
            "Authorization": f"Bearer {token}"
        }
        data = {
            'flavour': "BACON"
        }
        data_user = {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "password"
            }
        response = self.client.post('/auth/signup', json=data_user)
        response = self.client.post('/orders/orders', headers=header, json=data)
        response = self.client.get('/user/1/orders/1', headers=header)

        assert response.status_code == 200
        assert response.json['id'] == 1

    def test_get_all_user_orders(self):
        token = create_access_token(identity="testuser")
        
        header = {
            "Authorization": f"Bearer {token}"
        }
        data_1 = {
            'flavour': "BACON"
        }

        data_2 = {
            'flavour': "PEPPERONI"
        }

        data_user = {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "password"
            }
        response = self.client.post('/auth/signup', json=data_user)

        response = self.client.post('/orders/orders', headers=header, json=data_1)
        response = self.client.post('/orders/orders', headers=header, json=data_2)
        response = self.client.get('/user/1/orders', headers=header)

        orders = Order.query.all()

        assert len(orders) == 2
        assert response.status_code == 200
        
    def test_give_admin_privileges(self):
        token = create_access_token(identity="testuser")
        
        header = {
            "Authorization": f"Bearer {token}"
        }
        data_user = {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "password"
            }
        response = self.client.post('/auth/signup', json=data_user)
        response = self.client.patch('/user/user/1', headers=header)
        assert response.status_code == 200
        assert response.json['is_staff'] == True


    def test_delete_user(self):
        token = create_access_token(identity="testuser", fresh=True)
        
        header = {
            "Authorization": f"Bearer {token}"
        }
        data_user_1 = {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "password"
            }
        data_user_2 = {
            "username": "testuser2",
            "email": "testuser2@gmail.com",
            "password": "password"
            }
        response = self.client.post('/auth/signup', json=data_user_1)
        response = self.client.post('/auth/signup', json=data_user_2)
        response = self.client.patch('/user/user/1', headers=header)
        response = self.client.delete('/user/user/2', headers=header)
        assert response.status_code == 200
        assert response.json == {"message": "User deleted successfully"}


    def test_get_user(self):
        token = create_access_token(identity="testuser", fresh=True)
        
        header = {
            "Authorization": f"Bearer {token}"
        }
        data_user_1 = {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "password"
            }
        data_user_2 = {
            "username": "testuser2",
            "email": "testuser2@gmail.com",
            "password": "password"
            }
        response = self.client.post('/auth/signup', json=data_user_1)
        response = self.client.post('/auth/signup', json=data_user_2)
        response = self.client.patch('/user/user/1', headers=header)
        response = self.client.get('/user/user/2', headers=header)
        assert response.status_code == 200
        assert response.json["username"] == "testuser2"

        