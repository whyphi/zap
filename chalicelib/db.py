import os
import boto3

class DBResource:
    def __init__(self):
        self.is_prod = os.environ.get("ENV") == "prod"
        self.db = boto3.resource('dynamodb')
    
    def put_data(self, table_name: str, data):
        if self.is_prod: table_name += "-prod"
        else: table_name += "-dev"
        table = self.db.Table(table_name)
        table.put_item(
            Item=data
        )