import boto3
import os
from chalicelib.utils.utils import decode_base64


class S3Client:
    def __init__(self):
        self.bucket_name = "whyphi-zap"
        self.env = os.environ.get("ENV", "local")  # local, staging, prod
        self.is_local = self.env == "local"

        # Configure boto3 client based on environment
        if self.is_local:
            self.s3 = boto3.client(
                "s3",
                endpoint_url="http://localhost:4566",
                aws_access_key_id="test",
                aws_secret_access_key="test",
                region_name="us-east-1",
            )
            self.s3_endpoint = f"http://localhost:4566/{self.bucket_name}/"
        else:
            self.s3 = boto3.client("s3")
            self.s3_endpoint = f"https://{self.bucket_name}.s3.amazonaws.com/"

    def _get_path_prefix(self) -> str:
        """Get the appropriate path prefix based on environment"""
        if self.env == "prod":
            return "prod"
        elif self.env == "staging":
            return "dev" 
        else:
            return "local"

    def upload_binary_data(self, relative_path: str, data: str) -> str:
        """Uploads object to S3 Bucket and returns path"""
        full_path = f"{self._get_path_prefix()}/{relative_path}"

        # Split parts of base64 data
        parts = data.split(",")
        metadata, base64_data = parts[0], parts[1]

        # Extract content type from metadata
        content_type = metadata.split(";")[0][5:]  # Remove "data:" prefix
        binary_data = decode_base64(base64_data)

        # Upload binary data as object with content type set
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=full_path,
            Body=binary_data,
            ContentType=content_type,
        )

        # Retrieve endpoint of object
        object_url = self.s3_endpoint + full_path
        return object_url

    def delete_binary_data(self, relative_path: str) -> str:
        """Deletes object from s3 and returns response
        Args:
            relative_path (str): The key (path) of the object to delete from the S3 bucket. e.g. image/rush/<timeframe>/<event>/infosession2.png

        Returns:
            str: A message indicating the result of the deletion operation.

        Documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/delete_object.html
        """
        path = f"{self._get_path_prefix()}/{relative_path}"

        # delete binary data given bucket_name and key
        response = self.s3.delete_object(Bucket=self.bucket_name, Key=path)

        return response


s3 = S3Client()
