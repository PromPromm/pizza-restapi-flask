import unittest
from .. import create_app
from ..utils import db
from ..config import config_dict
from ..models.orders import Order
from ..models.users import User
from flask_jwt_extended import create_access_token


class OrderTestCase(unittest.TestCase):
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

    def test_get_all_orders(self):
        token = create_access_token(identity="testuser")
        
        header = {
            "Authorization": f"Bearer {token}"
        }
        response = self.client.get('/orders/orders', headers=header)

        assert response.status_code == 200

        assert response.json == []


    def test_create_order(self):
        data = {
            'flavour': "BACON"
        }
        token = create_access_token(identity="testuser")
        
        header = {
            "Authorization": f"Bearer {token}"
        }
        
        response = self.client.post('/orders/orders', headers=header, json=data)

        assert response.status_code == 201

        orders = Order.query.all()

        assert len(orders) == 1

        assert response.json['sizes'] == 'Sizes.SMALL'

    
    def test_get_order_by_id(self):
        token = create_access_token(identity="testuser")
        data = {
            'flavour': "PINEAPPLE"
        }
        header = {
            "Authorization": f"Bearer {token}"
        }
        response_1 = self.client.post('/orders/orders', headers=header, json=data)
        response_2 = self.client.get('/orders/order/1', headers=header)
        assert response_2.status_code == 200
        orders = Order.query.all()
        order_id = orders[0].id
        assert order_id == 1
        assert len(orders) == 1
        assert response_2.json['flavour'] == 'OrderFlavour.PINEAPPLE'
        
        
    def test_delete_order_by_id(self):
        token = create_access_token(identity="testuser")
        data = {
            'flavour': "BBQ_CHICKEN"
        }
        header = {
            "Authorization": f"Bearer {token}"
        }
        data_user = {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "password"
            }
        response = self.client.post('/auth/signup', json=data_user)
        response = self.client.post('/orders/orders', headers=header, json=data)
        response = self.client.delete('/orders/order/1', headers=header)
        assert response.status_code == 200
        assert response.json == {"message": "Order deleted successfully"}

    def test_update_order_status(self):
        token = create_access_token(identity="testuser")
        order = {
            'flavour': "BBQ_CHICKEN"
        }
        data = {
            'order_status': "DELIVERED"
        }
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
        response = self.client.post('/orders/orders', headers=header, json=order)
        response = self.client.patch('/orders/order/1/status', headers=header, json=data)
        assert response.status_code == 200
        assert response.json['order_status'] == 'OrderStatus.DELIVERED'
