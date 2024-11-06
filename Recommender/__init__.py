from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager
from .utils import Database, Utils
from flask_limiter import Limiter
from flask import Flask, jsonify
from .config import Config
import logging

db = Database()

class RecommendationAPI(Flask):
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the Server instance.

        Parameters:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.config.from_object(Config)
        self.limiter = Limiter(get_remote_address, default_limits=["200 per day", "50 per hour"])
        self.db = db
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            handlers=[logging.FileHandler('gen_serv.log'), logging.StreamHandler()])
        self.logger = logging.getLogger(__name__)
        self.jwt = JWTManager()
        self.mode = 'maintenance'
        
        # Import and register blueprints
        from .auth import bp as auth_bp
        self.register_blueprint(auth_bp)
        
        from .api import recommendation_bp
        self.register_blueprint(recommendation_bp)
        
        @self.route('/health', methods=['GET'])
        def health_check():
            return jsonify({
                'status': self.mode if self.mode != 'deploy' else 'healthy',
            })

    def run(self, host: str = None, port: int = None, mode: str = 'deploy', load_dotenv: bool = True, **options) -> None:
        ALL_MODE = ['deploy', 'debug', 'maintenance']
        if sum(mode in m for m in ALL_MODE) != 1:
            raise ValueError(f'The launching mode must be in : {ALL_MODE}')
        self.mode = mode
        self.limiter.init_app(self)
        self.db.init_app(self)
        self.jwt.init_app(self)
        
        if mode == 'debug':
            self.db.sync.sync_all()

        return super().run(host=host, port=port, debug=mode.lower() in 'debug', load_dotenv=load_dotenv, **options)
