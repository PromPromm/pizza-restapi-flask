from flask_restx import Namespace, Resource, fields
from flask import abort
from ..models.users import User
from ..models.orders import Order
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from http import HTTPStatus
from ..utils import db

user_namespace = Namespace('user', 'Namespace for user order')

order_model = user_namespace.model(
    'order', {
        'id': fields.Integer(),
        'sizes': fields.String(description='The size of pizza order', enum=['SMALL', 'MEDIUM', 'LARGE', 'EXTRA_LARGE']),
        'order_status': fields.String(description='Status of the order', enum=['PENDING', 'IN_TRANSIT', 'DELIVERED']),
        'flavour': fields.String(description='Pizza flavour'),
        'quantity': fields.Integer(description='Quantity of order'),
        'date_created': fields.DateTime(description='Time order was placed'),
        'customer': fields.Integer()
    }
)

user_model = user_namespace.model(
    'user', {
        'id': fields.Integer(),
        'username': fields.String(required=True, description='A username'),
        'email': fields.String(required=True, description='An email'),
        'password': fields.String(required=True, description='A password'),
        'is_staff': fields.Boolean(required=True, description='User admin Status'),
        'is_active': fields.Boolean(required=True, description='User active Status'),
        'orders': fields.List(fields.Nested(order_model), required=True, description='List of orders by user')
    }
)

@user_namespace.route('/<int:user_id>/orders/<int:order_id>')
class GetSpecificOrderByUser(Resource):
    @jwt_required()
    @user_namespace.marshal_list_with(order_model)
    @user_namespace.doc(description="Get a user specific order with the user id and order id",
                            params= {
                                'order_id': "The order id",
                                "user_id": "The user id"
                            }
    )
    def get(self, user_id, order_id):
        """
        Gets a user specific order
        """
        user = User.get_by_id(user_id)

        order = Order.query.filter_by(id=order_id).filter_by(user=user).first()

        return order, HTTPStatus.OK #NOTE


@user_namespace.route('/<int:user_id>/orders')
class GetOrdersByUser(Resource):
    @user_namespace.marshal_list_with(order_model)
    @user_namespace.doc(description="Get all orders of a particular user with the user id",
                            params= {
                                'user_id': "The user id"
                            } 
    )
    @jwt_required()
    def get(self, user_id):
        """
        Get all orders by a particular user
        """
        user = User.get_by_id(user_id)
        orders = user.orders

        return orders, 200

@user_namespace.route('/user/<int:user_id>')
class UserViews(Resource):
    @jwt_required()
    @user_namespace.marshal_with(user_model)
    @user_namespace.doc(description="Get a user with the user id. Only admins can access this route",
                            params= {
                                'user_id': "The user id"
                            } 
    )
    def get(self, user_id):
        """
        Get a user's details
        """
        user_name = get_jwt_identity()
        staff = User.query.filter_by(username=user_name).first()
        if staff.is_staff:
            user = User.get_by_id(user_id)
            return user, HTTPStatus.OK
        

    @jwt_required(fresh=True)
    @user_namespace.doc(description="Delete a user with the user id. Only admins can access this route. It is to be used when malicious activities are carried out by the user.",
                            params= {
                                'user_id': "The user id"
                            } 
    )
    def delete(self, user_id):
        """
        Delete a user
        """
        user_name = get_jwt_identity()
        staff = User.query.filter_by(username=user_name).first()
        user =  User.get_by_id(user_id)
        if staff.is_staff:
            db.session.delete(user)
            db.session.commit()
            return {"message": "User deleted successfully"}, HTTPStatus.OK

    @jwt_required()
    @user_namespace.marshal_with(user_model)
    @user_namespace.doc(description="Give a user admin privileges using the user id. Only the super administrator can access this route",
                            params= {
                                'user_id': "The user id"
                            } 
    )
    def patch(self, user_id):
        """
        Give staff privileges to user
        """
        jwt = get_jwt()
        if not jwt.get("app_admin"):
            abort(401, "Admin privilege only")
        user = User.query.get_or_404(user_id)
        user.make_admin()
        return user, HTTPStatus.OK

        
