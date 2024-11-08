from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np
import os

from .database import Database
from ..utils import Utils


class embedder(object):
    def __init__(self, model: str = 'all-MiniLM-L6-v2', *args, **kwargs) -> None:
        self.model = SentenceTransformer(model, *args, **kwargs)

    def encode(self, obj: object, show_progress_bar: bool = True, *args, **kwargs) -> np.ndarray:
        return self.model.encode(obj, show_progress_bar=show_progress_bar, *args, **kwargs)


class local_embedder:
    def __init__(self, model: str = 'all-MiniLM-L6-v2', *args, **kwargs) -> None:
        super().__init__(model, *args, **kwargs)
        self.filext = '_embeddings.npy'

    def load_embeddings(self, path):
        """Charge les embeddings d'un fichier, ou retourne un dictionnaire vide si le fichier n'existe pas."""
        if os.path.exists(path):
            return np.load(path, allow_pickle=True).item()
        return {}

    def save_embeddings(self, embeddings, path):
        """Enregistre les embeddings dans un fichier."""
        np.save(path, embeddings)


class integrated_embedder(embedder):
    def __init__(self, db: Database, model: str = 'all-MiniLM-L6-v2', *args, **kwargs) -> None:
        super().__init__(model, *args, **kwargs)
        self.db = db


class watif_embedder(object):
    def generate_user_embeddings(self, *args, **kwargs) -> dict:
        raise NotImplementedError(
            'Must be implemented in subclass / child class.')

    def generate_post_embeddings(self, *args, **kwargs) -> dict:
        raise NotImplementedError(
            'Must be implemented in subclass / child class.')

    def generate_thread_embeddings(self, *args, **kwargs) -> dict:
        raise NotImplementedError(
            'Must be implemented in subclass / child class.')

    def generate_interest_embeddings(self, *args, **kwargs) -> dict:
        raise NotImplementedError(
            'Must be implemented in subclass / child class.')

    def generate_key_embeddings(self, *args, **kwargs) -> dict:
        raise NotImplementedError(
            'Must be implemented in subclass / child class.')

    def generate_user_embedding(self, id_user: str | int | bytes, *args, **kwargs) -> np.ndarray:
        raise NotImplementedError(
            'Must be implemented in subclass / child class.')

    def generate_post_embedding(self, id_post: str | int | bytes, *args, **kwargs) -> np.ndarray:
        raise NotImplementedError(
            'Must be implemented in subclass / child class.')

    def generate_thread_embedding(self, id_thread: str | int | bytes, *args, **kwargs) -> np.ndarray:
        raise NotImplementedError(
            'Must be implemented in subclass / child class.')

    def generate_interest_embedding(self, id_interest: str | int | bytes, *args, **kwargs) -> np.ndarray:
        raise NotImplementedError(
            'Must be implemented in subclass / child class.')

    def generate_key_embedding(self, id_key: str | int | bytes, *args, **kwargs) -> np.ndarray:
        raise NotImplementedError(
            'Must be implemented in subclass / child class.')

    def encode(self, obj: object, *args, **kwargs) -> np.ndarray | dict:
        raise NotImplementedError(
            'Must be implemented in subclass / child class.')


class watif_local_embedder(local_embedder, watif_embedder):pass


class watif_integrated_embedder(integrated_embedder, watif_embedder):pass


class MC_embedder(watif_integrated_embedder):
    def generate_user_embedding(self, id_user: str | int | bytes, follow_weight: float = 0.4, interest_weight: float = 0.4, description_weight: float = 0.2, *args, **kwargs) -> np.ndarray:
        entity = self.get_embedding('users', id_user)
        if entity: return entity["embedding"]
        
        if not np.isclose(follow_weight + interest_weight + description_weight, 1.0, rtol=1e-09, atol=1e-09):
            raise ValueError('The sum of arguments follow_weight, interest_weight and description_weight must be 1.0')
        
        user = self.db.mongo_db['users'].find_one({"_id": id_user})
        return Utils.array_avg(
            Utils.array_avg(
                self.generate_interest_embedding(id_interest, *args, **kwargs)
                for id_interest in user['interests']
            ),
            self.model.encode(
                user['description'], *args, **kwargs
            ) * description_weight,
            Utils.array_avg(
                self.generate_user_embedding(id_user, *args, **kwargs)
                for id_user in user['follow']
            ) * follow_weight
        )

    def generate_post_embedding(self, id_post: str | int | bytes, key_weight: float = 0.35, title_weight: float = 0.35, content_weight: float = 0.2, author_weight: float = 0.1, *args, **kwargs) -> np.ndarray:
        entity = self.get_embedding('posts', id_post)
        if entity: return entity["embedding"]
        
        if not np.isclose(key_weight + title_weight + content_weight + author_weight, 1.0, rtol=1e-09, atol=1e-09):
            raise ValueError('The sum of arguments key_weight, title_weight, content_weight and author_weight must be 1.0')
        
        post = self.db.mongo_db['posts'].find_one({"_id": id_post})
        return Utils.array_avg(
            Utils.array_avg(
                self.generate_key_embedding(id_key, *args, **kwargs)
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
            self.generate_user_embedding(
                post['id_author'],
                *args, **kwargs
            ) * author_weight
        )

    def generate_thread_embedding(self, id_thread: str | int | bytes, author_weight: float = 0.1, name_weight: float = 0.1, member_weight: float = 0.4, post_weight: float = 0.4, *args, **kwargs) -> np.ndarray:
        entity = self.get_embedding('threads', id_thread)
        if entity: return entity["embedding"]
        
        if not np.isclose(author_weight + name_weight + member_weight + post_weight, 1.0, rtol=1e-09, atol=1e-09):
            raise ValueError('The sum of arguments author_weight, name_weight, member_weight and post_weight must be 1.0')
        
        thread = self.db.mongo_db['threads'].find_one({"_id": id_thread})
        return Utils.array_avg(
            self.generate_user_embedding(
                thread['id_author'],
                *args, **kwargs
            ) * author_weight,
            self.model.encode(
                sentences = thread['name'],
                prompt = 'Discussion name:\n',
                *args, **kwargs
            ),
            Utils.array_avg(
                self.generate_user_embedding(
                    id_member,
                    *args, **kwargs
                )
                for id_member in thread['members']
            ) * member_weight,
            Utils.array_avg(
                self.generate_post_embedding(
                    post['idPost'],
                    *args, **kwargs
                )
                for post in self.db.mongo_db['posts'].find({"id_thread": id_thread})
            ) * post_weight
        )

    def generate_key_embedding(self, id_key: str | int | bytes, *args, **kwargs) -> np.ndarray:
        entity = self.get_embedding('keys', id_key)
        return entity if entity else self.model.encode(entity['name'], *args, **kwargs)

    def generate_interest_embedding(self, id_interest: str | int | bytes, *args, **kwargs) -> np.ndarray:
        entity = self.get_embedding('interest', id_interest)
        return entity if entity else self.model.encode(entity['name'], *args, **kwargs)

    def generate_user_embeddings(self, *args, **kwargs) -> dict:
        return {user:
                self.generate_user_embeddings(user, *args, **kwargs)
                for user in self.db.mongo_db['users'].find(projection={'_id': 1})}

    def generate_post_embeddings(self, *args, **kwargs) -> dict:
        return {post:
                self.generate_post_embedding(post, *args, **kwargs)
                for post in self.db.mongo_db['posts'].find(projection={'_id': 1})}

    def generate_thread_embeddings(self, *args, **kwargs) -> dict:
        return {post:
                self.generate_post_embedding(post, *args, **kwargs)
                for post in self.db.mongo_db['threads'].find(projection={'_id': 1})}

    def generate_interest_embeddings(self, *args, **kwargs) -> dict:
        return {interest:
                self.generate_interest_embedding(interest, *args, **kwargs)
                for interest in self.db.mongo_db['interests'].find(projection={'_id': 1})}

    def generate_key_embeddings(self, *args, **kwargs) -> dict:
        return {key:
                self.generate_key_embedding(key, *args, **kwargs)
                for key in self.db.mongo_db['keys'].find(projection={'_id': 1})}

    def get_embedding(self, entity_type: str, entity_id: str | int | bytes) -> np.ndarray | None:
        entity = self.db.mongo_db[entity_type].find_one({"_id": entity_id}, {"embedding": 1})
        return np.array(entity.get("embedding")) if entity else None

    def encode(self, entity_type: str, entity_id: str | int | bytes, show_progress_bar: bool = True, *args, **kwargs) -> np.ndarray:
        match entity_type.lower():
            case 'key':
                return self.generate_key_embedding(entity_id, *args, **kwargs)
            case 'interest':
                return self.generate_interest_embedding(entity_id, *args, **kwargs)
            case 'user':
                return self.generate_user_embedding(entity_id, *args, **kwargs)
            case 'post':
                return self.generate_post_embedding(entity_id, *args, **kwargs)
            case 'thread':
                return self.generate_thread_embedding(entity_id, *args, **kwargs)
            case 'keys':
                return self.generate_key_embeddings(*args, **kwargs)
            case 'interests':
                return self.generate_interest_embeddings(*args, **kwargs)
            case 'users':
                return self.generate_user_embeddings(*args, **kwargs)
            case 'posts':
                return self.generate_post_embeddings(*args, **kwargs)
            case 'threads':
                return self.generate_thread_embeddings(*args, **kwargs)
            case _:
                return self.model.encode(entity_id, show_progress_bar=show_progress_bar, *args, **kwargs)
