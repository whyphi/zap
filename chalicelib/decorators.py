import boto3
import jwt
from chalice import UnauthorizedError


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
        if "env" in kwargs and kwargs["env"]:
            table_name += "-prod"
        else:
            table_name += "-dev"

        return func(self, table_name, *args, **kwargs)

    return wrapper


def auth(blueprint, role):
    """
    Decorator for authenticating and authorizing access to API routes.

    Args:
        blueprint (object): The Chalice Blueprint object, providing access to the current request.
        role (list[str]): The required role for authorization.

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
            if not auth_header:
                raise UnauthorizedError("Authorization header is missing.")

            _, token = auth_header.split(" ", 1) if " " in auth_header else (None, None)
            if not token:
                raise UnauthorizedError("Token is missing.")

            try:
                ssm_client = boto3.client("ssm")
                auth_secret = ssm_client.get_parameter(
                    Name="/Zap/AUTH_SECRET", WithDecryption=True
                )["Parameter"]["Value"]
                decoded = jwt.decode(token, auth_secret, algorithms=["HS256"])
                print(role)
                # TODO: if decoded role is not part of given, reject auth

                return func(*args, **kwargs)

            except jwt.ExpiredSignatureError:
                raise UnauthorizedError("Token has expired.")
            except jwt.InvalidTokenError:
                raise UnauthorizedError("Invalid token.")

        return wrapper

    return decorator
