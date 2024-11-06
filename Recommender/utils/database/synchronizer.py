"""========================= /!\\ In Rework /!\\ ========================="""

from pymongo.database import Database as MongoDatabase
from neo4j import Driver as Neo4jDriver

class Synchronizer:
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
        
    def _create_constraints(self):
        """Create necessary constraints in Neo4j."""
        with self.neo4j_driver.session() as session:
            # Create constraints for unique IDs
            constraints = [
                "CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id_user IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Post) REQUIRE p.id_post IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Thread) REQUIRE t.id_thread IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (k:Key) REQUIRE k.id_key IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (r:Role) REQUIRE r.name IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (i:Interest) REQUIRE i.id_interest IS UNIQUE"
            ]
            for constraint in constraints:
                session.run(constraint)

    def sync_users(self):
        """Synchronize users from MongoDB to Neo4j."""
        users = self.mongo_db.users.find()
        
        with self.neo4j_driver.session() as session:
            for user in users:
                # Create user node
                create_user = """
                MERGE (u:User {id_user: $id_user})
                SET u += $properties
                """
                properties = {k: v for k, v in user.items() if k not in ['_id', 'id_user', 'follow', 'blocked', 'interests', 'role']}
                session.run(create_user, id_user=str(user['_id']), properties=properties)

                session.run("""
                    MATCH (u:User {id_user: $user_id})
                    MATCH (r:Role {name: $role_name})
                    MERGE (u)-[:HAS_ROLE]->(r)
                    """, user_id=str(user['_id']), role_name=user['role'])

                # Create relationships
                if 'follow' in user:
                    for followed_id in user['follow']:
                        session.run("""
                        MATCH (u1:User {id_user: $user_id})
                        MATCH (u2:User {id_user: $followed_id})
                        MERGE (u1)-[:FOLLOWS]->(u2)
                        """, user_id=str(user['_id']), followed_id=followed_id)

                if 'blocked' in user:
                    for blocked_id in user['blocked']:
                        session.run("""
                        MATCH (u1:User {id_user: $user_id})
                        MATCH (u2:User {id_user: $blocked_id})
                        MERGE (u1)-[:BLOCKS]->(u2)
                        """, user_id=str(user['_id']), blocked_id=blocked_id)

                if 'interests' in user:
                    for interest_id in user['interests']:
                        session.run("""
                        MATCH (u:User {id_user: $user_id})
                        MATCH (k:Interest {id_interest: $key_id})
                        MERGE (u)-[:INTERESTED_IN]->(k)
                        """, user_id=str(user['_id']), key_id=interest_id)

    def sync_roles(self):
        """Synchronize roles from MongoDB to Neo4j."""
        roles = self.mongo_db.roles.find()
        
        with self.neo4j_driver.session() as session:
            for role in roles:
                # Create role node
                create_role = """
                MERGE (r:Role {name: $name})
                SET r += $properties
                """
                properties = {k: v for k, v in role.items() if k not in ['_id', 'name', 'extend']}
                session.run(create_role, name=role['name'], properties=properties)

                # Create extend relationships
                if 'extend' in role:
                    for extended_role in role['extend']:
                        session.run("""
                        MATCH (r1:Role {name: $role_name})
                        MATCH (r2:Role {name: $extended_name})
                        MERGE (r1)-[:EXTENDS]->(r2)
                        """, role_name=role['name'], extended_name=extended_role)

    def sync_threads(self):
        """Synchronize threads from MongoDB to Neo4j."""
        threads = self.mongo_db.threads.find()
        
        with self.neo4j_driver.session() as session:
            for thread in threads:
                # Create thread node
                create_thread = """
                MERGE (t:Thread {id_thread: $id_thread})
                SET t += $properties
                """
                properties = {k: v for k, v in thread.items() if k not in ['_id', 'id_thread', 'members', 'id_owner', 'admins']}
                session.run(create_thread, id_thread=str(thread['_id']), properties=properties)

                # Create relationships
                # Owner relationship
                session.run("""
                MATCH (u:User {id_user: $owner_id})
                MATCH (t:Thread {id_thread: $thread_id})
                MERGE (u)-[:OWNS]->(t)
                """, owner_id=thread['id_owner'], thread_id=str(thread['_id']))

                # Members relationship
                for member_id in thread['members']:
                    session.run("""
                    MATCH (u:User {id_user: $member_id})
                    MATCH (t:Thread {id_thread: $thread_id})
                    MERGE (u)-[:MEMBER_OF]->(t)
                    """, member_id=member_id, thread_id=str(thread['_id']))

                # Admins relationship
                for admin_id in thread['admins']:
                    session.run("""
                    MATCH (u:User {id_user: $admin_id})
                    MATCH (t:Thread {id_thread: $thread_id})
                    MERGE (u)-[:ADMIN_OF]->(t)
                    """, admin_id=admin_id, thread_id=str(thread['_id']))

    def sync_posts(self):
        """Synchronize posts from MongoDB to Neo4j."""
        posts = self.mongo_db.posts.find()
        
        with self.neo4j_driver.session() as session:
            for post in posts:
                # Create post node
                create_post = """
                MERGE (p:Post {id_post: $id_post})
                SET p += $properties
                """
                properties = {k: v for k, v in post.items() if k not in ['_id', 'id_post', 'id_thread', 'id_author', 'keys', 'likes', 'comments']}
                session.run(create_post, id_post=str(post['_id']), properties=properties)

                # Create relationships
                # Author relationship
                session.run("""
                MATCH (u:User {id_user: $author_id})
                MATCH (p:Post {id_post: $post_id})
                MERGE (u)-[:AUTHORED]->(p)
                """, author_id=post['id_author'], post_id=str(post['_id']))

                # Thread relationship
                session.run("""
                MATCH (t:Thread {id_thread: $thread_id})
                MATCH (p:Post {id_post: $post_id})
                MERGE (p)-[:POSTED_IN]->(t)
                """, thread_id=post['id_thread'], post_id=str(post['_id']))

                # Keys relationship
                for key_id in post.get('keys', []):
                    session.run("""
                    MATCH (p:Post {id_post: $post_id})
                    MATCH (k:Key {id_key: $key_id})
                    MERGE (p)-[:TAGGED_WITH]->(k)
                    """, post_id=str(post['_id']), key_id=key_id)

                # Likes relationship
                for liker_id in post.get('likes', []):
                    session.run("""
                    MATCH (u:User {id_user: $liker_id})
                    MATCH (p:Post {id_post: $post_id})
                    MERGE (u)-[:LIKES]->(p)
                    """, liker_id=liker_id, post_id=str(post['_id']))

                # Comments relationship
                for commenter_id in post.get('comments', []):
                    session.run("""
                    MATCH (u:User {id_user: $commenter_id})
                    MATCH (p:Post {id_post: $post_id})
                    MERGE (u)-[:COMMENTED_ON]->(p)
                    """, commenter_id=commenter_id, post_id=str(post['_id']))

    def sync_keys(self):
        """Synchronize keys from MongoDB to Neo4j."""
        keys = self.mongo_db.keys.find()
        
        with self.neo4j_driver.session() as session:
            for key in keys:
                # Create key node
                create_key = """
                MERGE (k:Key {id_key: $id_key})
                SET k += $properties
                """
                properties = {k: v for k, v in key.items() if k not in ['_id', 'id_key']}
                session.run(create_key, id_key=str(key['_id']), properties=properties)

    def sync_interests(self):
        """Synchronize interests from MongoDB to Neo4j."""
        interests = self.mongo_db.interests.find()
        
        with self.neo4j_driver.session() as session:
            for interest in interests:
                # Create interest node
                create_interest = """
                MERGE (i:Interest {id_interest: $id_interest})
                SET i += $properties
                """
                properties = {k: v for k, v in interest.items() if k not in ['_id', 'id_interest']}
                session.run(create_interest, id_interest=str(interest['_id']), properties=properties)

    def erase_all_data(self):
        """
        Erase all data from the Neo4j database.
        """
        with self.neo4j_driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def synchronize(self):
        """Run the synchronization process for all entities."""
        self._create_constraints()
        self.sync_roles()
        self.sync_interests()
        self.sync_keys()
        self.sync_users()
        self.sync_threads()
        self.sync_posts()
    
    def sync_all(self) -> None:
        """
        Synchronizes data across all collections between MongoDB and Neo4j.

        This method calls `sync_posts`, `sync_roles`, `sync_threads`, and `sync_users`.
        """
        print("Data synchronization between MongoDB and Neo4j databases ", end='')
        try:
            self.erase_all_data()
            self.synchronize()
            print("[SUCCESS]")
        except Exception as e:
            print(f"[FAILED]\n - {e}")
