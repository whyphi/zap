import boto3
import jwt


def add_env_suffix(func):
    def wrapper(self, table_name: str, *args, **kwargs):
        if "env" in kwargs and kwargs["env"]:
            table_name += "-prod"
        else:
            table_name += "-dev"

        return func(self, table_name, *args, **kwargs)

    return wrapper


def auth(blueprint, role):
    def decorator(func):
        def wrapper(*args, **kwargs):
            api_request = blueprint.current_request
            auth_header = api_request.headers.get("Authorization", None)
            _, token = auth_header.split(" ", 1) if " " in auth_header else (None, None)

            if not token:
                return {"error": "Authorization header is missing"}, 401

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
                return {"error": "Unauthorized: Token has expired"}, 401
            except jwt.InvalidTokenError:
                print("test")
                return {"error": "Unauthorized: Invalid token"}, 401

        return wrapper

    return decorator
