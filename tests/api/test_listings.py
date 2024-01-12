from chalice.app import Request
from chalice.test import Client
from unittest.mock import MagicMock, patch

from chalice import NotFoundError, BadRequestError


from app import app

TEST_LISTINGS = [
    {
        "deadline": "2023-09-19T04:00:00.000Z",
        "dateCreated": "2023-09-15T17:03:29.156Z",
        "questions": [
            {
                "question": "Tell us about yourself. What are you passionate about/what motivates you? (200 words max)",
                "additional": "",
            },
        ],
        "listingId": "1",
        "isVisible": True,
        "title": "PCT Fall 2023 Rush Application",
    },
    {
        "deadline": "2023-09-19T04:00:00.000Z",
        "dateCreated": "2023-09-15T17:03:29.156Z",
        "questions": [],
        "listingId": "2",
        "isVisible": True,
        "title": "PCT Fall 2024 Rush Application",
    },
]


def test_create_listing():
    with Client(app) as client:
        with patch(
            "chalicelib.services.ListingService.listing_service.create"
        ) as mock_create:
            mock_create.return_value = {"msg": True}
            response = client.http.post(f"/create")

            assert response.status_code == 200
            assert response.json_body == {"msg": True}


def test_get_listing():
    with Client(app) as client:
        with patch(
            "chalicelib.services.ListingService.listing_service.get"
        ) as mock_get:
            mock_get.return_value = TEST_LISTINGS[0]
            response = client.http.get(f"/listings/{TEST_LISTINGS[0]['listingId']}")

            assert response.status_code == 200
            assert response.json_body == TEST_LISTINGS[0]


def test_get_all_listings():
    with Client(app) as client:
        with patch(
            "chalicelib.services.ListingService.listing_service.get_all"
        ) as mock_get_all:
            mock_get_all.return_value = TEST_LISTINGS
            response = client.http.get(f"/listings")

            assert response.status_code == 200
            assert response.json_body == TEST_LISTINGS


def test_delete_listing():
    with Client(app) as client:
        with patch(
            "chalicelib.services.ListingService.listing_service.delete"
        ) as mock_delete:
            mock_delete.return_value = {"status": True}
            response = client.http.delete(f"/listings/{TEST_LISTINGS[0]['listingId']}")

            assert response.status_code == 200
            assert response.json_body == {"status": True}


def test_toggle_visibility():
    with Client(app) as client:
        with patch(
            "chalicelib.services.ListingService.listing_service.toggle_visibility"
        ) as mock_toggle_visibility:
            mock_toggle_visibility.return_value = {"status": True}
            response = client.http.patch(
                f"/listings/{TEST_LISTINGS[0]['listingId']}/toggle/visibility"
            )

            assert response.status_code == 200
            assert response.json_body == {"status": True}


def test_update_listing_field_route():
    with Client(app) as client:
        with patch(
            "chalicelib.services.ListingService.listing_service.update_field_route"
        ) as mock_update_field_route:
            mock_update_field_route.return_value = {
                "status": True,
                "updated_listing": TEST_LISTINGS[1],
            }
            response = client.http.patch(
                f"/listings/{TEST_LISTINGS[1]['listingId']}/update-field"
            )

            print(response.json_body)

            assert response.status_code == 200
            assert response.json_body == {
                "status": True,
                "updated_listing": TEST_LISTINGS[1],
            }


def test_update_listing_field_route_not_found():
    with Client(app) as client:
        with patch(
            "chalicelib.services.ListingService.listing_service.update_field_route"
        ) as mock_update_field_route:
            mock_update_field_route.side_effect = NotFoundError("Not found")

            response = client.http.patch(
                f"/listings/{TEST_LISTINGS[1]['listingId']}/update-field"
            )

            body, status_code = response.json_body

            assert status_code == 404
            assert body == {
                "status": False,
                "message": "Not found",
            }


def test_update_listing_field_route_bad_request():
    with Client(app) as client:
        with patch(
            "chalicelib.services.ListingService.listing_service.update_field_route"
        ) as mock_update_field_route:
            mock_update_field_route.side_effect = BadRequestError("Bad request")

            response = client.http.patch(
                f"/listings/{TEST_LISTINGS[1]['listingId']}/update-field"
            )

            body, status_code = response.json_body

            assert status_code == 400
            assert body == {
                "status": False,
                "message": "Bad request",
            }


def test_update_listing_field_route_exception():
    with Client(app) as client:
        with patch(
            "chalicelib.services.ListingService.listing_service.update_field_route"
        ) as mock_update_field_route:
            mock_update_field_route.side_effect = Exception("Error")

            response = client.http.patch(
                f"/listings/{TEST_LISTINGS[1]['listingId']}/update-field"
            )

            body, status_code = response.json_body

            assert status_code == 500
            assert body == {
                "status": False,
                "message": "Internal Server Error",
            }
