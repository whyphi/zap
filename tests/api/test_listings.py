import os
os.environ["CHALICE_TESTING"] = "1"

import json
from chalice.test import Client
from unittest.mock import Mock, patch
from chalice.app import NotFoundError, BadRequestError
import pytest
from app import app
from chalicelib.api import listings


TEST_LISTINGS = [
    {
        "id": "1",
        "deadline": "2023-09-19T04:00:00.000Z",
        "date_created": "2023-09-15T17:03:29.156Z",
        "questions": [
            {
                "question": "Tell us about yourself. What are you passionate about/what motivates you? (200 words max)",
                "additional": "",
            },
        ],
        "is_visible": True,
        "is_encrypted": False,
        "title": "PCT Fall 2023 Rush Application",
    },
    {
        "id": "2",
        "deadline": "2023-09-19T04:00:00.000Z",
        "date_created": "2023-09-15T17:03:29.156Z",
        "questions": [],
        "is_visible": True,
        "is_encrypted": False,
        "title": "PCT Fall 2024 Rush Application",
    },
]


@pytest.fixture(scope="module")
def test_client():
    # Create mocks for the services this api needs
    mock_listing_service = Mock()

    # Register the routes on the listings blueprint using the mock service
    listings.register_routes(listing_service=mock_listing_service)

    # Attach blueprint to the Chalice app (this makes routes available)
    app.register_blueprint(listings.listings_api)

    # Use the Chalice test client
    with Client(app) as client:
        # yield tuple so tests can access both client and mocks
        yield client, mock_listing_service


def test_create_listing(test_client):
    client, mock_listing_service = test_client

    mock_listing_service.create.return_value = {"msg": True}

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}

        response = client.http.post(
            "/listings/create",
            headers={
                "Authorization": "Bearer SAMPLE_TOKEN_STRING",
                "Content-Type": "application/json",
            },
            body=json.dumps(
                {"title": "Test Listing", "include_events_attended": False}
            ),
        )

    assert response.status_code == 200
    assert response.json_body == {"msg": True}
    mock_listing_service.create.assert_called_once_with(
        {"title": "Test Listing"}, False
    )


def test_get_listing(test_client):
    client, mock_listing_service = test_client
    mock_listing_service.get.return_value = TEST_LISTINGS[0]

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}
        response = client.http.get(
            f"/listings/{TEST_LISTINGS[0]['id']}",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

    assert response.status_code == 200
    assert response.json_body == TEST_LISTINGS[0]
    mock_listing_service.get.assert_called_once_with(TEST_LISTINGS[0]["id"])


def test_get_all_listings(test_client):
    client, mock_listing_service = test_client
    mock_listing_service.get_all.return_value = TEST_LISTINGS

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}
        response = client.http.get(
            "/listings",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

    assert response.status_code == 200
    assert response.json_body == TEST_LISTINGS
    mock_listing_service.get_all.assert_called_once()


def test_delete_listing(test_client):
    client, mock_listing_service = test_client
    mock_listing_service.delete.return_value = {"status": True}

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}
        response = client.http.delete(
            f"/listings/{TEST_LISTINGS[0]['id']}",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

    assert response.status_code == 200
    assert response.json_body == {"status": True}
    mock_listing_service.delete.assert_called_once_with(TEST_LISTINGS[0]["id"])


def test_toggle_visibility(test_client):
    client, mock_listing_service = test_client
    mock_listing_service.toggle_visibility.return_value = {"status": True}

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}
        response = client.http.patch(
            f"/listings/{TEST_LISTINGS[0]['id']}/toggle/visibility",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

    assert response.status_code == 200
    assert response.json_body == {"status": True}
    mock_listing_service.toggle_visibility.assert_called_once_with(
        TEST_LISTINGS[0]["id"]
    )


def test_update_listing_field_route(test_client):
    client, mock_listing_service = test_client
    mock_listing_service.update_field_route.return_value = {
        "status": True,
        "updated_listing": TEST_LISTINGS[1],
    }

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}
        response = client.http.patch(
            f"/listings/{TEST_LISTINGS[1]['id']}/update-field",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

    assert response.status_code == 200
    assert response.json_body == {
        "status": True,
        "updated_listing": TEST_LISTINGS[1],
    }
    mock_listing_service.update_field_route.assert_called_once_with(
        TEST_LISTINGS[1]["id"], None
    )


def test_update_listing_field_route_not_found(test_client):
    client, mock_listing_service = test_client
    mock_listing_service.update_field_route.side_effect = NotFoundError("Not found")

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}
        response = client.http.patch(
            f"/listings/{TEST_LISTINGS[1]['id']}/update-field",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

    assert response.status_code == 404
    assert response.json_body == {"Message": "Not found", "Code": "NotFoundError"}


def test_update_listing_field_route_bad_request(test_client):
    client, mock_listing_service = test_client
    mock_listing_service.update_field_route.side_effect = BadRequestError("Bad request")

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}
        response = client.http.patch(
            f"/listings/{TEST_LISTINGS[1]['id']}/update-field",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

    assert response.status_code == 400
    assert response.json_body == {"Code": "BadRequestError", "Message": "Bad request"}


def test_update_listing_field_route_exception(test_client):
    client, mock_listing_service = test_client
    mock_listing_service.update_field_route.side_effect = Exception("Error")

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}
        response = client.http.patch(
            f"/listings/{TEST_LISTINGS[1]['id']}/update-field",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

    assert response.status_code == 500
    assert response.json_body == {"error": "Internal Server Error", "message": "Error"}


def test_toggle_encryption_succeeds(test_client):
    client, mock_listing_service = test_client
    mock_listing_service.toggle_encryption.return_value = {"status": True}

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}
        response = client.http.patch(
            f"/listings/{TEST_LISTINGS[0]['id']}/toggle/encryption",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

    assert response.status_code == 200
    assert response.json_body == {"status": True}
    mock_listing_service.toggle_encryption.assert_called_once_with(
        TEST_LISTINGS[0]["id"]
    )


def test_toggle_encryption_invalid_id_raises_not_found(test_client):
    client, mock_listing_service = test_client
    mock_listing_service.toggle_encryption.side_effect = NotFoundError("empty id")

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}
        response = client.http.patch(
            f"/listings/{TEST_LISTINGS[0]['id']}/toggle/encryption",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

    assert response.status_code == 404
    assert response.json_body == {"Message": "empty id", "Code": "NotFoundError"}
