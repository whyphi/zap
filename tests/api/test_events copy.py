from chalice.test import Client
from unittest.mock import patch
import json

from app import app

with open("tests/fixtures/events/general/sample_rush_events.json") as f:
    SAMPLE_RUSH_EVENTS = json.load(f)

with open("tests/fixtures/events/general/sample_rush_event.json") as f:
    SAMPLE_RUSH_EVENT = json.load(f)

def test_get_rush_events():
    # Create a Chalice test client
    with Client(app) as client:
        # Mock applicant_service's get method
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"role": "admin"}
            with patch(
                "chalicelib.services.EventsRushService.events_rush_service.get_rush_categories_and_events",
            ) as mock_get_rush_categories_and_events:
                mock_get_rush_categories_and_events.return_value = SAMPLE_RUSH_EVENTS
                response = client.http.get(
                    f"/events/rush",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                # Check the response status code and body
                assert response.status_code == 200
                assert response.json_body == SAMPLE_RUSH_EVENTS

def test_get_rush_event():
    # Create a Chalice test client
    with Client(app) as client:
        # Mock applicant_service's get method
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"role": "admin"}
            with patch(
                "chalicelib.services.EventsRushService.events_rush_service.get_rush_event",
            ) as mock_get_rush_event:
                mock_get_rush_event.return_value = SAMPLE_RUSH_EVENT
                response = client.http.get(
                    f"/events/rush/test_event_id",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                # Check the response status code and body
                assert response.status_code == 200
                assert response.json_body == SAMPLE_RUSH_EVENT

def test_create_rush_category():
    with Client(app) as client:
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"role": "admin"}
            with patch(
                "chalicelib.services.EventsRushService.events_rush_service.create_rush_category"
            ) as mock_create_rush_category:
                mock_create_rush_category.return_value = {"msg": True}
                response = client.http.post(
                    f"/events/rush/category",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                assert response.status_code == 200
                assert response.json_body == {"msg": True}

def test_create_rush_event():
    with Client(app) as client:
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"role": "admin"}
            with patch(
                "chalicelib.services.EventsRushService.events_rush_service.create_rush_event"
            ) as mock_create_rush_event:
                mock_create_rush_event.return_value = {"msg": True}
                response = client.http.post(
                    f"/events/rush",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                assert response.status_code == 200
                assert response.json_body == {"msg": True}

def test_modify_rush_event():
    with Client(app) as client:
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"role": "admin"}
            with patch(
                "chalicelib.services.EventsRushService.events_rush_service.modify_rush_event"
            ) as mock_modify_rush_event:
                mock_modify_rush_event.return_value = {"msg": True}
                response = client.http.patch(
                    f"/events/rush",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                assert response.status_code == 200
                assert response.json_body == {"msg": True}

def test_modify_rush_settings():
    with Client(app) as client:
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"role": "admin"}
            with patch(
                "chalicelib.services.EventsRushService.events_rush_service.modify_rush_settings"
            ) as mock_modify_rush_settings:
                mock_modify_rush_settings.return_value = {"msg": True}
                response = client.http.patch(
                    f"/events/rush/settings",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                assert response.status_code == 200
                assert response.json_body == {"msg": True}

def test_checkin_rush():
    with Client(app) as client:
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"role": "admin"}
            with patch(
                "chalicelib.services.EventsRushService.events_rush_service.checkin_rush"
            ) as mock_checkin_rush:
                mock_checkin_rush.return_value = {"msg": True}
                response = client.http.post(
                    f"/events/rush/checkin/test_event_id",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                assert response.status_code == 200
                assert response.json_body == {"msg": True}

def test_delete_rush_event():
    with Client(app) as client:
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"role": "admin"}
            with patch(
                "chalicelib.services.EventsRushService.events_rush_service.delete_rush_event",
            ) as mock_delete_rush_event:
                mock_delete_rush_event.return_value = {"status": True}
                response = client.http.delete(
                    f"/events/rush/test_event_id",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                assert response.status_code == 200
                assert response.json_body == {'status': True}