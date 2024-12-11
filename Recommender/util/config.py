from dotenv import load_dotenv
import secrets
import os

# Load environment variables from a .env file
load_dotenv()


class Config:
    """
    Configuration class for the application settings.
    """
    SECRET_KEY = os.getenv('SECRET_KEY') if os.getenv('SECRET_KEY') and os.getenv('SECRET_KEY').lower() != 'auto' else secrets.token_urlsafe()
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT') if os.getenv('SECURITY_PASSWORD_SALT') and os.getenv('SECURITY_PASSWORD_SALT').lower() != 'auto' else secrets.token_hex(16)
    INDEPENDENT_REGISTER = str(os.getenv('INDEPENDENT_REGISTER') or 'True').lower() == 'true'
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') if os.getenv('JWT_SECRET_KEY') and os.getenv('JWT_SECRET_KEY').lower() != 'auto' else secrets.token_hex(16)
    NEO4J_URI = os.getenv('NEO4J_URI') or 'bolt://localhost:7687'
    NEO4J_USER = os.getenv('NEO4J_USER') or 'neo4j'
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD') or 'neo4j'
    NEO4J_AUTH = os.getenv('NEO4J_AUTH')
    MONGO_URI = os.getenv('MONGO_URI') or 'mongodb://localhost:27017/'
    MONGO_DB = os.getenv('MONGO_DB') or 'watif'
    NO_AUTH = bool(os.getenv('NO_AUTH'))
    authjwt_secret_key = JWT_SECRET_KEY
