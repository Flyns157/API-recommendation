import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import os

class embedder:
    def __init__(self, user_embeddings_path='user_embeddings.npy', 
                post_embeddings_path='post_embeddings.npy', 
                thread_embeddings_path='thread_embeddings.npy', 
                interest_embeddings_path='interest_embeddings.npy', 
                key_embeddings_path='key_embeddings.npy'):
        
        # Initialisation des chemins d'embeddings
        self.user_embeddings_path = user_embeddings_path
        self.post_embeddings_path = post_embeddings_path
        self.thread_embeddings_path = thread_embeddings_path
        self.interest_embeddings_path = interest_embeddings_path
        self.key_embeddings_path = key_embeddings_path

        # Chargement des embeddings si les fichiers existent, sinon initialisation vide
        self.user_embeddings = self.load_embeddings(self.user_embeddings_path)
        self.post_embeddings = self.load_embeddings(self.post_embeddings_path)
        self.thread_embeddings = self.load_embeddings(self.thread_embeddings_path)
        self.interest_embeddings = self.load_embeddings(self.interest_embeddings_path)
        self.key_embeddings = self.load_embeddings(self.key_embeddings_path)

        # Initialisation du modèle d'embeddings
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def load_embeddings(self, path):
        """Charge les embeddings d'un fichier, ou retourne un dictionnaire vide si le fichier n'existe pas."""
        if os.path.exists(path):
            return np.load(path, allow_pickle=True).item()
        return {}

    def save_embeddings(self, embeddings, path):
        """Enregistre les embeddings dans un fichier."""
        np.save(path, embeddings)

    def generate_embedding(self, text: str) -> np.ndarray:
        return self.model.encode(text)

class interface_embedder(embedder):
    def generate_user_embeddings(self, *args, **kwargs) -> dict:
        raise NotImplementedError('Must be implemented in subclass / child class.')
    def generate_post_embeddings(self, *args, **kwargs) -> dict:
        raise NotImplementedError('Must be implemented in subclass / child class.')
    def generate_thread_embeddings(self, *args, **kwargs) -> dict:
        raise NotImplementedError('Must be implemented in subclass / child class.')
    def generate_interest_embeddings(self, *args, **kwargs) -> dict:
        raise NotImplementedError('Must be implemented in subclass / child class.')
    def generate_key_embeddings(self, *args, **kwargs) -> dict:
        raise NotImplementedError('Must be implemented in subclass / child class.')

from ..utils import Utils
class watif_embedder(interface_embedder):
    def generate_user_embeddings(self, *args, **kwargs) -> dict:
        return {user['_id']or user['idUser']:
                self.generate_user_embeddings(user)
                for user in kwargs.get('users', [])}
        
    def generate_user_embedding(self, user: dict) -> np.ndarray:
        return Utils.array_avg(
                [self.interest_embeddings[id_interest] 
                for id_interest in user['interests']] + [
                    self.generate_embedding(user['description'])
                ] + Utils.array_avg(
                    self.user_embeddings[user[id_user]]
                    for id_user in user['follow']
                )
            )

    def generate_post_embeddings(self, *args, **kwargs) -> dict:
        # TODO : complete this methode
        return {post['_id']or post['idPost']:
            self.generate_post_embedding(post)
            for post in kwargs.get('posts', [])}

    def generate_post_embedding(self, post: dict) -> np.ndarray:
        # TODO : complete this methode
        return Utils.array_avg(
                [
                    self.key_embeddings[id_key] for id_key in post['keys']
                ] + [
                    self.generate_embedding(f'Titre:\n{post['title']}.\nContent:\n{post['content']}'),
                    self.user_embeddings[post['idAuthor']]
                ]
            )

    def generate_thread_embeddings(self, *args, **kwargs) -> dict:
        # TODO : complete this methode
        return {post['_id']or post['idPost']:
            self.generate_post_embedding(post)
            for post in kwargs.get('threads', [])}

    def generate_thread_embedding(self, thread: dict, posts: list[dict]) -> np.ndarray:
        # TODO : complete this methode
        return Utils.array_avg(
                [
                    self.user_embeddings[id_member]
                    for id_member in thread['members']
                ] + [
                    self.post_embeddings[post['idPost']] for post in posts if post['idThread']
                ]
            )

    def generate_interest_embeddings(self, *args, **kwargs) -> dict:
        return {interest['_id']or interest['idInterest']:self.generate_embedding(interest['name'])for interest in args[0]}

    def generate_key_embeddings(self, *args, **kwargs) -> dict:
        return {key['_id']or key['idKey']:self.generate_embedding(key['name'])for key in args[0]}



















    def recommend_users(self, id_user, top_n=10):
        """Recommande des utilisateurs similaires à un utilisateur donné en utilisant les embeddings."""
        user_embedding = self.user_embeddings.get(id_user)
        if user_embedding is None:
            raise ValueError(f"Embedding introuvable pour l'utilisateur {id_user}")

        all_users = list(self.user_embeddings.keys())
        all_embeddings = np.array(list(self.user_embeddings.values()))
        similarities = cosine_similarity([user_embedding], all_embeddings)[0]

        similar_users = sorted(zip(all_users, similarities), key=lambda x: x[1], reverse=True)
        return [user_id for user_id, _ in similar_users[:top_n] if user_id != id_user]

    def recommend_posts(self, id_user, top_n=10):
        """Recommande des posts pertinents pour un utilisateur donné."""
        user_embedding = self.user_embeddings.get(id_user)
        if user_embedding is None:
            raise ValueError(f"Embedding introuvable pour l'utilisateur {id_user}")

        all_posts = list(self.post_embeddings.keys())
        all_embeddings = np.array(list(self.post_embeddings.values()))
        similarities = cosine_similarity([user_embedding], all_embeddings)[0]

        similar_posts = sorted(zip(all_posts, similarities), key=lambda x: x[1], reverse=True)
        return [post_id for post_id, _ in similar_posts[:top_n]]

    def recommend_threads(self, id_user, top_n=10):
        """Recommande des threads pertinents pour un utilisateur donné."""
        user_embedding = self.user_embeddings.get(id_user)
        if user_embedding is None:
            raise ValueError(f"Embedding introuvable pour l'utilisateur {id_user}")

        all_threads = list(self.thread_embeddings.keys())
        all_embeddings = np.array(list(self.thread_embeddings.values()))
        similarities = cosine_similarity([user_embedding], all_embeddings)[0]

        similar_threads = sorted(zip(all_threads, similarities), key=lambda x: x[1], reverse=True)
        return [thread_id for thread_id, _ in similar_threads[:top_n]]
