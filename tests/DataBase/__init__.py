from pymongo import MongoClient
from pathlib import Path
import json

class DatabaseTest:
    def __init__(self, db_name='watif'):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[db_name]
        self.collections = ['users', 'threads', 'roles', 'posts', 'interests', 'keys']
        self.data_dir = Path(__file__).parent

    def load_json_data(self, file_name):
        file_path = self.data_dir / f'{file_name}.json'
        with open(file_path, 'r') as file:
            return json.load(file)

    def clear_collection(self, collection_name):
        self.db[collection_name].delete_many({})

    def insert_data(self, collection_name, data):
        self.db[collection_name].insert_many(data)

    def setup_database(self):
        for collection_name in self.collections:
            self.clear_collection(collection_name)
            data = self.load_json_data(collection_name)
            self.insert_data(collection_name, data)

    def teardown_database(self):
        for collection_name in self.collections:
            self.clear_collection(collection_name)

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def close_connection(self):
        self.client.close()

if __name__ == '__main__':
    db_test = DatabaseTest()
    db_test.setup_database()
    print("Test database 'watif' has been set up with fresh data.")
    db_test.close_connection()
