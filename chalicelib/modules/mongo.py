from pymongo.mongo_client import MongoClient
from bson import ObjectId
import boto3
import os


class MongoModule:
    """Manages connections to MongoDB."""

    def __init__(self):
        """Establishes connection to MongoDB server"""
        self.is_prod = os.environ.get("ENV") == "prod"
        self.ssm_client = boto3.client("ssm")
        self.user = self.ssm_client.get_parameter(
            Name="/Zap/MONGO_ADMIN_USER", WithDecryption=True
        )["Parameter"]["Value"]
        self.password = self.ssm_client.get_parameter(
            Name="/Zap/MONGO_ADMIN_PASSWORD", WithDecryption=True
        )["Parameter"]["Value"]
        self.uri = f"mongodb+srv://{self.user}:{self.password}@cluster0.9gtht.mongodb.net/?retryWrites=true&w=majority"

        self.mongo_client = MongoClient(self.uri)

    def add_env_suffix(func):
        def wrapper(self, collection_name: str, *args, **kwargs):
            # users collection is dependent on vault so suffix should not be appended
            if collection_name == "users":
                return func(self, collection_name, *args, **kwargs)

            if self.is_prod:
                collection_name += "-prod"
            else:
                collection_name += "-dev"

            return func(self, collection_name, *args, **kwargs)

        return wrapper

    def connect(self):
        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command("ping")
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

        # store db variable
        self.vault = self.client.vault

    @add_env_suffix
    def insert_document(self, collection: str, data: dict) -> None:
        """
        Inserts a document into the specified collection.

        Args:
            collection (str): The name of the collection to insert the document into.
            data (dict): The document to insert into the collection.

        Raises:
            Exception: If an error occurs while inserting the document.
        """
        try:
            self.mongo_client.vault[collection].insert_one(data)
        except Exception as e:
            print(e)

    @add_env_suffix
    def get_all_data(self):
        """
        Fetches all data in the 'users' collection.

        Returns:
            A MongoCursor object. If no data is found, an empty cursor is returned.
        """
        try:
            self.users = self.vault.users.find()
        except Exception as e:
            print(e)
        return self.users

    @add_env_suffix
    def get_all_data_from_collection(self, collection: str):
        """Fetches all data from the specified collection."""
        if collection is None:
            raise ValueError("The 'collection' parameter cannot be None")

        try:
            # Use the specified collection to fetch data
            cursor = self.mongo_client.vault[collection].find()
            data = list(cursor)  # Convert the cursor to a list

            if data is None:
                raise ValueError("The data returned by the MongoDB client is None")

            if data:
                return data
            else:
                print(f"No data found in collection '{collection}'")
                return []

        except Exception as e:
            print(
                f"An error occurred while fetching data from collection '{collection}': {e}"
            )
            raise  # Handle the exception gracefully, you may want to log it or take other actions

    @add_env_suffix
    def update_document_by_id(
        self, collection: str, document_id: str, update_data: dict
    ):
        """
        Updates a document in the specified collection with the given ID.

        Args:
            collection (str): The name of the collection to update the document in.
            document_id (str): The ID of the document to update.
            update_data (dict): A dictionary containing the fields and values to update in the document.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        try:
            result = self.mongo_client.vault[collection].update_one(
                {"_id": ObjectId(document_id)}, {"$set": update_data}
            )
            if result.modified_count > 0:
                print(f"Document with ID {document_id} updated successfully.")
                return True
            else:
                print(f"No document with ID {document_id} found.")
                return False
        except Exception as e:
            print(
                f"An error occurred while updating document with ID {document_id}: {e}"
            )
            return False

    @add_env_suffix
    def update_document(self, collection, document_id, query):
        """
        Updates a document in the specified collection with the given ID.

        Args:
            collection (str): The name of the collection to update the document in.
            document_id (str): The ID of the document to update.
            query (dict): A dictionary containing the update operators.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        try:
            print(collection)
            result = self.mongo_client.vault[collection].update_one(
                {"_id": ObjectId(document_id)}, query
            )

            if result.matched_count > 0:
                print(f"Document with ID {document_id} updated successfully.")
                return True
            else:
                print(f"No document with ID {document_id} found.")
                return False
        except Exception as e:
            print(
                f"An error occurred while updating document with ID {document_id}: {e}"
            )
            return False


mongo_module = MongoModule()
