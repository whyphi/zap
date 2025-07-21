from chalicelib.repositories.repository_factory import RepositoryFactory
from chalice.app import ConflictError, NotFoundError, UnauthorizedError, BadRequestError

from bson import ObjectId
from collections import defaultdict
import json
import jwt
import boto3

# IN PROGRESS

class MemberService:
    class BSONEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, ObjectId):
                return str(o)
            return super().default(o)

    def __init__(self):
        self.users_repo = RepositoryFactory.users()
        self.user_roles_repo = RepositoryFactory.user_roles()
        self.roles_repo = RepositoryFactory.roles()

    def create(self, data):
        """
        Creates a user in the database.

        Args:
            data (dict): A dictionary containing user information.

        Returns:
            bool: True if the user was created, False otherwise.
        """
        try:
            existing_user = self.users_repo.get_all_by_field(field="email", value=data["email"])
        except Exception as e:
            raise BadRequestError(f"Failed to check existing user: {str(e)}")

        if existing_user and len(existing_user) > 0:
            raise ConflictError("User already exists")
        
        # Create the user in the database
        try:
            self.users_repo.create(data)
        except Exception as e:
            raise BadRequestError(f"Failed to create user: {str(e)}")

        # Create user-role relationship in the user_roles table
        try:
            role_id = self.roles_repo.get_all_by_field(field="name", value="member")
        except Exception as e:
            raise BadRequestError(f"Failed to retrieve role: {str(e)}")    
            
        try:
            self.user_roles_repo.create({"user_id": data["id"], "role_id": role_id[0]["_id"]})
        except Exception as e:
            raise BadRequestError(f"Failed to create user role: {str(e)}")

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
            if not self.user_roles_repo.delete(field="user_id", value=id):
                raise NotFoundError(f"Document with ID {id} not found")
            if not self.users_repo.delete(field="user_id", value=id):
                raise NotFoundError(f"Document with ID {id} not found")

        return {
            "success": True,
            "message": "Documents deleted successfully",
        }

    def get_by_id(self, user_id: str):
        try:
            data = self.users_repo.get_by_id(user_id)
        except Exception as e:
            raise NotFoundError(f"Failed to retrieve user: {str(e)}")
        return json.dumps(data, cls=self.BSONEncoder)

    def get_all(self):
        try:
            data = self.users_repo.get_all()
        except Exception as e:
            raise NotFoundError(f"Failed to retrieve users: {str(e)}")
        return json.dumps(data, cls=self.BSONEncoder)

    def onboard(self, document_id=str, data=dict) -> bool:
        try:
            response = self.users_repo.update(document_id, data)
        except Exception as e:
            raise BadRequestError(f"Failed to onboard user: {str(e)}")
        return response
    
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
        
        try:
            response = self.users_repo.update(user_id, data)
        except Exception as e:
            raise BadRequestError(f"Failed to update user: {str(e)}")
        
        return response

    def update_roles(self, user_id=str, roles=list) -> bool:    
        # Delete existing roles for the user    
        try:
            self.user_roles_repo.delete(id_value="user_id")
        except BadRequestError as e:
            raise BadRequestError(f"Failed to delete existing roles: {str(e)}")        

        for role in roles:
            try:
                role_id = self.roles_repo.get_all_by_field(role)["role_id"]
            except Exception as e:
                raise BadRequestError(f"Failed to retrieve role: {str(e)}")
            
            if not role_id:
                raise NotFoundError(f"Role with ID {role} not found")

        try:
            response = self.user_roles_repo.create({"user_id": user_id, "role_ids": roles})
        except Exception as e:
            raise BadRequestError(f"Failed to update user roles: {str(e)}")

        return response

    # Function temporarily unusable
    def get_family_tree(self):
        data = self.users_repo.get_all()

        # Group by family
        family_groups = defaultdict(list)

        # There's no 'big' field in supabase data, so every member will be skipped in current implementation
        # TODO: should come up with a new way to store big/little relationships
        for member in data:
            if "big" not in member or member["big"] == "":
                continue
            member["_id"] = str(member["_id"])
            family_groups[member["family"]].append(member)

        return family_groups

member_service = MemberService()
