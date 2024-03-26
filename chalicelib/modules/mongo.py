from pymongo.mongo_client import MongoClient
from bson import ObjectId
import boto3


class MongoModule:
    """Manages connections to MongoDB."""

    def __init__(self):
        """Establishes connection to MongoDB server"""
        self.ssm_client = boto3.client("ssm")
        self.user = self.ssm_client.get_parameter(
            Name="/Zap/MONGO_ADMIN_USER", WithDecryption=True
        )["Parameter"]["Value"]
        self.password = self.ssm_client.get_parameter(
            Name="/Zap/MONGO_ADMIN_PASSWORD", WithDecryption=True
        )["Parameter"]["Value"]
        self.uri = f"mongodb+srv://{self.user}:{self.password}@cluster0.9gtht.mongodb.net/?retryWrites=true&w=majority"

        self.mongo_client = MongoClient(self.uri)

    def connect(self):
        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command("ping")
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

        # store db variable
        self.vault = self.client.vault

    def get_all_data(self):
        """fetches all data in specified collection"""
        try:
            self.users = self.vault.users.find()  # parameterize this
            # assert(self.users.count() != 0)   # this doesn't work, fix silent failure!!
        except Exception as e:
            print(e)
        # for u in self.users:
        #    print(u)
        return self.users

    def get_all_data_from_collection(self, collection: str):
        """Fetches all data from the specified collection."""
        try:
            # Use the specified collection to fetch data
            cursor = self.mongo_client.vault[collection].find()
            data = list(cursor)  # Convert the cursor to a list

        except Exception as e:
            print(e)
            return None  # Handle the exception gracefully, you may want to log it or take other actions

        return data

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


mongo_module = MongoModule()
