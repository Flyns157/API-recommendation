'''========================= /!\ Deprecated /!\ ========================='''

from pymongo.database import Database as MongoDatabase
from neo4j import Driver as Neo4jDriver

class Synchronizer:
    """
    Synchronizer handles data synchronization between a MongoDB database and a Neo4j database.
    
    **Deprecated**: This class is deprecated and may be reworked in future versions.

    Attributes:
        mongo_db (MongoDatabase): The MongoDB database instance.
        neo4j_driver (Neo4jDriver): The Neo4j driver instance.
    """
    
    '''========================= /!\ Deprecated /!\ ========================='''
    def __init__(self, mongo_db: MongoDatabase = None, neo4j_driver: Neo4jDriver = None) -> None:
        """
        Initializes the Synchronizer instance with optional MongoDB and Neo4j connections.

        Parameters:
            mongo_db (MongoDatabase, optional): The MongoDB database connection.
            neo4j_driver (Neo4jDriver, optional): The Neo4j driver connection.
        """
        self.set_conn(mongo_db=mongo_db, neo4j_driver=neo4j_driver)
    
    def set_conn(self, mongo_db: MongoDatabase, neo4j_driver: Neo4jDriver) -> None:
        """
        Sets the database connections for MongoDB and Neo4j.

        Parameters:
            mongo_db (MongoDatabase): The MongoDB database connection.
            neo4j_driver (Neo4jDriver): The Neo4j driver connection.
        """
        self.mongo_db = mongo_db
        self.neo4j_driver = neo4j_driver
    
    def sync_all(self) -> None:
        """
        Synchronizes data across all collections between MongoDB and Neo4j.

        This method calls `sync_posts`, `sync_roles`, `sync_threads`, and `sync_users`.
        """
        print("Data synchronization between MongoDB and Neo4j databases ", end='')
        try:
            self.sync_posts()
            self.sync_roles()
            self.sync_threads()
            self.sync_users()
            print("[SUCCESS]")
        except Exception:
            print("[FAILED]")
    
    def sync_roles(self) -> None:
        """
        Synchronizes roles from MongoDB to Neo4j.

        Each role in MongoDB is merged into Neo4j as a `Role` node, with properties for 
        `name`, `rights`, and `extend` attributes.
        """
        roles = self.mongo_db['roles'].find()
        with self.neo4j_driver.session() as session:
            for role in roles:
                session.run("""
                    MERGE (r:Role {name: $name})
                    SET r.rights = $rights, r.extend = $extend
                """, name=role['name'], rights=role['right'], extend=role.get('extend', []))

    def sync_users(self) -> None:
        """
        Synchronizes users from MongoDB to Neo4j.

        Each user in MongoDB is merged into Neo4j as a `User` node with properties for various
        attributes like `username`, `name`, `surname`, and `interests`. The method also handles
        relationships for follows and blocks among users.
        """
        users = self.mongo_db['users'].find()
        with self.neo4j_driver.session() as session:
            for user in users:
                session.run("""
                    MERGE (u:User {id_user: $id_user})
                    SET u.role = $role, u.username = $username, u.name = $name, u.surname = $surname,
                        u.birthdate = $birthdate, u.pp = $pp, u.description = $description, u.status = $status,
                        u.interests = $interests
                """, 
                id_user=user['id_user'], role=user['role'], username=user['username'],
                name=user['name'], surname=user['surname'], birthdate=user['birthdate'], pp=user['pp'],
                description=user['description'], status=user['status'], interests=user.get('interests', []))
                
                # Handle relationships for follows and blocks
                for follow_id in user.get('follow', []):
                    session.run("MATCH (u:User {id_user: $id_user}), (f:User {id_user: $follow_id}) MERGE (u)-[:FOLLOWS]->(f)",
                                id_user=user['id_user'], follow_id=follow_id)
                
                for block_id in user.get('blocked', []):
                    session.run("MATCH (u:User {id_user: $id_user}), (b:User {id_user: $block_id}) MERGE (u)-[:BLOCKS]->(b)",
                                id_user=user['id_user'], block_id=block_id)

    def sync_posts(self) -> None:
        """
        Synchronizes posts from MongoDB to Neo4j.

        Each post in MongoDB is merged into Neo4j as a `Post` node, with properties for attributes
        like `title`, `content`, and `media`. The method also handles relationships for likes and comments
        associated with each post.
        """
        posts = self.mongo_db['posts'].find()
        with self.neo4j_driver.session() as session:
            for post in posts:
                session.run("""
                    MERGE (p:Post {id_post: $id_post})
                    SET p.id_thread = $id_thread, p.id_author = $id_author, p.date = $date, 
                        p.title = $title, p.content = $content, p.media = $media, p.keys = $keys
                """,
                id_post=post['id_post'], id_thread=post['id_thread'], id_author=post['id_author'], 
                date=post['date'], title=post.get('title', ''), content=post['content'],
                media=post.get('media', []), keys=post.get('keys', []))

                # Handle likes and comments relationships
                for user_id in post.get('likes', []):
                    session.run("MATCH (u:User {id_user: $user_id}), (p:Post {id_post: $id_post}) MERGE (u)-[:LIKES]->(p)",
                                user_id=user_id, id_post=post['id_post'])
                
                for user_id in post.get('comments', []):
                    session.run("MATCH (u:User {id_user: $user_id}), (p:Post {id_post: $id_post}) MERGE (u)-[:COMMENTS]->(p)",
                                user_id=user_id, id_post=post['id_post'])

    def sync_threads(self) -> None:
        """
        Synchronizes threads from MongoDB to Neo4j.

        Each thread in MongoDB is merged into Neo4j as a `Thread` node, with properties for attributes
        like `name`, `range`, and `admins`. The method also handles membership relationships between
        users and threads.
        """
        threads = self.mongo_db['threads'].find()
        with self.neo4j_driver.session() as session:
            for thread in threads:
                session.run("""
                    MERGE (t:Thread {id_thread: $id_thread})
                    SET t.name = $name, t.range = $range, t.id_owner = $id_owner, t.admins = $admins
                """, 
                id_thread=thread['id_thread'], name=thread['name'], range=thread['range'],
                id_owner=thread['id_owner'], admins=thread.get('admins', []))

                # Handle membership relationships
                for member_id in thread.get('members', []):
                    session.run("MATCH (u:User {id_user: $member_id}), (t:Thread {id_thread: $id_thread}) MERGE (u)-[:MEMBER_OF]->(t)",
                                member_id=member_id, id_thread=thread['id_thread'])
