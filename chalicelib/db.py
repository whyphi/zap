import os
import boto3


class DBResource:
    def __init__(self):
        self.is_prod = os.environ.get("ENV") == "prod"
        self.db = boto3.resource("dynamodb")

    def put_data(self, table_name: str, data):
        if self.is_prod:
            table_name += "-prod"
        else:
            table_name += "-dev"

        table = self.db.Table(table_name)
        table.put_item(Item=data)

    
    def get_all(self, table_name: str):
        if self.is_prod:
            table_name += "-prod"
        else:
            table_name += "-dev"

        table = self.db.Table(table_name)
        
        # Use the scan operation to retrieve all items from the table
        response = table.scan()

        # The response contains the items as well as other information like metadata
        items = response.get("Items", [])

        return items