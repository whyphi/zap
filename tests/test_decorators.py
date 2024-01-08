from unittest.mock import patch
from chalicelib.decorators import add_env_suffix

def test_add_env_suffix_dev():
    def mocked_function(self, table_name: str, *args, **kwargs):
        return table_name

    # Create an instance of the decorator
    decorated_function = add_env_suffix(mocked_function)

    # Mock the 'self' argument for the instance method
    instance_mock = object()

    # Call the decorated function with 'env=False'
    result = decorated_function(instance_mock, "test-table", env=False)

    # Check if the suffix is added correctly
    assert result == "test-table-dev"

def test_add_env_suffix_prod():
    def mocked_function(self, table_name: str, *args, **kwargs):
        return table_name

    # Create an instance of the decorator
    decorated_function = add_env_suffix(mocked_function)

    # Mock the 'self' argument for the instance method
    instance_mock = object()

    # Call the decorated function with 'env=True'
    result = decorated_function(instance_mock, "test-table", env=True)

    # Check if the suffix is added correctly
    assert result == "test-table-prod"