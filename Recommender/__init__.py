"""
This module defines the RecommendationAPI class, which extends Flask to create a customizable API server
for recommendation services. It includes authentication, rate limiting, logging, and configurable modes
(deploy, debug, maintenance) for different use cases.

Modules:
    - flask_limiter.util: Provides utilities for rate-limiting based on the client's remote address.
    - flask_jwt_extended: Manages JWT authentication for the API.
    - Database, Utils: Utility modules for database interactions and general helper functions.
    - flask_limiter: Enables rate limiting for API endpoints.
    - Config: Configuration settings for the API.
    - logging: Used to set up a logging system with both file and stream handlers.

Classes:
    - RecommendationAPI: The main API server class, handling initialization and configuration for the API.
"""
__version__ = "0.1.5"

from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager
from .utils import Database, Utils
from flask_limiter import Limiter
from flask import Flask, jsonify
from .config import Config
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('recommender.log'), logging.StreamHandler()])
logger = logging.getLogger(__name__)
db = Database()

class RecommendationAPI(Flask):
    """
    RecommendationAPI extends Flask to provide a recommendation server with JWT-based authentication,
    rate limiting, logging, and configurable run modes. It sets up database, JWT, and rate-limiting 
    integrations and registers API blueprints for authentication and recommendation.

    Attributes:
        limiter (Limiter): The rate-limiting manager, limiting the number of requests per day and hour.
        db (Database): The database instance used for managing user and recommendation data.
        logger (logging.Logger): The application logger.
        jwt (JWTManager): The JSON Web Token manager for handling user authentication.
        mode (str): The operational mode of the server, affecting availability and functionality.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the RecommendationAPI instance with Flask configuration, rate limiting, JWT,
        logging, and route registration.

        Parameters:
            *args: Variable length argument list passed to the Flask constructor.
            **kwargs: Arbitrary keyword arguments passed to the Flask constructor.
        """
        super().__init__(*args, **kwargs)
        self.config.from_object(Config)
        self.limiter = Limiter(get_remote_address, default_limits=["200 per day", "50 per hour"])
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.jwt = JWTManager()
        self.mode = 'maintenance'
        
        # Import and register blueprints
        from .auth import bp as auth_bp
        self.register_blueprint(auth_bp)
        
        from .api import mc_recommendation_bp
        self.register_blueprint(mc_recommendation_bp)
        
        from .api import em_recommendation_bp
        self.register_blueprint(em_recommendation_bp)
        
        @self.route('/health', methods=['GET'])
        def health_check():
            """
            Health check endpoint for the API.

            Returns:
                JSON: Health status of the API, showing 'healthy' if in deploy mode, or the current
                operational mode otherwise.
            """
            return jsonify({
                'status': self.mode if self.mode != 'deploy' else 'healthy',
            })

    def run(self, host: str = None, port: int = None, mode: str = 'deploy', load_dotenv: bool = True, sync: bool = False, **options) -> None:
        """
        Run the RecommendationAPI server with specified host, port, and mode settings.

        Parameters:
            host (str): The IP address to bind the server. Defaults to None.
            port (int): The port on which the server will listen. Defaults to None.
            mode (str): The mode in which to run the server, one of 'deploy', 'debug', or 'maintenance'.
            load_dotenv (bool): If True, loads environment variables from .env. Defaults to True.
            **options: Additional keyword arguments passed to Flask's run method.

        Raises:
            ValueError: If the specified mode is not one of 'deploy', 'debug', or 'maintenance'.

        Returns:
            None
        """
        ALL_MODE = ['deploy', 'debug', 'maintenance']
        if sum(mode in m for m in ALL_MODE) != 1:
            raise ValueError(f'The launching mode must be in : {ALL_MODE}')
        self.mode = mode
        self.limiter.init_app(self)
        self.db.init_app(self)
        self.jwt.init_app(self)
        
        if sync:
            self.db.sync.sync_all(erase_data=True)

        return super().run(host=host, port=port, debug=mode.lower() in 'debug', load_dotenv=load_dotenv, **options)
