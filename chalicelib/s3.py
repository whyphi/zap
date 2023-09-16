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
        
        # Split parts of base64 data
        parts = base64_data.split(',')
        metadata, base64_data = parts[0], parts[1]        

        # Extract content type from metadata
        content_type = metadata.split(';')[0][5:]  # Remove "data:" prefix
        binary_data = decode_base64(base64_data)
        
        # Upload binary data as object with content type set
        self.s3.put_object(
            Bucket=self.bucket_name, Key=path, Body=binary_data, ContentType=content_type
        )

        # Retrieve endpoint of object
        s3_endpoint = f"https://{self.bucket_name}.s3.amazonaws.com/"
        object_url = s3_endpoint + path
        
        return object_url

    