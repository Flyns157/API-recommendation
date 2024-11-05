import sqlite3
import bcrypt

class AuthDatabase:
    def __init__(self) -> None:
        self.conn = sqlite3.connect('database')
        self.create_table()
    
    @staticmethod
    def hash_password(password:str)->bytes:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    @staticmethod
    def check_password(password:str, hashed:bytes)->bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    
    def create_table(self):
        """
        Crée la table des utilisateurs si elle n'existe pas déjà.
        """
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )
            """)

    def create_user(self, username: str, password: str) -> bool:
        try:
            with self.conn:
                self.conn.execute("""
                    INSERT INTO users (username, password) VALUES (?, ?)
                """, (username, AuthDatabase.hash_password(password)))
            print(f"Utilisateur {username} créé avec succès.")
            return True
        except sqlite3.IntegrityError:
            print(f"Erreur : Le nom d'utilisateur {username} existe déjà.")
            return False
    
    def check_user(self, username: str, password: str) -> bool:
        with self.conn:
            cursor = self.conn.execute("""
                SELECT password FROM users WHERE username = ?
            """, (username))
            hashed = cursor.fetchone()
            return hashed is not None and AuthDatabase.check_password(password, hashed)
    
    def exist_user(self, username: str) -> bool:
        with self.conn:
            cursor = self.conn.execute("""
                SELECT * FROM users WHERE username = ?
            """, (username))
            user = cursor.fetchone()
            return user is not None
