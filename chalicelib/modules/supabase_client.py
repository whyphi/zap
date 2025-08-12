import os
from supabase import create_client, Client
from chalicelib.modules.aws_ssm import aws_ssm
from dotenv import load_dotenv
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SupabaseClient:
    _client: Optional[Client] = None

    @staticmethod
    def get_params() -> Tuple[str, str]:
        """
        Retrieves Supabase URL and key based on the current environment.

        Returns:
            Tuple[str, str]: Supabase URL and key.
        Raises:
            Exception: If parameters cannot be found or fetched.
        """
        ENV = os.getenv("ENV", "local")
        logger.info(f"[SupabaseClient.get_params] Running in env: {ENV}")

        if ENV in ["staging", "prod"]:
            try:
                url = aws_ssm.get_parameter_value(f"/Zap/{ENV}/SUPABASE_URL")
                key = aws_ssm.get_parameter_value(f"/Zap/{ENV}/SUPABASE_KEY")
            except Exception as e:
                raise Exception(
                    f"[SupabaseClient] Failed to fetch Supabase params from SSM: {str(e)}"
                )
        elif ENV == "pytest-init":
            # TODO: remove entirely (shouldn't be needed for dep-injection pytest)
            # Edge case: pytest lazy-initializes url and key
            url = "dummy-url"
            key = "dummy-key"
        else:
            load_dotenv(".env.local")
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")

        if not (url and key):
            raise Exception(
                f"[SupabaseClient.get_params] Could not find Supabase url or key. ENV: {ENV}"
            )

        return url, key

    @classmethod
    def get_client(cls) -> Client:
        """
        Returns a cached Supabase client instance, creating it if necessary.

        Returns:
            Client: Supabase client instance.
        """
        if cls._client is None:
            url, key = cls.get_params()
            cls._client = create_client(url, key)
        return cls._client

    @classmethod
    def set_client(cls, client: Client):
        """
        Injects a mock or pre-initialized Supabase client instance (for testing).

        Args:
            client (Client): Supabase client instance to set.
        """
        cls._client = client

    @classmethod
    def reset_client(cls):
        """
        Clears the cached Supabase client instance (for teardown or reinitialization).
        """
        cls._client = None
