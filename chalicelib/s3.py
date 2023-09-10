import boto3
import os
import json
from datetime import datetime

class S3Client():
    def __init__(self, chalice_app):
        self.chalice_app = chalice_app
        self.bucket_name = "whyphi-zap"
        self.is_prod = os.environ.get("ENV") == "prod"
        self.s3 = boto3.client('s3')

    def upload_file_to_json(self, path: str, content: dict):
        """Converts python dictionary into JSON and uploads JSON file to S3 Bucket
        """
        # Set path
        if self.is_prod:
            path = f"prod/{path}"
        else:
            path = f"dev/{path}"

        try:
            pass