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
        ENV = os.getenv("ENV", "local")
        # TODO: remove eventually (for debugging)
        logger.info(f"[SupabaseClient] Running in env: {ENV}")

        if ENV in ["staging", "prod"]:
            try:
                url = aws_ssm.get_parameter_value(f"/Zap/{ENV}/SUPABASE_URL")
                key = aws_ssm.get_parameter_value(f"/Zap/{ENV}/SUPABASE_KEY")
            except Exception as e:
                raise Exception(
                    f"[SupabaseClient] Failed to fetch Supabase params from SSM: {str(e)}"
                )
        elif ENV == "pytest-init":
            # Edge case: pytest lazy-initializes url and key
            url = "dummy-url"
            key = "dummy-key"
        else:
            load_dotenv(".env.local")
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")

        if not (url and key):
            raise Exception(
                f"[SupabaseClient.__init__] Could not find Supabase url or key. ENV: {ENV}"
            )

        return url, key

    @classmethod
    def get_client(cls) -> Client:

        if cls._client is None:
            url, key = cls.get_params()
            cls._client = create_client(url, key)

        return cls._client
