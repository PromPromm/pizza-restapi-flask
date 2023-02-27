from flask_restx import Namespace, Resource, fields
from flask import request
from ..models.users import User
from ..models.blocklist import TokenBlocklist
from werkzeug.security import generate_password_hash, check_password_hash
from http import HTTPStatus
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from ..utils import db
from datetime import timezone, datetime

auth_namespace = Namespace('auth', 'Namespace for authentication')

signup_model = auth_namespace.model(
    'signup', {
        'id': fields.Integer(),
        'username': fields.String(required=True, description='A username'),
        'email': fields.String(required=True, description='An email'),
        'password': fields.String(required=True, description='A password')
    }
)
login_model = auth_namespace.model(
    'login', {
        'email': fields.String(required=True, description='An email'),
        'password': fields.String(required=True, description='A password')
    }
)


@auth_namespace.route('/signup')
class SignUp(Resource):
    @auth_namespace.expect(signup_model)
    @auth_namespace.marshal_with(signup_model, HTTPStatus.OK)
    @auth_namespace.doc(description="Sign up on the pizza app")
                       
    def post(self):
        """
        Register a user
        """
        data = request.get_json()
        user_email = User.query.filter_by(email=data.get('email')).first()
        user_name = User.query.filter_by(username=data.get('username')).first()

        if user_email or user_name:
            return {"message": "User already exists"}
        new_user = User(
                username=data.get('username'),
                email=data.get('email'),
                password=generate_password_hash(data.get('password'))
            )
        new_user.save()
        return new_user, HTTPStatus.CREATED #NOTE


@auth_namespace.route('/login')
class Login(Resource):
    @auth_namespace.expect(login_model)
    @auth_namespace.doc(description="Login to account on the pizza app")
    def post(self):
        """
        Login a user
        """
        data = request.get_json()
        email = data.get('email')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, data.get('password')):
            access_token = create_access_token(user.username, fresh=True)
            refresh_token = create_refresh_token(user.username)
            response = {
                "access_token": access_token,
                "refresh_token": refresh_token
            }
            return response, HTTPStatus.CREATED
        # return {"message": "Invalid credentials"}, HTTPStatus.BAD_REQUEST


@auth_namespace.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    @auth_namespace.doc(description="Generate refresh tokens")
    def post(self):
        user_name = get_jwt_identity()
        access_token = create_access_token(identity=user_name, fresh=False)
        return {"access_token": access_token}, HTTPStatus.OK


@auth_namespace.route('/logout')
class Logout(Resource):
    @jwt_required(fresh=True)
    @auth_namespace.doc(description="Logout of the pizza app")
    def delete(self):
        jti = get_jwt()["jti"]
        token = TokenBlocklist(jti=jti, created_at=datetime.now(timezone.utc))
        db.session.add(token)
        db.session.commit()
        return {"message": "User successfully logged out"}

