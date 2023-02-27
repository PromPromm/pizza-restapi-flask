from flask import Flask, jsonify
from flask_restx import Api
from .auth.views import auth_namespace
from .orders.views import order_namespace
from .user.views import user_namespace
from .config import config_dict
from .utils import db
from .models.orders import Order
from .models.users import User
from .models.blocklist import TokenBlocklist
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

def create_app(config=config_dict['prod']):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    jwt = JWTManager(app)
    
    migrate = Migrate(app, db)

    authorization = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Add a JWT token to the header with ** Bearer &lt;JWT&gt; token to authorize **"
        }
    }

    api = Api(app, title="Pizza Delivery API", description='A simple pizza delivery REST API service', authorizations=authorization, security='Bearer Auth')

    api.add_namespace(auth_namespace)
    api.add_namespace(order_namespace)
    api.add_namespace(user_namespace)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
        jti = jwt_payload["jti"]
        token = TokenBlocklist.query.filter_by(jti=jti).first()
        return token is not None

    @jwt.additional_claims_loader
    def add_claim_to_jwt(identity):
        if identity == "promiseee":
            return {"app_admin": True}
        return {"app_admin": False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "message": "The token has expired",
                    "error": "token_expired"
                }
            ), 401
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return jsonify(
            {
                "description": "The token is not fresh",
                "error": "fresh_token_required"
            }
        ), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {
                    "message": "Signature verification failed",
                    "error": "invalid_token"
                }
            ), 401
        )


    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token",
                    "error": "authorization_required"
                }
            ), 401
        )

    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'user': User,
            'order': Order
        }

    return app
