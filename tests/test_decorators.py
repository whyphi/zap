from chalicelib.decorators import add_env_suffix
from chalicelib.handlers.error_handler import handle_exceptions

import pytest
from chalice import Response, BadRequestError, NotFoundError, ChaliceViewError


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


def test_handle_exceptions_no_error():
    @handle_exceptions
    def sample_function():
        return "Success"

    assert sample_function() == "Success"


def test_handle_exceptions_bad_request_error():
    @handle_exceptions
    def sample_function():
        raise BadRequestError("Bad request")

    with pytest.raises(BadRequestError):
        sample_function()


def test_handle_exceptions_not_found_error():
    @handle_exceptions
    def sample_function():
        raise NotFoundError("Not found")

    with pytest.raises(NotFoundError):
        sample_function()


def test_handle_exceptions_chalice_view_error():
    @handle_exceptions
    def sample_function():
        raise ChaliceViewError("Chalice view error")

    with pytest.raises(ChaliceViewError):
        sample_function()


def test_handle_exceptions_general_exception():
    @handle_exceptions
    def sample_function():
        raise Exception("General error")

    response = sample_function()
    assert isinstance(response, Response)
    assert response.status_code == 500
    assert response.body == {
        "error": "Internal Server Error",
        "message": "General error",
    }
