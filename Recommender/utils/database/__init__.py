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
        self.mongo_client = MongoClient(mongo_uri)
        self.mongo_db = self.mongo_client[mongo_db]
        self.neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.sync = Sincronizer(self.mongo_client, self.neo4j_driver)
    
    def init_app(self, app:Flask)->None:
        self.app = app
        self.mongo_client = MongoClient(app.config['MONGO_URI'])
        self.mongo_db = self.mongo_client['MONGO_DB']
        self.neo4j_driver = GraphDatabase.driver(app.config['NEO4J_URI'], auth=(app.config['NEO4J_USER'], app.config['NEO4J_PASSWORD']) if app.config['NEO4J_AUTH'] else None)
    
    def recommend_users(self, user_id:int)->list[int]:
        # Recommends users to follow based on shared interests or mutual connections
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (u:User {id_user: $user_id})-[:FOLLOWS]->(f:User)-[:FOLLOWS]->(rec:User)
                WHERE NOT (u)-[:FOLLOWS]->(rec) AND u.id_user <> rec.id_user
                RETURN rec.id_user AS recommended_user, COUNT(*) AS common_followers
                ORDER BY common_followers DESC LIMIT 5
            """, user_id=user_id)
            return [record['recommended_user'] for record in result]

    def recommend_posts(self, user_id:int)->list[int]:
        # Recommends posts based on interests and liked content
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (u:User {id_user: $user_id})-[:LIKES]->(:Post)-[:LIKES]-(p:Post)
                WHERE NOT (u)-[:LIKES]->(p)
                RETURN p.id_post AS recommended_post, COUNT(*) AS like_similarity
                ORDER BY like_similarity DESC LIMIT 5
            """, user_id=user_id)
            return [record['recommended_post'] for record in result]

    def recommend_threads(self, user_id:int)->list[int]:
        # Recommends threads based on user membership
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (u:User {id_user: $user_id})-[:MEMBER_OF]->(:Thread)-[:MEMBER_OF]-(t:Thread)
                WHERE NOT (u)-[:MEMBER_OF]->(t)
                RETURN t.id_thread AS recommended_thread, COUNT(*) AS common_members
                ORDER BY common_members DESC LIMIT 5
            """, user_id=user_id)
            return [record['recommended_thread'] for record in result]

    def close(self):
        # Close the connections
        self.mongo_client.close()
        self.neo4j_driver.close()
        self.conn.close()
