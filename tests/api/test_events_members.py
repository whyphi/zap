import os

os.environ["CHALICE_TESTING"] = "1"

import json
import pytest
from unittest.mock import Mock, patch
from chalice.test import Client
from app import app
from chalicelib.api import events_member

with open("tests/fixtures/events/general/sample_timeframes.json") as f:
    SAMPLE_TIMEFRAMES = json.load(f)

with open("tests/fixtures/events/general/sample_timeframe_sheets.json") as f:
    SAMPLE_TIMEFRAME_SHEETS = json.load(f)


@pytest.fixture(scope="module")
def test_client():
    # Create mock for EventsMemberService
    mock_events_member_service = Mock()

    # Register routes with the mock
    events_member.register_routes(events_member_service=mock_events_member_service)

    # Attach blueprint
    app.register_blueprint(events_member.events_member_api)

    with Client(app) as client:
        yield client, mock_events_member_service


def test_create_timeframe(test_client):
    client, mock_service = test_client
    mock_service.create_timeframe.return_value = {"msg": True}

    with patch("chalicelib.decorators.jwt.decode", return_value={"roles": ["admin"]}):
        response = client.http.post(
            "/timeframes",
            headers={
                "Authorization": "Bearer SAMPLE_TOKEN_STRING",
                "Content-Type": "application/json",
            },
            body=json.dumps({"name": "Fall 2025"}),
        )

    assert response.status_code == 200
    assert response.json_body == {"msg": True}
    mock_service.create_timeframe.assert_called_once_with({"name": "Fall 2025"})


def test_get_all_timeframes(test_client):
    client, mock_service = test_client
    mock_service.get_all_timeframes_and_events.return_value = SAMPLE_TIMEFRAMES

    with patch("chalicelib.decorators.jwt.decode", return_value={"roles": ["admin"]}):
        response = client.http.get(
            "/timeframes",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

    assert response.status_code == 200
    assert response.json_body == SAMPLE_TIMEFRAMES
    mock_service.get_all_timeframes_and_events.assert_called_once()


def test_get_timeframe(test_client):
    client, mock_service = test_client
    mock_service.get_timeframe.return_value = SAMPLE_TIMEFRAMES[0]

    with patch("chalicelib.decorators.jwt.decode", return_value={"roles": ["admin"]}):
        response = client.http.get(
            f"/timeframes/{SAMPLE_TIMEFRAMES[0]['id']}",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

    assert response.status_code == 200
    assert response.json_body == SAMPLE_TIMEFRAMES[0]
    mock_service.get_timeframe.assert_called_once_with(SAMPLE_TIMEFRAMES[0]["id"])


def test_delete_timeframe(test_client):
    client, mock_service = test_client
    mock_service.delete_timeframe.return_value = {"status": True}

    with patch("chalicelib.decorators.jwt.decode", return_value={"roles": ["admin"]}):
        response = client.http.delete(
            f"/timeframes/{SAMPLE_TIMEFRAMES[0]['id']}",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

    assert response.status_code == 200
    assert response.json_body == {"status": True}
    mock_service.delete_timeframe.assert_called_once_with(SAMPLE_TIMEFRAMES[0]["id"])


def test_create_event(test_client):
    client, mock_service = test_client
    mock_service.create_event.return_value = {"msg": True}

    with patch("chalicelib.decorators.jwt.decode", return_value={"roles": ["admin"]}):
        response = client.http.post(
            f"/timeframes/{SAMPLE_TIMEFRAMES[0]['id']}/events",
            headers={
                "Authorization": "Bearer SAMPLE_TOKEN_STRING",
                "Content-Type": "application/json",
            },
            body=json.dumps({"name": "New Event"}),
        )

    assert response.status_code == 200
    assert response.json_body == {"msg": True}
    mock_service.create_event.assert_called_once_with(
        SAMPLE_TIMEFRAMES[0]["id"], {"name": "New Event"}
    )


def test_get_event(test_client):
    client, mock_service = test_client
    mock_service.get_event.return_value = SAMPLE_TIMEFRAMES[0]["events_member"][0]

    with patch("chalicelib.decorators.jwt.decode", return_value={"roles": ["admin"]}):
        response = client.http.get(
            f"/events/{SAMPLE_TIMEFRAMES[0]['events_member'][0]['id']}",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

    assert response.status_code == 200
    assert response.json_body == SAMPLE_TIMEFRAMES[0]["events_member"][0]
    mock_service.get_event.assert_called_once_with(
        SAMPLE_TIMEFRAMES[0]["events_member"][0]["id"]
    )


def test_get_timeframe_sheets(test_client):
    client, mock_service = test_client
    mock_service.get_timeframe_sheets.return_value = SAMPLE_TIMEFRAME_SHEETS

    with patch("chalicelib.decorators.jwt.decode", return_value={"roles": ["admin"]}):
        response = client.http.get(
            f"/timeframes/{SAMPLE_TIMEFRAMES[0]['id']}/sheets",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

    assert response.status_code == 200
    assert response.json_body == SAMPLE_TIMEFRAME_SHEETS
    mock_service.get_timeframe_sheets.assert_called_once_with(
        SAMPLE_TIMEFRAMES[0]["id"]
    )


def test_checkin(test_client):
    client, mock_service = test_client
    mock_service.checkin.return_value = {"msg": True}

    with patch("chalicelib.decorators.jwt.decode", return_value={"roles": ["admin"]}):
        response = client.http.post(
            f"/events/{SAMPLE_TIMEFRAMES[0]['events_member'][0]['id']}/checkin",
            headers={
                "Authorization": "Bearer SAMPLE_TOKEN_STRING",
                "Content-Type": "application/json",
            },
            body=json.dumps({"user": "123"}),
        )

    assert response.status_code == 200
    assert response.json_body == {"msg": True}
    mock_service.checkin.assert_called_once_with(
        SAMPLE_TIMEFRAMES[0]["events_member"][0]["id"], {"user": "123"}
    )


def test_delete_event(test_client):
    client, mock_service = test_client
    mock_service.delete.return_value = {"status": True}

    with patch("chalicelib.decorators.jwt.decode", return_value={"roles": ["admin"]}):
        response = client.http.delete(
            f"/events/{SAMPLE_TIMEFRAMES[0]['events_member'][0]['id']}",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

    assert response.status_code == 200
    assert response.json_body == {"status": True}
    mock_service.delete.assert_called_once_with(
        SAMPLE_TIMEFRAMES[0]["events_member"][0]["id"]
    )
