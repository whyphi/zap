import os
from supabase import create_client, Client
from chalicelib.modules.aws_ssm import aws_ssm
from dotenv import load_dotenv


ENV = os.getenv("ENV", "local")
# TODO: remove eventually (for debugging)
print(f"[supabase_client] Running in env: {ENV}")


class SupabaseClient:
    def __init__(self):
        if ENV in ["staging", "prod"]:
            self.url = aws_ssm.get_parameter_value(f"/Zap/{ENV}/SUPABASE_URL")
            self.key = aws_ssm.get_parameter_value(f"/Zap/{ENV}/SUPABASE_KEY")
        else:
            load_dotenv(".env.local")
            self.url = os.getenv("SUPABASE_URL")
            self.key = os.getenv("SUPABASE_KEY")

        if not (self.url and self.key):
            raise Exception(
                f"[SupabaseClient.__init__] Could not find Supabase url or key. ENV: {ENV}"
            )

        self.client: Client = create_client(self.url, self.key)

    def get_client(self):
        return self.client
