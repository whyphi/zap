import boto3
import jwt
import logging
from typing import Optional

from chalice.app import UnauthorizedError
from chalicelib.models.roles import Roles

logger = logging.getLogger(__name__)
PROD_SUFFIX = "-prod"
DEV_SUFFIX = "-dev"
AUTH_SECRET_PARAMETER = "/Zap/AUTH_SECRET"


def _resolve_table_name(table_name: str, env: bool) -> str:
    return f"{table_name}{PROD_SUFFIX if env else DEV_SUFFIX}"


def _extract_bearer_token(auth_header: Optional[str]) -> str:
    if not auth_header:
        raise UnauthorizedError("Authorization header is missing.")

    _, token = auth_header.split(" ", 1) if " " in auth_header else (None, None)
    if token is None:
        raise UnauthorizedError("Token is missing.")
    return token


def _get_auth_secret() -> str:
    ssm_client = boto3.client("ssm")
    return ssm_client.get_parameter(Name=AUTH_SECRET_PARAMETER, WithDecryption=True)[
        "Parameter"
    ]["Value"]


def _get_user_roles(decoded_jwt: dict) -> list[Roles]:
    try:
        return [Roles(role) for role in decoded_jwt.get("roles", [])]
    except ValueError:
        logger.error("Invalid role value in token payload.")
        raise UnauthorizedError("Invalid token.")


def _is_user_authorized(required_roles: list[Roles], user_roles: list[Roles]) -> bool:
    if len(required_roles) == 0:
        return True
    return any(role in user_roles for role in required_roles)


def add_env_suffix(func):
    """
    Decorator for adding an environment suffix to a table name based on the provided 'env' flag.

    Args:
        func (function): The original function to be decorated.

    Returns:
        function: A wrapper function that modifies the input 'table_name' based on the 'env' flag.

    - When calling my_function with env=True, the table_name will be suffixed with '-prod'.
    - When calling my_function with env=False or without the 'env' flag, the table_name will be suffixed with '-dev'.
    """

    def wrapper(self, table_name: str, *args, **kwargs):
        table_name = _resolve_table_name(
            table_name=table_name, env="env" in kwargs and kwargs["env"]
        )

        return func(self, table_name, *args, **kwargs)

    return wrapper


def auth(blueprint, roles):
    """
    Decorator for authenticating and authorizing access to API routes.

    Args:
        blueprint (object): The Chalice Blueprint object, providing access to the current request.
        roles (list[str]): The required role for authorization.

    Returns:
        function: A decorator function that authenticates and authorizes access based on the provided role.

    Raises:
        401 Unauthorized: If the Authorization header is missing, the token is invalid, or the token has expired.
        403 Forbidden: If the decoded role is not part of the given role.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            api_request = blueprint.current_request
            auth_header = api_request.headers.get("Authorization", None)
            token = _extract_bearer_token(auth_header=auth_header)

            try:
                auth_secret = _get_auth_secret()
                decoded = jwt.decode(token, auth_secret, algorithms=["HS256"])
                user_roles = _get_user_roles(decoded_jwt=decoded)
                if not _is_user_authorized(required_roles=roles, user_roles=user_roles):
                    logger.error(
                        f"User with roles {user_roles} tried to access a resource requiring roles {roles}"
                    )
                    raise UnauthorizedError(
                        "You do not have permission to access this resource."
                    )

                return func(*args, **kwargs)

            except jwt.ExpiredSignatureError:
                logger.error("Token has expired.")
                raise UnauthorizedError("Token has expired.")
            except jwt.InvalidTokenError:
                logger.error("Invalid token.")
                raise UnauthorizedError("Invalid token.")

        return wrapper

    return decorator
