from pymongo.database import Database as MongoDatabase
from neo4j import Driver as Neo4jDriver

class Sincronizer:
    def __init__(self, mongo_db:MongoDatabase, neo4j_db:Neo4jDriver)->None:
        self.mongo_db = mongo_db
        self.neo4j_driver = neo4j_db
    
    def sync_all(self)->None:
        self.sync_posts()
        self.sync_roles()
        self.sync_threads()
        self.sync_users()
    
    def sync_roles(self)->None:
        roles = self.mongo_db['roles'].find()
        with self.neo4j_driver.session() as session:
            for role in roles:
                session.run("""
                    MERGE (r:Role {name: $name})
                    SET r.rights = $rights, r.extend = $extend
                """, name=role['name'], rights=role['right'], extend=role.get('extend', []))

    def sync_users(self)->None:
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
                description=user['description'], status=user['status'], interests=user.get('interest', []))
                
                # Handle relationships for follows and blocks
                for follow_id in user.get('follow', []):
                    session.run("MATCH (u:User {id_user: $id_user}), (f:User {id_user: $follow_id}) MERGE (u)-[:FOLLOWS]->(f)",
                                id_user=user['id_user'], follow_id=follow_id)
                
                for block_id in user.get('blocked', []):
                    session.run("MATCH (u:User {id_user: $id_user}), (b:User {id_user: $block_id}) MERGE (u)-[:BLOCKS]->(b)",
                                id_user=user['id_user'], block_id=block_id)

    def sync_posts(self)->None:
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

    def sync_threads(self)->None:
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
