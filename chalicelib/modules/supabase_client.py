import os
from supabase import create_client, Client
from dotenv import load_dotenv

# TODO: switch to using AWS SSM Parameter Store
load_dotenv()


class SupabaseClient:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.client: Client = create_client(self.url, self.key)

    def get_client(self):
        return self.client
