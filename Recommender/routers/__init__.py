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
    router: The Flask blueprint for recommendation API endpoints.

Routes:
    - /recommend/users (GET): Recommends user profiles to a given user based on mutual connections and shared interests.
    - /recommend/posts (GET): Recommends posts to a given user based on interests and interactions.
    - /recommend/threads (GET): Recommends threads for a given user based on shared memberships and interests.
"""
from .em_router import router as em_router
from .mc_router import router as mc_router
from .ja_router import router as ja_router

__all__ = [
    "em_router",
    "mc_router",
    "ja_router"
]
