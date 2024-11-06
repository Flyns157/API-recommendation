from .auth_database import AuthDatabase
from .synchronizer import Synchronizer
from pymongo import MongoClient
from neo4j import GraphDatabase
from datetime import datetime
from flask import Flask

class Database(AuthDatabase):
    """
    The `Database` class manages connections to MongoDB and Neo4j databases,
    extending the `AuthDatabase` for user authentication functionalities.
    It initializes database connections and integrates with a Flask application.

    Attributes:
        mongo_client (MongoClient): The MongoDB client.
        mongo_db (Database): The MongoDB database instance.
        neo4j_driver (GraphDatabase.driver): The Neo4j driver instance.
        sync (Synchronizer): Synchronizer instance for handling data synchronization between MongoDB and Neo4j.
        app (Flask): Flask application instance for configuration.
    """
    
    def __init__(self, mongo_uri: str = None, mongo_db: str = None, neo4j_uri: str = None, neo4j_user: str = None, neo4j_password: str = None) -> None:
        """
        Initializes the `Database` instance with optional MongoDB and Neo4j connections.

        Parameters:
            mongo_uri (str, optional): URI for connecting to MongoDB.
            mongo_db (str, optional): Database name for MongoDB.
            neo4j_uri (str, optional): URI for connecting to Neo4j.
            neo4j_user (str, optional): Username for Neo4j authentication.
            neo4j_password (str, optional): Password for Neo4j authentication.
        """
        super().__init__()
        if mongo_uri and mongo_db:
            self.mongo_client = MongoClient(mongo_uri)
            self.mongo_db = self.mongo_client[mongo_db]
        if neo4j_uri:
            self.neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.sync = Synchronizer(self.mongo_client, self.neo4j_driver) if mongo_uri and mongo_db and neo4j_uri else Synchronizer()
    
    def init_app(self, app: Flask) -> None:
        """
        Configures the database connections using a Flask application's configuration.

        Parameters:
            app (Flask): The Flask application instance, from which database URIs and credentials are retrieved.
        
        Sets up MongoDB and Neo4j connections based on the Flask app's configuration, and initializes the synchronizer with these connections.
        """
        self.app = app
        self.mongo_client = MongoClient(app.config['MONGO_URI'])
        self.mongo_db = self.mongo_client[app.config['MONGO_DB']]
        self.neo4j_driver = GraphDatabase.driver(
            app.config['NEO4J_URI'], 
            auth=(app.config['NEO4J_USER'], app.config['NEO4J_PASSWORD']) if app.config.get('NEO4J_AUTH') else None
        )
        self.sync.set_conn(self.mongo_db, self.neo4j_driver)
    
    def close(self) -> None:
        """
        Closes the database connections for MongoDB and Neo4j.

        This method closes both the MongoDB and Neo4j connections and also calls the parent class's `close` method to handle any additional cleanup.
        """
        super().close()
        self.mongo_client.close()
        self.neo4j_driver.close()
