"""
Module for managing a MongoDB test database with setup and teardown capabilities for testing purposes.

Classes:
    DatabaseTest: Handles initialization, data setup, clearing, and closing connections for a MongoDB database used in testing.

Example Usage:
    db_test = DatabaseTest()
    db_test.setup_database()  # Sets up database with initial data
    db_test.teardown_database()  # Clears all data in the test collections
    db_test.close_connection()  # Closes the connection to MongoDB
"""

from pymongo import MongoClient
from pathlib import Path
import json

class DatabaseTest:
    """
    Class for handling MongoDB test database setup, teardown, and data loading from JSON files.

    Attributes:
        client (MongoClient): Connection to the MongoDB server.
        db (Database): The MongoDB database for testing.
        collections (list[str]): List of collection names used in the database.
        data_dir (Path): Path to the directory containing JSON data files.
    """

    def __init__(self, db_name='watif'):
        """
        Initializes the DatabaseTest instance and connects to the MongoDB server.

        Parameters:
            db_name (str): The name of the database to connect to. Default is 'watif'.
        """
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[db_name]
        self.collections = ['users', 'threads', 'roles', 'posts', 'interests', 'keys']
        self.data_dir = Path(__file__).parent

    def load_json_data(self, file_name):
        """
        Loads data from a JSON file in the data directory.

        Parameters:
            file_name (str): The name of the JSON file (without extension) to load data from.

        Returns:
            dict or list: Parsed JSON data from the file.
        """
        file_path = self.data_dir / f'{file_name}.json'
        with open(file_path, 'r') as file:
            return json.load(file)

    def clear_collection(self, collection_name):
        """
        Clears all documents from a specified collection.

        Parameters:
            collection_name (str): The name of the collection to clear.
        """
        self.db[collection_name].delete_many({})

    def insert_data(self, collection_name, data):
        """
        Inserts multiple documents into a specified collection.

        Parameters:
            collection_name (str): The name of the collection to insert data into.
            data (list[dict]): List of documents to insert.
        """
        self.db[collection_name].insert_many(data)

    def setup_database(self):
        """
        Sets up the database by clearing and reloading each collection with initial data from JSON files.
        """
        for collection_name in self.collections:
            self.clear_collection(collection_name)
            data = self.load_json_data(collection_name)
            self.insert_data(collection_name, data)

    def teardown_database(self):
        """
        Clears all data from the collections in the database, effectively resetting the database.
        """
        for collection_name in self.collections:
            self.clear_collection(collection_name)

    def get_collection(self, collection_name):
        """
        Retrieves a specified collection from the database.

        Parameters:
            collection_name (str): The name of the collection to retrieve.

        Returns:
            Collection: The MongoDB collection object.
        """
        return self.db[collection_name]

    def close_connection(self):
        """
        Closes the MongoDB connection.
        """
        self.client.close()

if __name__ == '__main__':
    db_test = DatabaseTest()
    db_test.teardown_database()
    db_test.setup_database()
    print("Test database 'watif' has been set up with fresh data.")
    db_test.close_connection()
