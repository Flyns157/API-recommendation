from .database import Database
import random

class recommender_engine:
    def __init__(self, db:Database) -> None:
        self.db = db
    
    def recommend_users(user_id:int)->list[int]:
        raise NotImplementedError('Must be implemented in subclass / child class.')

    def recommend_posts(user_id:int)->list[int]:
        raise NotImplementedError('Must be implemented in subclass / child class.')
    
    def recommend_threads(user_id:int)->list[int]:
        raise NotImplementedError('Must be implemented in subclass / child class.')

# Mattéo
# =====================================================================================================================
class MC_engine(recommender_engine):
    def recommend_users(self, user_id:int)->list[int]:
        # Recommends users to follow based on shared interests or mutual connections
        with self.db.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (u:User {id_user: $user_id})-[:FOLLOWS]->(f:User)-[:FOLLOWS]->(rec:User)
                WHERE NOT (u)-[:FOLLOWS]->(rec) AND u.id_user <> rec.id_user
                RETURN rec.id_user AS recommended_user, COUNT(*) AS common_followers
                ORDER BY common_followers DESC LIMIT 5
            """, user_id=user_id)
            return [record['recommended_user'] for record in result]

    def recommend_posts(self, user_id:int)->list[int]:
        # Recommends posts based on interests and liked content
        with self.db.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (u:User {id_user: $user_id})-[:LIKES]->(:Post)-[:LIKES]-(p:Post)
                WHERE NOT (u)-[:LIKES]->(p)
                RETURN p.id_post AS recommended_post, COUNT(*) AS like_similarity
                ORDER BY like_similarity DESC LIMIT 5
            """, user_id=user_id)
            return [record['recommended_post'] for record in result]

    def recommend_threads(self, user_id:int)->list[int]:
        # Recommends threads based on user membership
        with self.db.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (u:User {id_user: $user_id})-[:MEMBER_OF]->(:Thread)-[:MEMBER_OF]-(t:Thread)
                WHERE NOT (u)-[:MEMBER_OF]->(t)
                RETURN t.id_thread AS recommended_thread, COUNT(*) AS common_members
                ORDER BY common_members DESC LIMIT 5
            """, user_id=user_id)
            return [record['recommended_thread'] for record in result]

# Jean-Alexis
# =====================================================================================================================
class JA_engine(recommender_engine):
    def get_hastags(self, id_user:int)->set:
        """
        Retrieve hashtags used by a specific user.

        Args:
            id_user (int): The ID of the user.

        Returns:
            set: A set of hashtags used by the user.
        """
        with self.db.neo4j_driver.session() as session:
            hashtags = session.run(
                "MATCH (p:posts) WHERE p.id_author = $id_user RETURN p.keys AS hashtags",
                id_user=str(id_user)
            )
            hashtag_set = set()
            for record in hashtags:
                hashtag_set.update(record["hashtags"])
            return hashtag_set

    def recommend_users(self, id_user:int)->list[int]:
        """
        Generate profile recommendations for a specific user based on mutual follows and interests.

        Args:
            id_user (int): The ID of the user.

        Returns:
            list: A sorted list of recommended user IDs.
        """
        with self.db.neo4j_driver.session() as session:
            user = session.run(
                "MATCH (u:users) WHERE u.id_user = $id_user RETURN u",
                id_user=str(id_user)
            ).single()

            users = session.run(
                "MATCH (u:users) WHERE u.id_user <> $id_user RETURN u"
            )

            scores = {}
            user_follows = {rel.end_node for rel in session.run(
                "MATCH (u:users)-[f:FOLLOWS]->(f2:users) WHERE u.id_user = $id_user RETURN f2",
                id_user=id_user
            )}

            user_interests = set(user["u"]["interest"])

            for u in users:
                u_follows = {rel.end_node for rel in session.run(
                    "MATCH (u:users)-[f:FOLLOWS]->(f2:users) WHERE u.id_user = $id_user RETURN f2",
                    id_user=u["u"]["id_user"]
                )}

                follows_score = len(user_follows & u_follows) / len(user_follows | u_follows) if user_follows and u_follows else 0
                u_interests = set(u["u"]["interest"])
                interests_score = len(user_interests & u_interests) / len(user_interests | u_interests) if user_interests and u_interests else 0

                rec_score = ((follows_score*0.4) + (interests_score*0.6)) / 2
                scores[u["u"]["id_user"]] = rec_score

            return sorted(scores, key=scores.get, reverse=True)

    def recommend_posts(self, id_user:int)->list[int]:
        """
        Generate post recommendations for a specific user based on hashtags and interests.

        Args:
            id_user (int): The ID of the user.

        Returns:
            list: A sorted list of recommended post IDs.
        """
        with self.db.neo4j_driver.session() as session:
            posts = session.run(
                "MATCH (p:posts) WHERE p.id_author <> $id_user RETURN p",
                id_user=str(id_user)
            )

            user_hashtags = self.get_hastags(id_user)
            scores = {}

            if not user_hashtags:
                user_interests = session.run(
                    "MATCH (u:users) WHERE u.id_user = $id_user RETURN u.interests AS interests",
                    id_user=id_user
                ).single()["interests"]

                for post in posts:
                    u = session.run(
                        "MATCH (u:users) WHERE u.id_user = $id_author RETURN u.interests AS interests",
                        id_author=post["id_author"]
                    ).single()["interests"]

                    interests_score = len(set(user_interests) & set(u)) / len(set(user_interests) | set(u))
                    scores[post["id_post"]] = interests_score
            else:
                for post in posts:
                    post_hashtags = set(post["keys"])
                    score = len(user_hashtags & post_hashtags) / len(user_hashtags | post_hashtags)
                    scores[post["id_post"]] = score

            scores_tab = sorted(scores, key=scores.get, reverse=True)

            for s in range(len(scores_tab)):
                if random.random() >= 0.8:
                    scores_tab.insert(s, scores_tab[-1])
                    del scores_tab[-1]

            return scores_tab
