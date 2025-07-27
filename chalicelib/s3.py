import boto3
import os
from chalicelib.utils import decode_base64


class S3Client:
    def __init__(self):
        self.bucket_name = "whyphi-zap"
        self.is_prod = os.environ.get("ENV") == "prod"
        self.s3 = boto3.client("s3")

    def upload_binary_data(self, path: str, data: str) -> str:
        """Uploads object to S3 Bucket and returns path"""
        # Set path
        if self.is_prod:
            path = f"prod/{path}"
        else:
            path = f"dev/{path}"

        # Split parts of base64 data
        parts = data.split(",")
        metadata, base64_data = parts[0], parts[1]

        # Extract content type from metadata
        content_type = metadata.split(";")[0][5:]  # Remove "data:" prefix
        binary_data = decode_base64(base64_data)

        # Upload binary data as object with content type set
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=path,
            Body=binary_data,
            ContentType=content_type,
        )

        # Retrieve endpoint of object
        s3_endpoint = f"https://{self.bucket_name}.s3.amazonaws.com/"
        object_url = s3_endpoint + path

        return object_url

    def delete_binary_data(self, object_id: str, is_full_path: bool = False) -> str:
        """Deletes object from s3 and returns response
        Args:
            object_id (str): The key (path) of the object to delete from the S3 bucket. e.g. dev/image/rush/66988908fd70b2c44bf2305d/199bb28f-b54c-48a3-9b94-1c95eab61f7d/infosession2.png
            is_full_path (bool): Flag set to true if object_id includes dev/prod in the url

        Returns:
            str: A message indicating the result of the deletion operation.

        Documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/delete_object.html
        """
        if is_full_path:
            path = object_id
        elif self.is_prod:
            path = f"prod/{object_id}"
        else:
            path = f"dev/{object_id}"

        # delete binary data given bucket_name and key
        response = self.s3.delete_object(Bucket=self.bucket_name, Key=path)

        return response


s3 = S3Client()
