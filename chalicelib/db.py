import os
import boto3
from botocore import errorfactory


class DBResource:
    def __init__(self):
        self.is_prod = os.environ.get("ENV") == "prod"
        self.resource = boto3.resource("dynamodb")
        self.primary_keys = {"zap-listings": "listingId"}

    def add_env_suffix(func):
        def wrapper(self, table_name: str, *args, **kwargs):
            if self.is_prod:
                table_name += "-prod"
            else:
                table_name += "-dev"

            return func(self, table_name, *args, **kwargs)

        return wrapper

    @add_env_suffix
    def put_data(self, table_name: str, data):
        table = self.resource.Table(table_name)
        table.put_item(Item=data)

    @add_env_suffix
    def get_all(self, table_name: str):
        table = self.resource.Table(table_name)
        # Use the scan operation to retrieve all items from the table
        response = table.scan()
        # The response contains the items as well as other information like metadata
        items = response.get("Items", [])

        return items

    @add_env_suffix
    def get_item(self, table_name: str, key: dict):
        """Gets an item from table_name through key specifier"""
        table = self.resource.Table(table_name)
        print(table)
        item = table.get_item(Key=key)
        return item
