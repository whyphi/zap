import os
import boto3
from botocore import errorfactory


class DBResource:
    def __init__(self):
        self.is_prod = os.environ.get("ENV") == "prod"
        self.resource = boto3.resource("dynamodb")
        self.primary_keys = {"zap-listings": "listingId"}

    # def create_table(self, table_name: str, primary_key: str):
    #     """Creates a table with a given primary_key"""
    #     table = self.resource.create_table(
    #         TableName=table_name,
    #         KeySchema=[
    #             {
    #                 "AttributeName": primary_key,
    #                 "KeyType": "HASH",  # Assuming you have a hash key
    #             }
    #         ],
    #         AttributeDefinitions=[
    #             {
    #                 "AttributeName": primary_key,
    #                 "AttributeType": "S",  # Assuming it's a string
    #             }
    #         ],
    #         ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    #     )
    #     # Wait until the table exists
    #     table.meta.client.get_waiter("table_exists").wait(TableName=table_name)
    #     print(table)
    #     return table

    def put_data(self, table_name: str, data):
        if self.is_prod:
            table_name += "-prod"
        else:
            table_name += "-dev"

        table = self.resource.Table(table_name)

        table.put_item(Item=data)

    def get_all(self, table_name: str):
        if self.is_prod:
            table_name += "-prod"
        else:
            table_name += "-dev"

        table = self.resource.Table(table_name)

        # Use the scan operation to retrieve all items from the table
        response = table.scan()

        # The response contains the items as well as other information like metadata
        items = response.get("Items", [])

        return items
