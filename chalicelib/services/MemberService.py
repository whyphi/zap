from chalicelib.repositories.repository_factory import RepositoryFactory
from chalice.app import (
    ConflictError,
    NotFoundError,
    UnauthorizedError,
    BadRequestError,
    CaseInsensitiveMapping,
)
from bson import ObjectId
from collections import defaultdict
import json
import jwt
import boto3
import uuid


class MemberService:

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
            existing_user = self.users_repo.get_all_by_field(
                field="email", value=data["email"]
            )

            if existing_user and len(existing_user) > 0:
                raise ConflictError("User already exists")

            # Create the user in the database
            roles = data.pop("roles", None)  # Remove roles if present
            data["id"] = str(uuid.uuid4())  # Generate a new UUID for the user ID
            data["is_eboard"] = data.get(
                "is_eboard", False
            )  # Default to False if not provided
            data["is_new_user"] = data.get(
                "is_new_user", True
            )  # Default to True if not provided
            self.users_repo.create(data)

            # Create user-role relationship in the user_roles database
            role_id = self.roles_repo.get_all_by_field(field="name", value="member")
            if not role_id:
                raise NotFoundError("Default role not found")
            self.user_roles_repo.create(
                {"user_id": data["id"], "role_id": role_id[0]["id"]}
            )

            for role in roles or []:
                role_id = self.roles_repo.get_all_by_field(field="name", value=role)
                if not role_id:
                    raise NotFoundError(f"Role {role} is not role")
                self.user_roles_repo.create(
                    {"user_id": data["id"], "role_id": role_id[0]["id"]}
                )

            return {
                "success": True,
                "message": "User created successfully",
            }
        except Exception as e:
            raise BadRequestError(f"Failed to create user: {e}")

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
        try:
            if not data:
                raise NotFoundError("No IDs provided to delete")

            for user_id in data:
                self.users_repo.delete(user_id)

            return {
                "success": True,
                "message": "Documents deleted successfully",
            }
        except Exception as e:
            raise BadRequestError(f"Failed to delete users: {str(e)}")

    def get_by_id(self, user_id: str):
        try:
            data = self.users_repo.get_by_id(user_id)
            return data
        except Exception as e:
            raise BadRequestError(f"Failed to retrieve user")

    def get_all(self):
        try:
            data = self.users_repo.get_all()
            return data
        except Exception as e:
            raise NotFoundError(f"Failed to retrieve users: {str(e)}")

    def onboard(self, id: str, data: dict) -> bool:
        try:
            print(f"Onboarding user: {id} with data: {data}")

            print(f"data.get('is_eboard'): {data.get('is_eboard')}")

            data["is_new_user"] = False
            if "graduation_year" in data:
                data["grad_year"] = int(data["graduation_year"])
                data.pop("graduation_year", None)
            if "is_eboard" in data:
                data["is_eboard"] = data["is_eboard"]
                data.pop("is_eboard", None)
            if "is_new_user" in data:
                data.pop("is_new_user", None)

            print(f"Processed data for onboarding: {data}")
            self.users_repo.update(id, data)
            return True
        except Exception as e:
            raise BadRequestError(f"Failed to onboard user: {str(e)}")

    # TODO: test updates with frontend
    def update(self, user_id: str, data: dict, headers: CaseInsensitiveMapping) -> bool:
        try:
            ssm_client = boto3.client("ssm")
            auth_header = headers.get("authorization", None)

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
                    f"User {user_id} is not authorized to update this user."
                )

            # NOTE: Performing an update on the path 'id' would modify the immutable field 'id'
            data.pop("id", None)

            self.users_repo.update(user_id, data)

            return True

        except Exception as e:
            raise BadRequestError(f"Failed to update user: {e}")

    def update_roles(self, user_id: str, roles: list) -> bool:
        try:
            existing_roles = self.users_repo.get_by_id(user_id)  # Check if user exists
            if existing_roles:
                self.user_roles_repo.delete_by_field("user_id", user_id)

            for role in roles:
                role_id = self.roles_repo.get_all_by_field("name", role)[0].get("id")
                if not role_id:
                    raise NotFoundError(f"Role with ID {role} not found")
                self.user_roles_repo.create({"user_id": user_id, "role_id": role_id})
            return True
        except Exception as e:
            raise BadRequestError(f"Failed to update roles: {e}")

    # Function temporarily unusable
    def get_family_tree(self):
        try:
            data = self.users_repo.get_all()

            # Group by family
            family_groups = defaultdict(list)

            # There's no 'big' field in supabase data, so every member will be skipped in current implementation
            # TODO: should come up with a new way to store big/little relationships

            # NOTE: idk how to do this but this below assumes big-id field exists in each user record
            for member in data:
                if not member.get("big_id"):  # skip members w/o a big
                    continue
                family = member.get("family", "Unknown")  # uses unknown if no fam field
                family_groups[family].append(member)  # gorups by family
            return family_groups

        except Exception as e:
            raise BadRequestError(f"Failed to generate family tree")


member_service = MemberService()
