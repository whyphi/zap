import pytest
from chalice.test import Client
from unittest.mock import MagicMock, patch
from chalice import NotFoundError, BadRequestError
from app import app
from chalicelib.api.events import events_api
from chalicelib.services.EventService import event_service

@pytest.fixture
def api_client(mock_functions, role):
    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        # Set the role based on the input parameter
        mock_decode.return_value = {"role": role}
        
        # Mock the specified functions
        mocked_functions = {}
        for function_name in mock_functions:
            mocked_functions[function_name] = patch(f"chalicelib.services.EventService.event_service.{function_name}")
            mocked_functions[function_name].start()
            mocked_functions[function_name].return_value = None
        
        yield mocked_functions
        
        # Stop all mocked functions
        for function in mocked_functions.values():
            function.stop()

@pytest.fixture
def mock_functions():
    return ["create_timeframe"]

def test_create_timeframe(api_client):
    # Assuming you have an instance of the API client
    client = api_client["create_timeframe"]
    
    # Make the API call
    response = client.http.post(
        f"/timeframes",
        headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
    )
    
    # Check the response status code and body
    assert response.status_code == 200
    assert response.json() == {"id": "timeframe_id", "name": "Test Timeframe"}