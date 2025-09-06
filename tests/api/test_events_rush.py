import os

os.environ["CHALICE_TESTING"] = "1"

import json
import pytest
from unittest.mock import Mock, patch
from chalice.test import Client
from app import app
from chalicelib.api import events_rush

with open("tests/fixtures/events/general/sample_rush_events.json") as f:
    SAMPLE_RUSH_EVENTS = json.load(f)

with open("tests/fixtures/events/general/sample_rush_event.json") as f:
    SAMPLE_RUSH_EVENT = json.load(f)


@pytest.fixture(scope="module")
def test_client():
    # Create mock for EventsRushService
    mock_events_rush_service = Mock()

    # Register routes with the mock
    events_rush.register_routes(events_rush_service=mock_events_rush_service)

    # Attach blueprint
    app.register_blueprint(events_rush.events_rush_api)

    with Client(app) as client:
        yield client, mock_events_rush_service


def test_get_rush_events(test_client):
    client, mock_service = test_client
    mock_service.get_rush_categories_and_events.return_value = SAMPLE_RUSH_EVENTS

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}

        response = client.http.get(
            "/events/rush",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

    assert response.status_code == 200
    assert response.json_body == SAMPLE_RUSH_EVENTS
    mock_service.get_rush_categories_and_events.assert_called_once()


def test_get_rush_event(test_client):
    client, mock_service = test_client
    mock_service.get_rush_event.return_value = SAMPLE_RUSH_EVENT

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}

        response = client.http.get(
            "/events/rush/test_event_id?hideCode=false&hideAttendees=false",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

    assert response.status_code == 200
    assert response.json_body == SAMPLE_RUSH_EVENT
    mock_service.get_rush_event.assert_called_once_with(
        event_id="test_event_id", hide_attendees=False, hide_code=False
    )


def test_create_rush_event(test_client):
    client, mock_service = test_client
    mock_service.create_rush_event.return_value = {"msg": True}

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}

        response = client.http.post(
            "/events/rush",
            headers={
                "Authorization": "Bearer SAMPLE_TOKEN_STRING",
                "Content-Type": "application/json",
            },
            body=json.dumps({"name": "New Rush Event"}),
        )

    assert response.status_code == 200
    assert response.json_body == {"msg": True}
    mock_service.create_rush_event.assert_called_once_with({"name": "New Rush Event"})


def test_modify_rush_event(test_client):
    client, mock_service = test_client
    mock_service.modify_rush_event.return_value = {"msg": True}

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}

        response = client.http.patch(
            "/events/rush",
            headers={
                "Authorization": "Bearer SAMPLE_TOKEN_STRING",
                "Content-Type": "application/json",
            },
            body=json.dumps({"id": "123", "name": "Updated Name"}),
        )

    assert response.status_code == 200
    assert response.json_body == {"msg": True}
    mock_service.modify_rush_event.assert_called_once_with(
        {"id": "123", "name": "Updated Name"}
    )


def test_delete_rush_event(test_client):
    client, mock_service = test_client
    mock_service.delete_rush_event.return_value = {"status": True}

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}

        response = client.http.delete(
            "/events/rush/test_event_id",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

    assert response.status_code == 200
    assert response.json_body == {"status": True}
    mock_service.delete_rush_event.assert_called_once_with("test_event_id")
