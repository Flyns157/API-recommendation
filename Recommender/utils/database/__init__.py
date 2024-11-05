from .auth_database import AuthDatabase
from .sincronizer import Sincronizer
from pymongo import MongoClient
from neo4j import GraphDatabase
from datetime import datetime
from flask import Flask

class Database(AuthDatabase):
    def __init__(self, mongo_uri:str=None, mongo_db:str=None, neo4j_uri:str=None, neo4j_user:str=None, neo4j_password:str=None)->None:
        # Initialize connections to MongoDB and Neo4j
        super()
        if mongo_uri and mongo_db:
            self.mongo_client = MongoClient(mongo_uri)
            self.mongo_db = self.mongo_client[mongo_db]
        if neo4j_uri:
            self.neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            self.sync = Sincronizer(self.mongo_client, self.neo4j_driver)
    
    def init_app(self, app:Flask)->None:
        self.app = app
        self.mongo_client = MongoClient(app.config['MONGO_URI'])
        self.mongo_db = self.mongo_client['MONGO_DB']
        self.neo4j_driver = GraphDatabase.driver(app.config['NEO4J_URI'], auth=(app.config['NEO4J_USER'], app.config['NEO4J_PASSWORD']) if app.config['NEO4J_AUTH'] else None)
    
    def close(self):
        # Close the connections
        self.mongo_client.close()
        self.neo4j_driver.close()
        self.conn.close()
