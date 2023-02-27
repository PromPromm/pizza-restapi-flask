from flask_restx import Namespace, Resource, fields
from ..models.orders import Order, OrderStatus
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.users import User
from ..utils import db
from flask import request, abort

order_namespace = Namespace('orders', 'Namespace for order')

place_order_model = order_namespace.model(
    'order', {
        'flavour': fields.String(required=True, description='Pizza flavour')
    }
)
order_model = order_namespace.model(
    'order', {
        'id': fields.Integer(),
        'sizes': fields.String(description='The size of pizza order', enum=['SMALL', 'MEDIUM', 'LARGE', 'EXTRA_LARGE']),
        'order_status': fields.String(description='Status of the order', enum=['PENDING', 'IN_TRANSIT', 'DELIVERED']),
        'flavour': fields.String(description='Pizza flavour', enum=['BBQ_CHICKEN', 'PEPPERONI', 'SAUSAGE', 'CHEESE', 'EXTRA_CHEESE', 'BACON', 'PINEAPPLE', 'MARGHERITA' ]),
        'quantity': fields.Integer(description='Quantity of order'),
        'date_created': fields.DateTime(description='Time order was placed'),
        'customer': fields.Integer()
    }
)
update_order_model = order_namespace.model(
    'order', {
        'sizes': fields.String(description='The size of pizza order', enum=['SMALL', 'MEDIUM', 'LARGE', 'EXTRA_LARGE']),
        'flavour': fields.String(description='Pizza flavour'),
        'quantity': fields.Integer(description='Quantity of order')
    }
)

update_order_status_model = order_namespace.model(
    'order', {
        'order_status': fields.String(description='Status of the order', enum=['PENDING', 'IN_TRANSIT', 'DELIVERED'])
    }
)

@order_namespace.route('/orders')
class Orders(Resource):
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(description="Get all orders")
    @jwt_required()
    def get(self):
        """
        Get all orders
        """
        orders = Order.query.all()
        return orders, HTTPStatus.OK


    @order_namespace.expect(place_order_model)
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(description="Place an order")
    @jwt_required()
    def post(self):
        """
        Place an order
        """
        user_name = get_jwt_identity()
        current_user = User.query.filter_by(username=user_name).first()
        data = order_namespace.payload #NOTE
        new_order = Order(
            flavour=data['flavour']
        )
        new_order.user = current_user
        new_order.save()
        return new_order, HTTPStatus.CREATED #NOTE???? Wrong Enum


@order_namespace.route('/order/<int:order_id>')
class OrderById(Resource):
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(description="Retrieve an order by it's id",
                            params= {
                                'order_id': "The order id"
                            }
    )
    @jwt_required()
    def get(self, order_id):
        """
        Get an order by id
        """
        order = Order.get_by_id(order_id)
        return order, HTTPStatus.OK
        

    @order_namespace.expect(update_order_model)
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(description="Update an order with id",
                            params= {
                                'order_id': "The order id"
                            }
    )
    @jwt_required()
    def patch(self, order_id):
        """
        Update an order
        """
        order_to_update = Order.get_by_id(order_id)
        data = order_namespace.payload
        identity = get_jwt_identity()
        current_user = User.query.filter_by(id=order_to_update.customer).first()

        if (identity == current_user.username):
            order_to_update.sizes = data['sizes']
            order_to_update.flavour = data['flavour']
            order_to_update.quantity = data['quantity']

            db.session.commit()
            return order_to_update, HTTPStatus.OK

    @jwt_required()
    @order_namespace.doc(description="Delete an order by id",
                            params= {
                                'order_id': "The order id"
                            }
    )
    def delete(self, order_id):
        """
        Delete an order
        """
        identity = get_jwt_identity()
        order_to_delete = Order.get_by_id(order_id)
        current_user = User.query.filter_by(id=order_to_delete.customer).first()

        if (identity == current_user.username):
            if order_to_delete.order_status != OrderStatus.PENDING:
                abort(404, 'Order already in production')
            order_to_delete.delete_by_id()
            return {"message": "Order deleted successfully"}, HTTPStatus.OK
        return {"message": "Not allowed"}, HTTPStatus.FORBIDDEN


@order_namespace.route('/order/<int:order_id>/status')
@order_namespace.doc(description="Update order status by id",
                        params= {
                                'order_id': "The order id"
                            }
)
class UpdateOrderStatus(Resource):
    @jwt_required()
    @order_namespace.expect(update_order_status_model)
    @order_namespace.marshal_with(order_model)
    def patch(self, order_id):
        """
        Update an order status
        """
        identity = get_jwt_identity()
        user = User.query.filter_by(username=identity).first()
        if user.is_staff:
            order_to_update = Order.get_by_id(order_id)
            data = order_namespace.payload
            order_to_update.order_status = data['order_status']
            
            db.session.commit()
            return order_to_update, HTTPStatus.OK
