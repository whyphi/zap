import boto3
import os
import json
from datetime import datetime
from chalicelib.utils import decode_base64


class S3Client:
    def __init__(self):
        self.bucket_name = "whyphi-zap"
        self.is_prod = os.environ.get("ENV") == "prod"
        self.s3 = boto3.client("s3")

    def upload_binary_data(self, path: str, data) -> str:
        """Uploads resume to S3 Bucket and returns path"""
        # Set path
        if self.is_prod:
            path = f"prod/{path}"
        else:
            path = f"dev/{path}"

        metadata = {
            "Content-Type": "application/pdf",
        }
        
        base64_data = data.split(',')[1]        
        binary_data = decode_base64(base64_data)
        
        self.s3.put_object(
            Bucket=self.bucket_name, Key=path, Body=binary_data, Metadata=metadata
        )

        s3_endpoint = f"https://{self.bucket_name}.s3.amazonaws.com/"
        resume_url = s3_endpoint + path
        
        return resume_url
