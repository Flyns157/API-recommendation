"""
This file contains the API routes for the Monte Carlo-based recommendation engine.
"""
from flask_jwt_extended import jwt_required
from flask import Blueprint, jsonify, request
from ..utils.config import Config
import logging

from ..core.mc_engine import MC_engine
from .. import db

logger = logging.getLogger(__name__)

mc_recommendation_bp = Blueprint(name="mc_recommendation_api", import_name=__name__, url_prefix="/recommend/MC")
from ..utils import MC_engine
mc_recommender = MC_engine(db)

@mc_recommendation_bp.route('/users', methods=['GET'])
@jwt_required(not Config.NO_AUTH)
def recommend_users():
    """
    Recommend user profiles based on shared interests and mutual connections.

    Query Parameters:
        user_id (str): The ID of the user requesting recommendations.
        follow_weight (float, optional): The weight given to mutual followers in scoring, default is 0.5.
        interest_weight (float, optional): The weight given to shared interests in scoring, default is 0.5.
        limit (int, optional): The size of the recommendation.

    Returns:
        JSON: A JSON response containing a list of recommended user IDs or an error message.
        Status Code:
            200: Success, returns recommended users.
            400: Bad request, missing required parameters.
            500: Server error, failed to generate recommendations.
    """
    user_id = request.args.get('user_id')
    follow_weight = float(request.args.get('follow_weight', 0.5))
    interest_weight = float(request.args.get('interest_weight', 0.5))
    limit = int(request.args.get('limit', 10))
    
    if not user_id:
        return jsonify({"error": "Missing user_id parameter"}), 400

    try:
        recommendations = mc_recommender.recommend_users(user_id, follow_weight, interest_weight, limit)
        return jsonify({"recommended_users": recommendations})
    except Exception as e:
        logger.error(f"Error in recommend_users: {e}")
        return jsonify({"error": str(e)}), 500

@mc_recommendation_bp.route('/posts', methods=['GET'])
@jwt_required(not Config.NO_AUTH)
def recommend_posts():
    """
    Recommend posts based on shared interests and user interactions.

    Query Parameters:
        user_id (str): The ID of the user requesting recommendations.
        interest_weight (float, optional): The weight given to shared interests in scoring, default is 0.7.
        interaction_weight (float, optional): The weight given to user interactions (likes, comments) in scoring, default is 0.3.
        limit (int, optional): The size of the recommendation.

    Returns:
        JSON: A JSON response containing a list of recommended post IDs or an error message.
        Status Code:
            200: Success, returns recommended posts.
            400: Bad request, missing required parameters.
            500: Server error, failed to generate recommendations.
    """
    user_id = request.args.get('user_id')
    interest_weight = float(request.args.get('interest_weight', 0.7))
    interaction_weight = float(request.args.get('interaction_weight', 0.3))
    limit = int(request.args.get('limit', 10))
    
    if not user_id:
        return jsonify({"error": "Missing user_id parameter"}), 400

    try:
        recommendations = mc_recommender.recommend_posts(user_id, interest_weight, interaction_weight, limit)
        return jsonify({"recommended_posts": recommendations})
    except Exception as e:
        logger.error(f"Error in recommend_posts: {e}")
        return jsonify({"error": str(e)}), 500

@mc_recommendation_bp.route('/threads', methods=['GET'])
@jwt_required(not Config.NO_AUTH)
def recommend_threads():
    """
    Recommend threads for a user based on shared memberships and interests.

    Query Parameters:
        user_id (str): The ID of the user requesting recommendations.
        member_weight (float, optional): The weight given to shared memberships in scoring, default is 0.6.
        interest_weight (float, optional): The weight given to shared interests in scoring, default is 0.4.
        limit (int, optional): The size of the recommendation.

    Returns:
        JSON: A JSON response containing a list of recommended thread IDs or an error message.
        Status Code:
            200: Success, returns recommended threads.
            400: Bad request, missing required parameters.
            500: Server error, failed to generate recommendations.
    """
    user_id = request.args.get('user_id')
    member_weight = float(request.args.get('member_weight', 0.6))
    interest_weight = float(request.args.get('interest_weight', 0.4))
    limit = int(request.args.get('limit', 10))
    
    if not user_id:
        return jsonify({"error": "Missing user_id parameter"}), 400

    try:
        recommendations = mc_recommender.recommend_threads(user_id, member_weight, interest_weight, limit)
        return jsonify({"recommended_threads": recommendations})
    except Exception as e:
        logger.error(f"Error in recommend_threads: {e}")
        return jsonify({"error": str(e)}), 500
