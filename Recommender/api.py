"""
This module defines the recommendation API endpoints, providing functionality to recommend users 
and posts based on mutual connections, shared interests, and hashtags. The endpoints are secured 
with JWT, conditional on the configuration setting for authentication.

Modules:
    - flask_jwt_extended: Provides JWT authentication.
    - flask: Used to define API routes and handle JSON responses.
    - logging: Used for logging any errors or information.
    - recommender_engine.JA_engine: The recommendation engine for generating recommendations based
      on user data.
    - db: The database instance.

Routes:
    - /users/<int:id_user> (GET): Recommends user profiles to the given user.
    - /posts/<int:id_user> (GET): Recommends posts to the given user.
"""

from flask_jwt_extended import jwt_required
from flask import Blueprint, jsonify, request
from .config import Config
import logging

from .utils.recommender_engine import JA_engine
from . import db

logger = logging.getLogger(__name__)

recommendation_bp = Blueprint(name="recommendation_api", import_name=__name__, url_prefix="/api/recommender")
recommender = JA_engine(db)

@recommendation_bp.route('users/<int:id_user>', methods=['GET'])
@jwt_required(not Config.NO_AUTH)
def recommend_users(id_user):
    """
    Recommend user profiles to a given user based on mutual followers and shared interests.

    Args:
        id_user (int): The ID of the user for whom recommendations are generated.

    Query Parameters:
        follow_weight (float, optional): The weight assigned to mutual following in the recommendation 
            score calculation. Defaults to 0.4.
        intrest_weight (float, optional): The weight assigned to shared interests in the recommendation 
            score calculation. Defaults to 0.6.

    Returns:
        JSON response: A sorted list of recommended user IDs.
        
        Response Codes:
            200: Successfully generated recommendations.
            400: Invalid input (e.g., non-numeric weights).
            500: Internal server error or other unexpected error.
    """
    try:
        follow_weight = float(request.args.get('follow_weight', 0.4))
        intrest_weight = float(request.args.get('intrest_weight', 0.6))
        
        recommended_users = recommender.recommend_users(id_user, follow_weight, intrest_weight)
        return jsonify(recommended_users), 200
    except ValueError as ve:
        logger.error(f"Value error in recommend_users: {ve}")
        return jsonify({'error': 'Invalid weight value provided'}), 400
    except Exception as e:
        logger.error(f"Unexpected error in recommend_users: {e}")
        return jsonify({'error': 'An error occurred while generating recommendations'}), 500

@recommendation_bp.route('/posts/<int:id_user>', methods=['GET'])
@jwt_required(not Config.NO_AUTH)
def recommend_posts(id_user):
    """
    Recommend posts to a given user based on shared hashtags and interests.

    Args:
        id_user (int): The ID of the user for whom post recommendations are generated.

    Returns:
        JSON response: A sorted list of recommended post IDs.
        
        Response Codes:
            200: Successfully generated recommendations.
            500: Internal server error or other unexpected error.
    """
    try:
        recommended_posts = recommender.recommend_posts(id_user)
        return jsonify(recommended_posts), 200
    except Exception as e:
        logger.error(f"Unexpected error in recommend_posts: {e}")
        return jsonify({'error': 'An error occurred while generating post recommendations'}), 500
