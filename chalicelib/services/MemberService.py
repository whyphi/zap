from chalicelib.modules.mongo import mongo_module
from chalice.app import ConflictError, NotFoundError, UnauthorizedError

from bson import ObjectId
from collections import defaultdict
import json
import jwt
import boto3


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

    def get_by_id(self, user_id: str):
        data = mongo_module.get_document_by_id(self.collection, user_id)
        return json.dumps(data, cls=self.BSONEncoder)

    def get_all(self):
        data = mongo_module.get_data_from_collection(self.collection)
        return json.dumps(data, cls=self.BSONEncoder)

    def onboard(self, document_id=str, data=dict) -> bool:
        return mongo_module.update_document_by_id(self.collection, document_id, data)

    def update(self, user_id: str, data: dict, headers: dict) -> bool:
        ssm_client = boto3.client("ssm")
        auth_header = headers.get("Authorization", None)

        if not auth_header:
            raise UnauthorizedError("Authorization header is missing.")

        _, token = auth_header.split(" ", 1) if " " in auth_header else (None, None)

        if not token:
            raise UnauthorizedError("Token is missing.")

        auth_secret = ssm_client.get_parameter(
            Name="/Zap/AUTH_SECRET", WithDecryption=True
        )["Parameter"]["Value"]
        decoded = jwt.decode(token, auth_secret, algorithms=["HS256"])

        if user_id != decoded["_id"]:
            raise UnauthorizedError(
                "User {user_id} is not authorized to update this user."
            )

        # NOTE: Performing an update on the path '_id' would modify the immutable field '_id'
        data.pop("_id", None)

        return mongo_module.update_document_by_id(self.collection, user_id, data)

    def update_roles(self, document_id=str, roles=list) -> bool:
        return mongo_module.update_document(
            self.collection,
            document_id,
            [{"$set": {"roles": roles}}],
        )

    def get_family_tree(self):
        data = mongo_module.get_data_from_collection(self.collection)

        # Group by family
        family_groups = defaultdict(list)

        for member in data:
            if "big" not in member or member["big"] == "":
                continue
            member["_id"] = str(member["_id"])
            family_groups[member["family"]].append(member)

        return family_groups


member_service = MemberService()
