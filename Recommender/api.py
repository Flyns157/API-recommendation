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
    Endpoint pour recommander des profils à un utilisateur en fonction des abonnements mutuels et des intérêts.

    Args:
        id_user (int): L'identifiant de l'utilisateur.

    Query Params:
        follow_weight (float): Poids pour l'abonnement mutuel dans le calcul de recommandation (par défaut 0.4).
        intrest_weight (float): Poids pour les intérêts partagés dans le calcul de recommandation (par défaut 0.6).

    Returns:
        JSON: Liste triée des IDs des utilisateurs recommandés.
    """
    try:
        follow_weight = float(request.args.get('follow_weight', 0.4))
        intrest_weight = float(request.args.get('intrest_weight', 0.6))
        
        recommended_users = recommender.recommend_users(id_user, follow_weight, intrest_weight)
        return jsonify(recommended_users), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recommendation_bp.route('/api/recommend/posts/<int:id_user>', methods=['GET'])
@jwt_required(not Config.NO_AUTH)
def recommend_posts(id_user):
    """
    Endpoint pour recommander des posts à un utilisateur en fonction des hashtags et des intérêts.

    Args:
        id_user (int): L'identifiant de l'utilisateur.

    Returns:
        JSON: Liste triée des IDs des posts recommandés.
    """
    try:
        recommended_posts = recommender.recommend_posts(id_user)
        return jsonify(recommended_posts), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
