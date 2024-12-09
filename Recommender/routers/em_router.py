"""
This file contains the API routes for the EM-based recommendation engine.
"""
from flask_jwt_extended import jwt_required
from flask import Blueprint, jsonify, request
from ..utils.config import Config
import logging

from ..core.em_engine import EM_engine
from .. import db

logger = logging.getLogger(__name__)


em_recommendation_bp = Blueprint(name="em_recommendation_api", import_name=__name__, url_prefix="/recommend/EM")
from ..utils import EM_engine
em_recommender = EM_engine(db)

@em_recommendation_bp.route('/users', methods=['GET'])
@jwt_required(not Config.NO_AUTH)
def recommend_users():
    """
    Recommend user profiles based on shared interests and mutual connections.

    Query Parameters:
        user_id (str): The ID of the user requesting recommendations.
        limit (int, optional): The size of the recommendation.

    Returns:
        JSON: A JSON response containing a list of recommended user IDs or an error message.
        Status Code:
            200: Success, returns recommended users.
            400: Bad request, missing required parameters.
            500: Server error, failed to generate recommendations.
    """
    user_id = request.args.get('user_id')
    top_n = int(request.args.get('limit', 10))
    
    if not user_id:
        return jsonify({"error": "Missing user_id parameter"}), 400

    try:
        recommendations = em_recommender.recommend_users(user_id, top_n)
        return jsonify({"recommended_users": recommendations})
    except Exception as e:
        logger.error(f"Error in recommend_users: {e}")
        return jsonify({"error": str(e)}), 500

@em_recommendation_bp.route('/posts', methods=['GET'])
@jwt_required(not Config.NO_AUTH)
def recommend_posts():
    """
    Recommend posts based on shared interests and user interactions.

    Query Parameters:
        user_id (str): The ID of the user requesting recommendations.
        limit (int, optional): The size of the recommendation.

    Returns:
        JSON: A JSON response containing a list of recommended post IDs or an error message.
        Status Code:
            200: Success, returns recommended posts.
            400: Bad request, missing required parameters.
            500: Server error, failed to generate recommendations.
    """
    user_id = request.args.get('user_id')
    top_n = int(request.args.get('limit', 10))
    
    if not user_id:
        return jsonify({"error": "Missing user_id parameter"}), 400

    try:
        recommendations = em_recommender.recommend_posts(user_id, top_n)
        return jsonify({"recommended_posts": recommendations})
    except Exception as e:
        logger.error(f"Error in recommend_posts: {e}")
        return jsonify({"error": str(e)}), 500

@em_recommendation_bp.route('/threads', methods=['GET'])
@jwt_required(not Config.NO_AUTH)
def recommend_threads():
    """
    Recommend threads for a user based on shared memberships and interests.

    Query Parameters:
        user_id (str): The ID of the user requesting recommendations.
        limit (int, optional): The size of the recommendation.

    Returns:
        JSON: A JSON response containing a list of recommended thread IDs or an error message.
        Status Code:
            200: Success, returns recommended threads.
            400: Bad request, missing required parameters.
            500: Server error, failed to generate recommendations.
    """
    user_id = request.args.get('user_id')
    top_n = int(request.args.get('limit', 10))
    
    if not user_id:
        return jsonify({"error": "Missing user_id parameter"}), 400

    try:
        recommendations = em_recommender.recommend_threads(user_id, top_n)
        return jsonify({"recommended_threads": recommendations})
    except Exception as e:
        logger.error(f"Error in recommend_threads: {e}")
        return jsonify({"error": str(e)}), 500
