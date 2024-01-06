import os
import boto3
from botocore import errorfactory
from chalicelib.models.listing import Listing
from boto3.dynamodb.conditions import Key
from typing import Optional, Union


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
    def get_item(self, table_name: str, key: dict) -> dict:
        """Gets an item from table_name through key specifier"""
        table = self.resource.Table(table_name)
        response = table.get_item(Key=key)
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return response["Item"]

        return {}

    @add_env_suffix
    def delete_item(self, table_name: str, key: dict):
        """Deletes an item identified by the key."""
        # Get a reference to the DynamoDB table
        table = self.resource.Table(table_name)

        # Try to delete the item
        try:
            response = table.delete_item(Key=key)
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                return True
            else:
                return False
        except errorfactory.client.exceptions.ResourceNotFoundException:
            # If the item does not exist, return False
            return False

    @add_env_suffix
    def get_applicants(self, table_name: str, listing_id: str):
        secondary_key_name = "listingId"
        secondary_key_value = listing_id

        # Get a reference to the DynamoDB table
        table = self.resource.Table(table_name)

        # Use the query method to filter items by the secondary key
        # Ensure that global secondary key is set
        response = table.query(
            IndexName=f"{secondary_key_name}-index",
            KeyConditionExpression=Key(secondary_key_name).eq(secondary_key_value),
        )

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return response["Items"]

        return []

    @add_env_suffix
    def toggle_visibility(self, table_name: str, key: dict):
        """Toggles the visibility boolean for an item identified by the key."""
        # Get a reference to the DynamoDB table
        table = self.resource.Table(table_name)

        # Fetch the current item
        listing_item = table.get_item(Key=key)
        if "Item" not in listing_item:
            return None

        curr_listing = Listing.from_dynamodb_item(listing_item["Item"])

        # If the item exists, update the visibility field to the opposite value
        if curr_listing:
            current_visibility = curr_listing.isVisible
            updated_visibility = (
                not current_visibility if current_visibility is not None else True
            )

            # Update the item with the new visibility value
            table.update_item(
                Key=key,
                UpdateExpression="SET isVisible = :value",
                ExpressionAttributeValues={":value": updated_visibility},
            )

            return True

        # Return None if the item doesn't exist
        return None

    @add_env_suffix
    def update_listing_field(
        self,
        table_name: str,
        key: dict,
        field: str,
        new_value: Union[str, int, float, bool],
    ) -> Optional[dict]:
        """Updates a specific field of a listing identified by the key."""
        # Get a reference to the DynamoDB table
        table = self.resource.Table(table_name)

        # Fetch the current item
        listing_item = table.get_item(Key=key)
        if "Item" not in listing_item:
            return None

        # Update the specified field with the new value
        update_expression = f"SET {field} = :value"
        expression_attribute_values = {":value": new_value}

        table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
        )

        return listing_item["Item"]

db = DBResource()