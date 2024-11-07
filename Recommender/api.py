"""
This module defines the recommendation API endpoints, providing functionality to recommend users,
posts, and threads based on mutual connections, shared interests, and hashtags. The endpoints are
secured with JWT, conditional on the configuration setting for authentication.

Modules:
    - flask_jwt_extended: Provides JWT authentication.
    - flask: Used to define API routes and handle JSON responses.
    - logging: Used for logging errors or information.
    - mc_recommender_engine.JA_engine, mc_recommender_engine.MC_engine: Recommendation engines for
      generating recommendations based on user data.
    - db: The database instance.

Blueprint:
    recommendation_bp: The Flask blueprint for recommendation API endpoints.

Routes:
    - /recommend/users (GET): Recommends user profiles to a given user based on mutual connections and shared interests.
    - /recommend/posts (GET): Recommends posts to a given user based on interests and interactions.
    - /recommend/threads (GET): Recommends threads for a given user based on shared memberships and interests.
"""

from flask_jwt_extended import jwt_required
from flask import Blueprint, jsonify, request
from .config import Config
import logging

from .utils.recommender_engine import JA_engine
from . import db

logger = logging.getLogger(__name__)

mc_recommendation_bp = Blueprint(name="mc_recommendation_api", import_name=__name__, url_prefix="/recommend/MC")
from .utils.recommender_engine import MC_engine
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
    
    if not user_id:
        return jsonify({"error": "Missing user_id parameter"}), 400

    try:
        recommendations = mc_recommender.recommend_users(user_id, follow_weight, interest_weight)
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
    
    if not user_id:
        return jsonify({"error": "Missing user_id parameter"}), 400

    try:
        recommendations = mc_recommender.recommend_posts(user_id, interest_weight, interaction_weight)
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
    
    if not user_id:
        return jsonify({"error": "Missing user_id parameter"}), 400

    try:
        recommendations = mc_recommender.recommend_threads(user_id, member_weight, interest_weight)
        return jsonify({"recommended_threads": recommendations})
    except Exception as e:
        logger.error(f"Error in recommend_threads: {e}")
        return jsonify({"error": str(e)}), 500


em_recommendation_bp = Blueprint(name="em_recommendation_api", import_name=__name__, url_prefix="/recommend/EM")
from .utils.recommender_engine import EM_engine
em_recommender = EM_engine(db)

@em_recommendation_bp.route('/users', methods=['GET'])
@jwt_required(not Config.NO_AUTH)
def recommend_users():
    """
    Recommend user profiles based on shared interests and mutual connections.

    Query Parameters:
        user_id (str): The ID of the user requesting recommendations.
        follow_weight (float, optional): The weight given to mutual followers in scoring, default is 0.5.
        interest_weight (float, optional): The weight given to shared interests in scoring, default is 0.5.

    Returns:
        JSON: A JSON response containing a list of recommended user IDs or an error message.
        Status Code:
            200: Success, returns recommended users.
            400: Bad request, missing required parameters.
            500: Server error, failed to generate recommendations.
    """
    user_id = request.args.get('user_id')
    top_n = int(request.args.get('top_n', 15))
    
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
        interest_weight (float, optional): The weight given to shared interests in scoring, default is 0.7.
        interaction_weight (float, optional): The weight given to user interactions (likes, comments) in scoring, default is 0.3.

    Returns:
        JSON: A JSON response containing a list of recommended post IDs or an error message.
        Status Code:
            200: Success, returns recommended posts.
            400: Bad request, missing required parameters.
            500: Server error, failed to generate recommendations.
    """
    user_id = request.args.get('user_id')
    top_n = int(request.args.get('top_n', 15))
    
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
        member_weight (float, optional): The weight given to shared memberships in scoring, default is 0.6.
        interest_weight (float, optional): The weight given to shared interests in scoring, default is 0.4.

    Returns:
        JSON: A JSON response containing a list of recommended thread IDs or an error message.
        Status Code:
            200: Success, returns recommended threads.
            400: Bad request, missing required parameters.
            500: Server error, failed to generate recommendations.
    """
    user_id = request.args.get('user_id')
    top_n = int(request.args.get('top_n', 15))
    
    if not user_id:
        return jsonify({"error": "Missing user_id parameter"}), 400

    try:
        recommendations = em_recommender.recommend_threads(user_id, top_n)
        return jsonify({"recommended_threads": recommendations})
    except Exception as e:
        logger.error(f"Error in recommend_threads: {e}")
        return jsonify({"error": str(e)}), 500
