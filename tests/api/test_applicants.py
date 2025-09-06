import os

os.environ["CHALICE_TESTING"] = "1"

from chalice.test import Client
from unittest.mock import Mock, patch
import pytest
from chalicelib.api import applicants

from app import app

TEST_APPLICANTS = [
    {"id": "sample_id1", "name": "John Doe"},
    {"id": "sample_id2", "name": "Bob"},
]


@pytest.fixture(scope="module")
def test_client():
    # Create mocks for the services this api needs
    mock_applicants_service = Mock()

    # Register the routes on the listings blueprint using the mock service
    applicants.register_routes(applicant_service=mock_applicants_service)

    # Attach blueprint to the Chalice app (this makes routes available)
    app.register_blueprint(applicants.applicants_api)

    # Use the Chalice test client
    with Client(app) as client:
        # yield tuple so tests can access both client and mocks
        yield client, mock_applicants_service


def test_get_applicant(test_client):
    client, mock_applicant_service = test_client
    mock_applicant_service.get.return_value = TEST_APPLICANTS[0]

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}
        response = client.http.get(
            f"/applicant/{TEST_APPLICANTS[0]['id']}",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

        assert response.status_code == 200
        assert response.json_body == TEST_APPLICANTS[0]


def test_get_all_applicants(test_client):
    client, mock_applicant_service = test_client
    mock_applicant_service.get_all.return_value = TEST_APPLICANTS

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}
        response = client.http.get(
            f"/applicants",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

        assert response.status_code == 200
        assert response.json_body == TEST_APPLICANTS


def test_get_all_applicants_from_listing(test_client):
    client, mock_applicant_service = test_client
    mock_applicant_service.get_all_from_listing.return_value = TEST_APPLICANTS

    with patch("chalicelib.decorators.jwt.decode") as mock_decode:
        mock_decode.return_value = {"roles": ["admin"]}
        response = client.http.get(
            f"/applicants/test_listing_id",
            headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
        )

        assert response.status_code == 200
        assert response.json_body == TEST_APPLICANTS
