"""
Add authentication routes to the application, enabling user registration and login functionalities.
This module provides endpoints for user registration (if `INDEPENDENT_REGISTER` is enabled) and
authentication through JSON Web Tokens (JWT). It uses rate-limiting (commented out here) to limit
access frequency to the registration and login routes.

Routes:
    /register (POST): Registers a new user with a username and password, provided that they do
    not already exist in the database. This route is available only if `INDEPENDENT_REGISTER` 
    in the config is set to True.

    /login (POST): Authenticates an existing user by verifying the username and password. If
    authentication is successful, a JWT access token is returned.
"""

from flask_jwt_extended import create_access_token
from flask import Blueprint, jsonify, request
from .utils import Database
from .config import Config
from . import db

config = Config()

bp = Blueprint("api", __name__, url_prefix="/api/auth")

if config.INDEPENDENT_REGISTER:
    @bp.route('/register', methods=['POST'])
    # @bp.limiter.limit("5 per minute")
    def register():
        """
        Register a new user.

        Accepts a JSON payload with 'username' and 'password' fields. Checks if the username
        already exists in the database; if not, creates a new user entry with the given
        credentials.

        Returns:
            JSON response with a success message on successful registration or an error message
            if the username is missing, the password is missing, or the user already exists.
        """
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        if not username or not password:
            return jsonify({"msg": "Username and password are required"}), 400
        if db.exist_user(username):
            return jsonify({"msg": "User already exist"}), 400
        db.create_user(username, password)
        return jsonify({"msg": f"User {username} created with success"}), 201

@bp.route('/login', methods=['POST'])
# @bp.limiter.limit("5 per minute")
def login():
    """
    Authenticate an existing user and return a JWT access token.

    Accepts a JSON payload with 'username' and 'password' fields. Verifies the username and
    password against the database. If authentication is successful, generates and returns
    a JWT access token.

    Returns:
        JSON response containing the JWT access token if authentication is successful, or
        an error message if the username or password is incorrect.
    """
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if db.exist_user(username) and db.check_user(username, password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)
    
    return jsonify({"msg": "Wrong identifiers"}), 401
