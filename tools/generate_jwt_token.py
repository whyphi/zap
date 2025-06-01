import argparse
import jwt
from datetime import datetime, timedelta, timezone
import boto3

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from chalicelib.models.roles import Roles

ssm_client = boto3.client("ssm")
AUTH_SECRET = ssm_client.get_parameter(Name="/Zap/AUTH_SECRET", WithDecryption=True)[
    "Parameter"
]["Value"]


def generate_token(expiry_hours: int, roles: list[str]) -> str:
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(hours=expiry_hours),
        "roles": roles,
        "iat": datetime.now(timezone.utc),
    }

    token = jwt.encode(payload, AUTH_SECRET, algorithm="HS256")
    return token


def main():
    role_choices = [role.value for role in Roles]

    parser = argparse.ArgumentParser(description="Generate a JWT for local testing")

    parser.add_argument(
        "--expiry", type=int, default=1, help="Expiration time in hours (default: 1)"
    )
    parser.add_argument(
        "--roles",
        nargs="+",
        choices=role_choices,
        default=["member"],
        help=(
            "List of user roles (space-separated). "
            f"Valid roles: {', '.join(role_choices)}. "
            "Example: --roles admin member"
        ),
    )

    args = parser.parse_args()
    token = generate_token(args.expiry, args.roles)
    print(f"\n✅ JWT:\n{token}\n")


if __name__ == "__main__":
    main()
