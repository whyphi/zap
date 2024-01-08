import pytest
from chalicelib.db import DBResource
import boto3
from moto import mock_dynamodb


@pytest.fixture(scope="function")
def dynamodb_client():
    # Set up mock DynamoDB client using Moto
    with mock_dynamodb():
        dynamodb = boto3.client("dynamodb")
        yield dynamodb


@pytest.fixture(scope="function")
def mock_dynamodb_resource(dynamodb_client):
    # Create the minimum tables required to test DynamoDB calls
    dynamodb_client.create_table(
        TableName="test-table-dev",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        ProvisionedThroughput={
            "ReadCapacityUnits": 1,
            "WriteCapacityUnits": 1,
        },
    )
    dynamodb_client.create_table(
        TableName="test-table-prod",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        ProvisionedThroughput={
            "ReadCapacityUnits": 1,
            "WriteCapacityUnits": 1,
        },
    )
    yield boto3.resource("dynamodb")


@pytest.fixture(scope="function")
def db(mock_dynamodb_resource):
    # Yield DBResource with DynamoDB resource
    yield DBResource()


SAMPLE_DATA = [
    {"id": "123", "title": "Sample Listing"},
    {"id": "124", "title": "Sample Listing"},
]


def test_put_data(db):
    # Sample data to be inserted
    sample_data = {"id": "123", "title": "Sample Listing"}

    # Executing the put_data method
    db.put_data("test-table", sample_data)

    # Check if the item exists in the table
    retrieved_item = db.get_item("test-table", {"id": "123"})
    assert retrieved_item == sample_data


def test_put_data_on_prod_table(db):
    # Sample data to be inserted
    sample_data = {"id": "123", "title": "Sample Listing"}

    # Set env to prod
    db.is_prod = True

    # Executing the put_data method
    db.put_data("test-table", sample_data)

    # Check if the item exists in the table
    retrieved_item = db.get_item("test-table", {"id": "123"})
    assert retrieved_item == sample_data


def test_get_all(db):
    # Executing the put_data method
    db.put_data("test-table", SAMPLE_DATA[0])
    db.put_data("test-table", SAMPLE_DATA[1])

    # Check if the item exists in the table
    retrieved_item = db.get_all("test-table")
    assert retrieved_item == SAMPLE_DATA


def test_get_item(db):
    # Executing the put_data method
    db.put_data("test-table", SAMPLE_DATA[0])

    # Check if the item exists in the table
    retrieved_item = db.get_item("test-table", {"id": "123"})
    assert retrieved_item == SAMPLE_DATA[0]

    # retrieved_item = db.get_item("test-table", {"id": "122"})
    # assert retrieved_item == {}


def test_delete_item(db):
    db.put_data("test-table", SAMPLE_DATA[0])

    response = db.delete_item("test-table", {"id": 123})
    assert response == True

    # TODO: Test case should fail, but isn't
    # response = db.delete_item("test-table", {"id": 124})
    # assert response == False


