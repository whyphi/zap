from chalicelib.modules.mongo import mongo_module
from chalice import ConflictError, NotFoundError

import json
from bson import ObjectId


class MemberService:
    class BSONEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, ObjectId):
                return str(o)
            return super().default(o)

    def __init__(self):
        self.collection = "users"

    def create(self, data):
        """
        Creates a user in the database.

        Args:
            data (dict): A dictionary containing user information.

        Returns:
            bool: True if the user was created, False otherwise.
        """
        existing_user = mongo_module.find_one_document(
            self.collection, {"email": data["email"]}
        )

        if existing_user:
            raise ConflictError("User already exists")

        # Create the user in the database
        data["isNewUser"] = True
        mongo_module.insert_document(self.collection, data)

        return {
            "success": True,
            "message": "User created successfully",
        }
    
    def delete(self, data: list[str]) -> dict:
        """
        Deletes user documents based on the provided IDs.

        Args:
            data (List[str]): A list of document IDs to be deleted.

        Returns:
            dict: A dictionary indicating the success of the deletion process.
                Contains the following keys:

                - "success" (bool): True if all documents were deleted successfully, False otherwise.
                - "message" (str): A message indicating the result of the deletion process.

        Raises:
            NotFoundError: If no IDs are provided or if a document with one of the
                provided IDs is not found in the database.
        """
        if not data:
            raise NotFoundError("No IDs provided to delete")

        for id in data:
            if not mongo_module.delete_document_by_id(self.collection, id):
                raise NotFoundError(f"Document with ID {id} not found")

        return {
            "success": True,
            "message": "Documents deleted successfully",
        }
        

    def get_all(self):
        data = mongo_module.get_all_data_from_collection(self.collection)
        return json.dumps(data, cls=self.BSONEncoder)

    def onboard(self, document_id=str, data=dict) -> bool:
        return mongo_module.update_document_by_id(self.collection, document_id, data)

    def update_roles(self, document_id=str, roles=list) -> bool:
        return mongo_module.update_document(
            self.collection,
            document_id,
            [{"$set": {"roles": roles}}],
        )


member_service = MemberService()
