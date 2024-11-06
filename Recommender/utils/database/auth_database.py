"""
This module provides the AuthDatabase class, which manages user authentication data in an SQLite database.
It includes methods for creating and verifying users, as well as hashing and checking passwords.

Classes:
    - AuthDatabase: Manages user creation, password hashing, and authentication checks for a user database.
"""

import sqlite3
import bcrypt

class AuthDatabase:
    """
    AuthDatabase provides methods for managing a user database, including creating user records,
    hashing passwords, and verifying user credentials.

    Attributes:
        conn (sqlite3.Connection): The connection object for the SQLite database.
    """

    def __init__(self) -> None:
        """
        Initializes the AuthDatabase instance by connecting to the SQLite database and
        creating the users table if it doesn't already exist.
        """
        self.conn = sqlite3.connect('database')
        self.create_table()
    
    @staticmethod
    def hash_password(password: str) -> bytes:
        """
        Hashes a plain-text password using bcrypt.

        Parameters:
            password (str): The plain-text password to hash.

        Returns:
            bytes: The hashed password.
        """
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    @staticmethod
    def check_password(password: str, hashed: bytes) -> bool:
        """
        Checks a plain-text password against a hashed password.

        Parameters:
            password (str): The plain-text password to verify.
            hashed (bytes): The hashed password to check against.

        Returns:
            bool: True if the password matches the hash, False otherwise.
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    
    def create_table(self) -> None:
        """
        Creates the 'users' table in the database if it does not already exist.
        The table includes columns for a unique username and a hashed password.
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
        """
        Adds a new user to the database with a hashed password.

        Parameters:
            username (str): The unique username for the user.
            password (str): The plain-text password for the user.

        Returns:
            bool: True if the user was created successfully, False if the username already exists.
        """
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
        """
        Verifies a user's credentials by checking if the provided password matches the stored hash.

        Parameters:
            username (str): The username to verify.
            password (str): The plain-text password to check.

        Returns:
            bool: True if the username exists and the password is correct, False otherwise.
        """
        with self.conn:
            cursor = self.conn.execute("""
                SELECT password FROM users WHERE username = ?
            """, (username,))
            hashed = cursor.fetchone()
            return hashed is not None and AuthDatabase.check_password(password, hashed)
    
    def exist_user(self, username: str) -> bool:
        """
        Checks if a username exists in the database.

        Parameters:
            username (str): The username to check.

        Returns:
            bool: True if the username exists, False otherwise.
        """
        with self.conn:
            cursor = self.conn.execute("""
                SELECT * FROM users WHERE username = ?
            """, (username,))
            user = cursor.fetchone()
            return user is not None
    
    def close(self) -> None:
        """
        Closes the database connection.
        """
        self.conn.close()
