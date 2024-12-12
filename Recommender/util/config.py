from dotenv import load_dotenv
from pydantic import BaseModel
import secrets
import os


# Load environment variables from a .env file
load_dotenv()


class Settings(object):
    """
    Configuration class for the application settings.
    """
    SECRET_KEY: str = os.getenv('SECRET_KEY') if os.getenv('SECRET_KEY') and os.getenv('SECRET_KEY').lower() != 'auto' else secrets.token_urlsafe()
    SECURITY_PASSWORD_SALT: str = os.getenv('SECURITY_PASSWORD_SALT') if os.getenv('SECURITY_PASSWORD_SALT') and os.getenv('SECURITY_PASSWORD_SALT').lower() != 'auto' else secrets.token_hex(16)
    INDEPENDENT_REGISTER : bool = str(os.getenv('INDEPENDENT_REGISTER') or 'True').lower() == 'true'
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY') if os.getenv('JWT_SECRET_KEY') and os.getenv('JWT_SECRET_KEY').lower() != 'auto' else secrets.token_hex(16)
    NEO4J_URI: str = os.getenv('NEO4J_URI') or 'bolt://localhost:7687'
    NEO4J_USER: str = os.getenv('NEO4J_USER') or 'neo4j'
    NEO4J_PASSWORD: str = os.getenv('NEO4J_PASSWORD') or 'neo4j'
    NEO4J_AUTH: str = os.getenv('NEO4J_AUTH')
    MONGO_URI: str = os.getenv('MONGO_URI') or 'mongodb://localhost:27017/'
    MONGO_DB: str = os.getenv('MONGO_DB') or 'watif'
    NO_AUTH: bool = bool(os.getenv('NO_AUTH'))
    authjwt_secret_key: str = os.getenv('JWT_SECRET_KEY') if os.getenv('JWT_SECRET_KEY') and os.getenv('JWT_SECRET_KEY').lower() != 'auto' else secrets.token_hex(16)
