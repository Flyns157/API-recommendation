"""
Embedding Module for Social Media Recommendation System

This module provides various classes to handle embeddings for entities within a social media platform.
The main purpose of these embeddings is to enable personalized recommendations by calculating 
similarities between users, posts, threads, interests, and other social media entities.

Classes:
    - embedder: A base class for generating embeddings using a specified language model.
    - local_embedder: A specialized embedder that saves and loads embeddings locally from files.
    - integrated_embedder: An embedder that integrates with a Database instance for retrieving entity embeddings.
    - watif_embedder: An abstract class defining methods for getting various types of embeddings 
      (e.g., user, post, thread) but leaves implementation to child classes.
    - watif_local_embedder: Combines functionality of local_embedder and watif_embedder, managing local embeddings for each type.
    - watif_integrated_embedder: Extends integrated_embedder and watif_embedder, handling embeddings that interact with a Database instance.
    - MC_embedder: A fully integrated embedder that retrieves and processes embeddings for users, posts, and threads with 
      configurable weights for different entity attributes (e.g., interests, follow connections) to create personalized embeddings.

Functions:
    - get_user_embedding: Generates an embedding for a user, weighted by interests, follow connections, and description.
    - get_post_embedding: Generates an embedding for a post, weighted by keys, title, content, and author.
    - get_thread_embedding: Generates an embedding for a thread, weighted by attributes like author, members, and related posts.
    - get_key_embedding: Retrieves the embedding for a specific keyword.
    - get_interest_embedding: Retrieves the embedding for a specific interest.
    - get_embedding: Utility function to get an entity embedding from the database.

Examples:
    # Initialize an MC_embedder with a database instance and model
    mc_embedder = MC_embedder(db=database, model='all-MiniLM-L6-v2')

    # Generate and retrieve user embedding based on attributes and weighting
    user_embedding = mc_embedder.get_user_embedding(id_user='123', follow_weight=0.5, interest_weight=0.3, description_weight=0.2)

Requirements:
    - `numpy`: For handling embedding arrays.
    - `scikit-learn`: For cosine similarity calculations.
    - `sentence-transformers`: For the language model used to generate embeddings.

"""

from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np
import os

from .database import Database
from ..utils import Utils


class embedder(object):
    """Embedder using SentenceTransformer for encoding textual objects."""
    def __init__(self, model: str = 'all-MiniLM-L6-v2', *args, **kwargs) -> None:
        """
        Initializes the embedder with a specified model.

        Args:
            model (str): Model name for SentenceTransformer.
            *args: Additional arguments for SentenceTransformer.
            **kwargs: Additional keyword arguments for SentenceTransformer.
        """
        self.model = SentenceTransformer(model, *args, **kwargs)

    def encode(self, obj: object, show_progress_bar: bool = True, *args, **kwargs) -> np.ndarray:
        """
        Encodes an object to generate embeddings.

        Args:
            obj (object): Object to encode.
            show_progress_bar (bool): Display progress bar.
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            np.ndarray: Encoded embedding.
        """
        return self.model.encode(obj, show_progress_bar=show_progress_bar, *args, **kwargs)


class local_embedder:
    """Embedder class with local saving/loading capabilities for embeddings."""

    def __init__(self, model: str = 'all-MiniLM-L6-v2', *args, **kwargs) -> None:
        """
        Initializes the local embedder.

        Args:
            model (str): Model name for SentenceTransformer.
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(model, *args, **kwargs)
        self.filext = '_embeddings.npy'

    def load_embeddings(self, path):
        """
        Loads embeddings from a file or returns an empty dictionary if the file doesn't exist.

        Args:
            path (str): Path to the embeddings file.

        Returns:
            dict: Loaded embeddings or an empty dictionary.
        """
        if os.path.exists(path):
            return np.load(path, allow_pickle=True).item()
        return {}

    def save_embeddings(self, embeddings, path):
        """
        Saves embeddings to a file.

        Args:
            embeddings (dict): Embeddings to save.
            path (str): Path to the output file.
        """
        np.save(path, embeddings)


class integrated_embedder(embedder):
    """Embedder that integrates with a database for storing embeddings."""

    def __init__(self, db: Database, model: str = 'all-MiniLM-L6-v2', *args, **kwargs) -> None:
        """
        Initializes the integrated embedder with database access.

        Args:
            db (Database): Database instance.
            model (str): Model name for SentenceTransformer.
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(model, *args, **kwargs)
        self.db = db


class watif_embedder(object):
    """Abstract class defining methods to retrieve specific entity embeddings."""

    def get_user_embeddings(self, *args, **kwargs) -> dict:
        raise NotImplementedError('Must be implemented in subclass / child class.')

    def get_post_embeddings(self, *args, **kwargs) -> dict:
        raise NotImplementedError('Must be implemented in subclass / child class.')

    def get_thread_embeddings(self, *args, **kwargs) -> dict:
        raise NotImplementedError('Must be implemented in subclass / child class.')

    def get_interest_embeddings(self, *args, **kwargs) -> dict:
        raise NotImplementedError('Must be implemented in subclass / child class.')

    def get_key_embeddings(self, *args, **kwargs) -> dict:
        raise NotImplementedError('Must be implemented in subclass / child class.')

    def get_user_embedding(self, id_user: str | int | bytes, *args, **kwargs) -> np.ndarray:
        raise NotImplementedError('Must be implemented in subclass / child class.')

    def get_post_embedding(self, id_post: str | int | bytes, *args, **kwargs) -> np.ndarray:
        raise NotImplementedError('Must be implemented in subclass / child class.')

    def get_thread_embedding(self, id_thread: str | int | bytes, *args, **kwargs) -> np.ndarray:
        raise NotImplementedError('Must be implemented in subclass / child class.')

    def get_interest_embedding(self, id_interest: str | int | bytes, *args, **kwargs) -> np.ndarray:
        raise NotImplementedError('Must be implemented in subclass / child class.')

    def get_key_embedding(self, id_key: str | int | bytes, *args, **kwargs) -> np.ndarray:
        raise NotImplementedError('Must be implemented in subclass / child class.')

    def encode(self, obj: object, *args, **kwargs) -> np.ndarray | dict:
        raise NotImplementedError('Must be implemented in subclass / child class.')


class watif_local_embedder(local_embedder, watif_embedder):
    """Combines local_embedder and watif_embedder to store and retrieve entity embeddings locally."""
    pass


class watif_integrated_embedder(integrated_embedder, watif_embedder):
    """Combines integrated_embedder and watif_embedder for entity embedding management with database integration."""
    pass



class MC_embedder(watif_integrated_embedder):
    """
    Embedder class responsible for generating and managing embeddings for social media entities such as users, posts, threads, and interests.
    The embeddings are weighted based on configurable attributes like followings, interests, descriptions, and content. 

    Attributes:
        db (Database): A database instance to interact with MongoDB collections.
        model (sentence-transformers.Model): A model instance used for encoding textual information into embeddings.
        
    Methods:
        get_user_embedding(id_user, follow_weight, interest_weight, description_weight, *args, **kwargs):
            Generates a weighted user embedding based on user interests, followings, and description.
        
        get_post_embedding(id_post, key_weight, title_weight, content_weight, author_weight, *args, **kwargs):
            Generates a weighted post embedding based on the post's keys, title, content, and author.

        get_thread_embedding(id_thread, author_weight, name_weight, member_weight, post_weight, *args, **kwargs):
            Generates a weighted thread embedding based on thread's author, name, members, and posts.

        get_key_embedding(id_key, *args, **kwargs):
            Retrieves or generates an embedding for a key entity.

        get_interest_embedding(id_interest, *args, **kwargs):
            Retrieves or generates an embedding for an interest entity.

        get_user_embeddings(*args, **kwargs):
            Retrieves embeddings for all users in the database.

        get_post_embeddings(*args, **kwargs):
            Retrieves embeddings for all posts in the database.

        get_thread_embeddings(*args, **kwargs):
            Retrieves embeddings for all threads in the database.

        get_interest_embeddings(*args, **kwargs):
            Retrieves embeddings for all interests in the database.

        get_key_embeddings(*args, **kwargs):
            Retrieves embeddings for all keys in the database.

        get_embedding(entity_type, entity_id):
            Retrieves the embedding for a specific entity from the database.

        encode(entity_type, entity_id, show_progress_bar=True, *args, **kwargs):
            Encodes an entity based on its type and ID, with configurable arguments and weights for generating embeddings.
    """

    def get_user_embedding(self, id_user: str | int | bytes, follow_weight: float = 0.4, interest_weight: float = 0.4, description_weight: float = 0.2, *args, **kwargs) -> np.ndarray:
        """
        Generates a weighted user embedding based on interests, followings, and description.

        Args:
            id_user (str | int | bytes): User ID.
            follow_weight (float): Weight for followings.
            interest_weight (float): Weight for interests.
            description_weight (float): Weight for description.
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            np.ndarray: The generated user embedding as a NumPy array.
        
        Raises:
            ValueError: If the sum of `follow_weight`, `interest_weight`, and `description_weight` is not equal to 1.
        """
        entity = self.get_embedding('users', id_user)
        if "embedding" in entity: return entity["embedding"]
        
        if not np.isclose(follow_weight + interest_weight + description_weight, 1.0, rtol=1e-09, atol=1e-09):
            raise ValueError('The sum of arguments follow_weight, interest_weight and description_weight must be 1.0')
        
        user = self.db.mongo_db['users'].find_one({"_id": id_user})
        return Utils.array_avg(
            Utils.array_avg(
                self.get_interest_embedding(id_interest, *args, **kwargs)
                for id_interest in user['interests']
            ),
            self.model.encode(
                user['description'], *args, **kwargs
            ) * description_weight,
            Utils.array_avg(
                self.get_user_embedding(id_user, *args, **kwargs)
                for id_user in user['follow']
            ) * follow_weight
        )

    def get_post_embedding(self, id_post: str | int | bytes, key_weight: float = 0.35, title_weight: float = 0.35, content_weight: float = 0.2, author_weight: float = 0.1, *args, **kwargs) -> np.ndarray:
        """
        Generates a weighted post embedding based on the post's keys, title, content, and author.

        Args:
            id_post (str | int | bytes): Post ID.
            key_weight (float): Weight for keys associated with the post.
            title_weight (float): Weight for the title of the post.
            content_weight (float): Weight for the content of the post.
            author_weight (float): Weight for the author of the post.
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            np.ndarray: The generated post embedding as a NumPy array.
        
        Raises:
            ValueError: If the sum of `key_weight`, `title_weight`, `content_weight`, and `author_weight` is not equal to 1.
        """
        entity = self.get_embedding('posts', id_post)
        if "embedding" in entity: return entity["embedding"]
        
        if not np.isclose(key_weight + title_weight + content_weight + author_weight, 1.0, rtol=1e-09, atol=1e-09):
            raise ValueError('The sum of arguments key_weight, title_weight, content_weight and author_weight must be 1.0')
        
        post = self.db.mongo_db['posts'].find_one({"_id": id_post})
        return Utils.array_avg(
            Utils.array_avg(
                self.get_key_embedding(id_key, *args, **kwargs)
                for id_key in post['keys']
            ) * key_weight,
            self.model.encode(
                sentences = post['title'],
                prompt = 'Titre:\n',
                *args, **kwargs
            ) * title_weight,
            self.model.encode(
                sentences = post['content'],
                prompt = 'Content:\n',
                *args, **kwargs
            ) * content_weight,
            self.get_user_embedding(
                post['id_author'],
                *args, **kwargs
            ) * author_weight
        )

    def get_thread_embedding(self, id_thread: str | int | bytes, author_weight: float = 0.1, name_weight: float = 0.1, member_weight: float = 0.4, post_weight: float = 0.4, *args, **kwargs) -> np.ndarray:
        """
        Generates a weighted thread embedding based on author, name, members, and posts in the thread.

        Args:
            id_thread (str | int | bytes): Thread ID.
            author_weight (float): Weight for the thread's author.
            name_weight (float): Weight for the thread's name.
            member_weight (float): Weight for the members of the thread.
            post_weight (float): Weight for posts in the thread.
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            np.ndarray: The generated thread embedding as a NumPy array.
        
        Raises:
            ValueError: If the sum of `author_weight`, `name_weight`, `member_weight`, and `post_weight` is not equal to 1.
        """
        entity = self.get_embedding('threads', id_thread)
        if "embedding" in entity: return entity["embedding"]
        
        if not np.isclose(author_weight + name_weight + member_weight + post_weight, 1.0, rtol=1e-09, atol=1e-09):
            raise ValueError('The sum of arguments author_weight, name_weight, member_weight and post_weight must be 1.0')
        
        thread = self.db.mongo_db['threads'].find_one({"_id": id_thread})
        return Utils.array_avg(
            self.get_user_embedding(
                thread['id_author'],
                *args, **kwargs
            ) * author_weight,
            self.model.encode(
                sentences = thread['name'],
                prompt = 'Discussion name:\n',
                *args, **kwargs
            ),
            Utils.array_avg(
                self.get_user_embedding(
                    id_member,
                    *args, **kwargs
                )
                for id_member in thread['members']
            ) * member_weight,
            Utils.array_avg(
                self.get_post_embedding(
                    post['idPost'],
                    *args, **kwargs
                )
                for post in self.db.mongo_db['posts'].find({"id_thread": id_thread})
            ) * post_weight
        )

    def get_key_embedding(self, id_key: str | int | bytes, *args, **kwargs) -> np.ndarray:
        """
        Retrieves or generates an embedding for a key entity.

        Args:
            id_key (str | int | bytes): Key ID.
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            np.ndarray: The generated or retrieved key embedding as a NumPy array.
        """
        entity = self.get_embedding('keys', id_key)
        return entity["embedding"] if "embedding" in entity else self.model.encode(entity['name'], *args, **kwargs)

    def get_interest_embedding(self, id_interest: str | int | bytes, *args, **kwargs) -> np.ndarray:
        """
        Retrieves or generates an embedding for an interest entity.

        Args:
            id_interest (str | int | bytes): Interest ID.
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            np.ndarray: The generated or retrieved interest embedding as a NumPy array.
        """
        entity = self.get_embedding('interest', id_interest)
        return entity["embedding"] if "embedding" in entity else self.model.encode(entity['name'], *args, **kwargs)

    def get_user_embeddings(self, *args, **kwargs) -> dict:
        """
        Retrieves embeddings for all users in the database.

        Args:
            *args: Additional arguments to pass to the embedding generation process.
            **kwargs: Additional keyword arguments for embedding generation.

        Returns:
            dict: A dictionary with user IDs as keys and their embeddings (np.ndarray) as values.
        """
        return {user:
                self.get_user_embeddings(user, *args, **kwargs)
                for user in self.db.mongo_db['users'].find(projection={'_id': 1})}

    def get_post_embeddings(self, *args, **kwargs) -> dict:
        """
        Retrieves embeddings for all posts in the database.

        Args:
            *args: Additional arguments to pass to the embedding generation process.
            **kwargs: Additional keyword arguments for embedding generation.

        Returns:
            dict: A dictionary with post IDs as keys and their embeddings (np.ndarray) as values.
        """
        return {post:
                self.get_post_embedding(post, *args, **kwargs)
                for post in self.db.mongo_db['posts'].find(projection={'_id': 1})}

    def get_thread_embeddings(self, *args, **kwargs) -> dict:
        """
        Retrieves embeddings for all threads in the database.

        Args:
            *args: Additional arguments to pass to the embedding generation process.
            **kwargs: Additional keyword arguments for embedding generation.

        Returns:
            dict: A dictionary with thread IDs as keys and their embeddings (np.ndarray) as values.
        """
        return {post:
                self.get_post_embedding(post, *args, **kwargs)
                for post in self.db.mongo_db['threads'].find(projection={'_id': 1})}

    def get_interest_embeddings(self, *args, **kwargs) -> dict:
        """
        Retrieves embeddings for all interests in the database.

        Args:
            *args: Additional arguments to pass to the embedding generation process.
            **kwargs: Additional keyword arguments for embedding generation.

        Returns:
            dict: A dictionary with interest IDs as keys and their embeddings (np.ndarray) as values.
        """
        return {interest:
                self.get_interest_embedding(interest, *args, **kwargs)
                for interest in self.db.mongo_db['interests'].find(projection={'_id': 1})}

    def get_key_embeddings(self, *args, **kwargs) -> dict:
        """
        Retrieves embeddings for all keywords in the database.

        Args:
            *args: Additional arguments to pass to the embedding generation process.
            **kwargs: Additional keyword arguments for embedding generation.

        Returns:
            dict: A dictionary with keyword IDs as keys and their embeddings (np.ndarray) as values.
        """
        return {key:
                self.get_key_embedding(key, *args, **kwargs)
                for key in self.db.mongo_db['keys'].find(projection={'_id': 1})}

    def get_embedding(self, entity_type: str, entity_id: str | int | bytes) -> np.ndarray | None:
        """
        Retrieves embedding for a specific entity from the database.

        Args:
            entity_type (str): Type of entity (e.g., 'user', 'post', 'thread').
            entity_id (str | int | bytes): Entity ID.

        Returns:
            np.ndarray | None: Retrieved embedding or None if not found.
        """
        entity = self.db.mongo_db[entity_type].find_one({"_id": entity_id}, {"embedding": 1})
        return np.array(entity.get("embedding")) if entity else None

    def encode(self, entity_type: str, entity_id: str | int | bytes, show_progress_bar: bool = True, *args, **kwargs) -> np.ndarray:
        """
        Encodes an entity based on type and ID, using specified weights if needed.

        Args:
            entity_type (str): Type of entity.
            entity_id (str | int | bytes): Entity ID.
            show_progress_bar (bool): Display progress bar.
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            np.ndarray: Encoded embedding.
        """
        match entity_type.lower():
            case 'key':
                return self.get_key_embedding(entity_id, *args, **kwargs)
            case 'interest':
                return self.get_interest_embedding(entity_id, *args, **kwargs)
            case 'user':
                return self.get_user_embedding(entity_id, *args, **kwargs)
            case 'post':
                return self.get_post_embedding(entity_id, *args, **kwargs)
            case 'thread':
                return self.get_thread_embedding(entity_id, *args, **kwargs)
            case 'keys':
                return self.get_key_embeddings(*args, **kwargs)
            case 'interests':
                return self.get_interest_embeddings(*args, **kwargs)
            case 'users':
                return self.get_user_embeddings(*args, **kwargs)
            case 'posts':
                return self.get_post_embeddings(*args, **kwargs)
            case 'threads':
                return self.get_thread_embeddings(*args, **kwargs)
            case _:
                return self.model.encode(entity_id, show_progress_bar=show_progress_bar, *args, **kwargs)
