"""
This module defines the structure and implementation of a recommendation engine for social networks,
focused on suggesting users, posts, and threads based on shared connections and interests. It
provides an abstract base class `recommender_engine` with unimplemented recommendation methods,
and two concrete classes, `MC_engine` and `JA_engine`, each with distinct recommendation strategies.

Classes:
    recommender_engine: Abstract base class for building a recommendation engine. Provides method
        templates for recommending users, posts, and threads.
    MC_engine: Monte Carlo-based implementation of `recommender_engine`. Suggests users, posts, and
        threads based on mutual connections and engagement patterns.
    JA_engine: A recommendation engine implementation that uses a combination of mutual follows and
        interest-based scores. Provides additional methods for fetching user hashtags and calculating
        recommendation scores.

Usage:
    Create an instance of `Database`, pass it to an `MC_engine` or `JA_engine` instance, and call the
    relevant recommendation methods. For example, `recommend_users(user_id)`, `recommend_posts(user_id)`,
    or `recommend_threads(user_id)`.
"""

from .database import Database

import numpy as np
import random

class recommender_engine:
    """
    Base class for a recommendation engine in a social network, providing a structure for generating
    recommendations of users, posts, and threads based on various criteria. This class must be extended
    with implementations of the recommendation methods.

    Attributes:
        db (Database): Database instance used for Neo4j interactions.
    """
    
    def __init__(self, db: Database) -> None:
        """
        Initializes the recommender engine with a database connection.

        Parameters:
            db (Database): The Database instance for accessing Neo4j data.
        """
        self.db = db
    
    def recommend_users(self, user_id: str) -> list[str]:
        """
        Recommends users for a specified user to follow. To be implemented in a subclass.

        Parameters:
            user_id (str): The unique identifier of the user for whom recommendations are being generated.

        Returns:
            list[int]: List of recommended user IDs.
        
        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError('Must be implemented in subclass / child class.')

    def recommend_posts(self, user_id: str) -> list[str]:
        """
        Recommends posts for a specified user based on interests and content engagement. To be implemented in a subclass.

        Parameters:
            user_id (str): The unique identifier of the user for whom recommendations are being generated.

        Returns:
            list[str]: List of recommended post IDs.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError('Must be implemented in subclass / child class.')
    
    def recommend_threads(self, user_id: str) -> list[str]:
        """
        Recommends threads for a specified user to join based on shared memberships. To be implemented in a subclass.

        Parameters:
            user_id (str): The unique identifier of the user for whom recommendations are being generated.

        Returns:
            list[str]: List of recommended thread IDs.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError('Must be implemented in subclass / child class.')

# Mattéo
# =====================================================================================================================
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

class MC_engine(recommender_engine):
    """
    Monte Carlo-based recommendation engine for suggesting users to follow, posts to view, and threads to join.
    Generates recommendations based on shared interests, mutual connections, and engagement patterns.

    Methods:
        recommend_users(user_id: str, follow_weight: float = 0.5, interest_weight: float = 0.5) -> list[str]:
            Recommends users to follow based on common followers and shared interests.

        recommend_posts(user_id: str, interest_weight: float = 0.7, interaction_weight: float = 0.3) -> list[str]:
            Recommends posts based on shared interests and past interactions.

        recommend_threads(user_id: str, member_weight: float = 0.6, interest_weight: float = 0.4) -> list[str]:
            Recommends threads to join based on shared memberships and relevant interests.
    """

    def recommend_users(self, user_id: str, follow_weight: float = 0.5, interest_weight: float = 0.5, limit: int = 10) -> list[str]:
        """
        Recommends users to follow based on common followers and shared interests.

        Parameters:
            user_id (str): The ID of the user for whom recommendations are being generated.
            follow_weight (float, optional): Weight assigned to the influence of common followers in the recommendation score.
            interest_weight (float, optional): Weight assigned to the influence of shared interests in the recommendation score.

        Returns:
            list[str]: A list of recommended user IDs, sorted by relevance.
        """
        if not np.isclose(follow_weight + interest_weight, 1.0, rtol=1e-09, atol=1e-09):
            raise ValueError('The sum of arguments follow_weight and interest_weight must be 1.0')
        with self.db.neo4j_driver.session() as session:
            scores = session.run("""
                MATCH (u:User {id_user: $user_id})-[:INTERESTED_BY]->(i:Interest)<-[:INTERESTED_BY]-(u2:User)
                WHERE u2.id_user <> $user_id
                WITH u2, COUNT(i) AS common_interests
                MATCH (u)-[:FOLLOWS]->(f:User)<-[:FOLLOWS]-(u2)
                WITH u2, common_interests, COUNT(f) AS common_follows
                RETURN u2.id_user AS user_id,
                       ($follow_weight * common_follows + $interest_weight * common_interests) AS score
                ORDER BY score DESC
                LIMIT $limit
            """, user_id=user_id, follow_weight=follow_weight, interest_weight=interest_weight, limit=limit)
            return [record["user_id"] for record in scores]

    def recommend_posts(self, user_id: str, interest_weight: float = 0.7, interaction_weight: float = 0.3, limit: int = 10) -> list[str]:
        """
        Recommends posts based on shared interests and user interactions.

        Parameters:
            user_id (str): The ID of the user for whom recommendations are being generated.
            interest_weight (float, optional): Weight assigned to the influence of shared interests in the recommendation score.
            interaction_weight (float, optional): Weight assigned to the influence of user interactions (e.g., likes, comments) in the recommendation score.

        Returns:
            list[str]: A list of recommended post IDs, sorted by relevance.
        """
        if not np.isclose(interaction_weight + interest_weight, 1.0, rtol=1e-09, atol=1e-09):
            raise ValueError('The sum of arguments interaction_weight and interest_weight must be 1.0')
        with self.db.neo4j_driver.session() as session:
            scores = session.run("""
                MATCH (u:User {id_user: $user_id})-[:INTERESTED_BY]->(i:Interest)<-[:HAS_KEY]-(p:Post)
                WITH p, COUNT(i) AS interest_score
                OPTIONAL MATCH (u)-[:LIKES|:COMMENTED_ON]->(p)
                WITH p, interest_score, COUNT(u) AS interaction_score
                RETURN p.id_post AS post_id,
                       ($interest_weight * interest_score + $interaction_weight * interaction_score) AS score
                ORDER BY score DESC
                LIMIT $limit
            """, user_id=user_id, interest_weight=interest_weight, interaction_weight=interaction_weight, limit=limit)
            return [record["post_id"] for record in scores]

    def recommend_threads(self, user_id: str, member_weight: float = 0.6, interest_weight: float = 0.4, limit: int = 10) -> list[str]:
        """
        Recommends threads to join based on shared memberships and user interests.

        Parameters:
            user_id (str): The ID of the user for whom recommendations are being generated.
            member_weight (float, optional): Weight assigned to the influence of shared memberships in the recommendation score.
            interest_weight (float, optional): Weight assigned to the influence of shared interests in the recommendation score.

        Returns:
            list[str]: A list of recommended thread IDs, sorted by relevance.
        """
        if not np.isclose(member_weight + interest_weight, 1.0, rtol=1e-09, atol=1e-09):
            raise ValueError('The sum of arguments member_weight and interest_weight must be 1.0')
        with self.db.neo4j_driver.session() as session:
            scores = session.run("""
                MATCH (u:User {id_user: $user_id})-[:MEMBER_OF]->(t:Thread)<-[:MEMBER_OF]-(u2:User)
                WITH t, COUNT(u2) AS member_score
                MATCH (u)-[:INTERESTED_BY]->(i:Interest)<-[:HAS_KEY]-(t)
                WITH t, member_score, COUNT(i) AS interest_score
                RETURN t.id_thread AS thread_id,
                       ($member_weight * member_score + $interest_weight * interest_score) AS score
                ORDER BY score DESC
                LIMIT $limit
            """, user_id=user_id, member_weight=member_weight, interest_weight=interest_weight, limit=limit)
            return [record["thread_id"] for record in scores]

# Mattéo - embedding
# =====================================================================================================================
from .embedding import MC_embedder
from .. import logger
class EM_engine(recommender_engine):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.embedder = MC_embedder(db, logger=logger)

    def _get_embedding(self, entity_type: str, entity_id: int |str | bytes) -> np.ndarray:
        """
        Retrieve the embedding vector for a given entity from MongoDB.
        
        Args:
            entity_type (str): The type of entity (e.g., 'user', 'post', 'thread').
            entity_id (str): The ID of the entity.
        
        Returns:
            np.ndarray: The embedding vector for the entity.
        """
        self.embedder.encode(entity_type, entity_id)

    def recommend_users(self, id_user, top_n=50):
        """
        Recommend users based on similarity of embeddings.
        
        Args:
            id_user (str): The ID of the user.
            top_n (int): The number of recommendations to return.

        Returns:
            list: A list of recommended user IDs.
        """
        user_embedding = self._get_embedding("users", id_user)
        if user_embedding is None:
            return []
        
        # Fetch all users' embeddings except the target user
        users = list(self.db.mongo_db["users"].find({"_id": {"$ne": id_user}}, {"_id": 1, "embedding": 1}))
        
        user_ids = []
        user_embeddings = []
        for user in users:
            if "embedding" in user:
                user_ids.append(user["_id"])
                user_embeddings.append(np.array(user["embedding"]))

        # Calculate cosine similarity between the target user and all other users
        user_embeddings = np.vstack(user_embeddings)
        similarities = cosine_similarity([user_embedding], user_embeddings).flatten()
        
        # Get top N similar users
        recommended_ids = [user_ids[i] for i in np.argsort(similarities)[-top_n:][::-1]]
        return recommended_ids

    def recommend_posts(self, id_user, top_n=50):
        """
        Recommend posts based on similarity of embeddings between user and posts.
        
        Args:
            id_user (str): The ID of the user.
            top_n (int): The number of posts to recommend.

        Returns:
            list: A list of recommended post IDs.
        """
        user_embedding = self._get_embedding("users", id_user)
        if user_embedding is None:
            return []
        
        # Fetch all posts' embeddings
        posts = list(self.db.mongo_db["posts"].find({}, {"_id": 1, "embedding": 1}))
        
        post_ids = []
        post_embeddings = []
        for post in posts:
            if "embedding" in post:
                post_ids.append(post["_id"])
                post_embeddings.append(np.array(post["embedding"]))

        # Calculate cosine similarity between the user and all posts
        post_embeddings = np.vstack(post_embeddings)
        similarities = cosine_similarity([user_embedding], post_embeddings).flatten()
        
        # Get top N similar posts
        recommended_ids = [post_ids[i] for i in np.argsort(similarities)[-top_n:][::-1]]
        return recommended_ids

    def recommend_threads(self, id_user, top_n=50):
        """
        Recommend threads based on similarity of embeddings between user and threads.
        
        Args:
            id_user (str): The ID of the user.
            top_n (int): The number of threads to recommend.

        Returns:
            list: A list of recommended thread IDs.
        """
        user_embedding = self._get_embedding("users", id_user)
        if user_embedding is None:
            return []
        
        # Fetch all threads' embeddings
        threads = list(self.db.mongo_db["threads"].find({}, {"_id": 1, "embedding": 1}))
        
        thread_ids = []
        thread_embeddings = []
        for thread in threads:
            if "embedding" in thread:
                thread_ids.append(thread["_id"])
                thread_embeddings.append(np.array(thread["embedding"]))

        # Calculate cosine similarity between the user and all threads
        thread_embeddings = np.vstack(thread_embeddings)
        similarities = cosine_similarity([user_embedding], thread_embeddings).flatten()
        
        # Get top N similar threads
        recommended_ids = [thread_ids[i] for i in np.argsort(similarities)[-top_n:][::-1]]
        return recommended_ids

# Jean-Alexis
# =====================================================================================================================
class JA_engine(recommender_engine):
    def get_hastags(self, id_user: str) -> set:
        """
        Retrieve hashtags used by a specific user.

        Args:
            id_user (str): The ID of the user.

        Returns:
            set: A set of hashtags used by the user.
        """
        with self.db.neo4j_driver.session() as session:
            hashtags = session.run(
                "MATCH (u:users),(p:posts),(k:keys) WHERE u.idUser = $id_user RETURN k.idKey AS ids",
                id_user=str(id_user)
            )
            hashtag_set = set()
            for record in hashtags:
                hashtag_set.update(record["ids"])
            return hashtag_set

    def recommend_users(self, id_user: str, follow_weight: float = 0.4, intrest_weight: float = 0.6) -> list[str]:
        """
        Generate profile recommendations for a specific user based on mutual follows and interests.

        Args:
            id_user (str): The ID of the user.
            follow_weight (float): The weight given to the follow score in the recommendation algorithm. Default is 0.4.
            intrest_weight (float): The weight given to the interest score in the recommendation algorithm. Default is 0.6.

        Returns:
            list[str]: A sorted list of recommended user IDs.

        Raises:
            ValueError: If the sum of follow_weight and intrest_weight is not equal to 1.0.

        Example:
            >>> recommender.recommend_users(123, follow_weight=0.5, intrest_weight=0.5)
            [456, 789, 1011]
        """
        if not np.isclose(follow_weight + intrest_weight, 1.0, rtol=1e-09, atol=1e-09):
            raise ValueError('The sum of arguments follow_weight and intrest_weight must be 1.0')
        with self.db.neo4j_driver.session() as session:
            user = session.run(
                "MATCH (u:users) WHERE u.idUser = $idUser RETURN u",
                id_user=str(id_user)
            ).single()

            users = session.run(
                "MATCH (u:users) WHERE u.idUser <> $idUser RETURN u",
                id_user=id_user
            )

            scores = {}
            user_follows = {rel.end_node for rel in session.run(
                "MATCH (u:users)-[f:FOLLOWS]->(f2:users) WHERE u.idUser = $id_user RETURN f2",
                id_user=id_user
            )}

            user_interests = {rel.end_node["idInterest"] for rel in session.run(
                "MATCH (u:users)-[ib:INTERESTED_BY]->(i:interests) WHERE u.idUser = $id_user RETURN i",
                id_user=id_user
            )}

            for u in users:
                u_follows = {rel.end_node for rel in session.run(
                    "MATCH (u:users)-[f:FOLLOWS]->(f2:users) WHERE u.id_user = $id_user RETURN f2",
                    id_user=u["u"]["idUser"]
                )}

                follows_score = len(user_follows & u_follows) / len(user_follows | u_follows) if user_follows and u_follows else 0

                u_interests = {rel.end_node["idInterest"] for rel in session.run(
                    "MATCH (u:users)-[ib:INTERESTED_BY]->(i:interests) WHERE u.idUser = $id_user RETURN i",
                    id_user=u["u"]["idUser"]
                )}

                interests_score = len(user_interests & u_interests) / len(user_interests | u_interests) if user_interests and u_interests else 0

                rec_score = ((follows_score*follow_weight) + (interests_score*intrest_weight)) / 2
                scores[u["u"]["idUser"]] = rec_score

            return sorted(scores, key=scores.get, reverse=True)

    def recommend_posts(self, id_user: str) -> list[str]:
        """
        Generate post recommendations for a specific user based on hashtags and interests.

        Args:
            id_user (str): The ID of the user.

        Returns:
            list: A sorted list of recommended post IDs.
        """
        with self.db.neo4j_driver.session() as session:
            posts = session.run(
                "MATCH (u:users),(p:posts) WHERE u.idUser <> $id_user RETURN p",
                id_user=str(id_user)
            )

            user_hashtags = self.get_hastags(id_user)
            scores = {}

            if not user_hashtags:
                user_interests = session.run(
                    "MATCH (u:users)-[ib:INTERESTED_BY]->(i:interests) WHERE u.idUser = $id_user RETURN i.idInterest AS interests",
                    id_user=id_user
                ).single()["interests"]

                for post in posts:
                    id_author = session.run(
                        "MATCH (u:users),(p:posts) WHERE u.idUser = $id_user RETURN u.idUser AS id",
                        id_user=str(post["idPost"])
                    ).single()["id"]

                    u = session.run(
                        "MATCH (u:users)-[ib:INTERESTED_BY]->(i:interests) WHERE u.id_user = $id_author RETURN i.idInterest AS interests",
                        id_author=id_author
                    ).single()["interests"]

                    interests_score = len(set(user_interests) & set(u)) / len(set(user_interests) | set(u))
                    scores[post["idPost"]] = interests_score
            else:
                for post in posts:
                    hashtags = session.run(
                        "MATCH (p:posts),(k:keys) WHERE p.idPost = $idPost RETURN k.idKey AS ids",
                        idPost=str(post["idPost"])
                    )
                    post_hashtags = set()
                    for record in hashtags:
                        post_hashtags.update(record["ids"])

                    score = len(user_hashtags & post_hashtags) / len(user_hashtags | post_hashtags)
                    scores[post["idPost"]] = score

            scores_tab = sorted(scores, key=scores.get, reverse=True)

            for s in range(len(scores_tab)):
                if random.random() >= 0.8:
                    scores_tab.insert(s, scores_tab[-1])
                    del scores_tab[-1]

            return scores_tab
