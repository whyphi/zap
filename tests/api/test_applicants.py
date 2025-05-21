from chalice.test import Client
from unittest.mock import patch


from app import app

TEST_APPLICANTS = [
    {"applicantId": "sample_id1", "name": "John Doe"},
    {"applicantId": "sample_id2", "name": "Bob"},
]


def test_get_applicant():
    # Create a Chalice test client
    with Client(app) as client:
        # Mock applicant_service's get method
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"roles": ["admin"]}

            with patch(
                "chalicelib.services.ApplicantService.applicant_service.get"
            ) as mock_get:
                mock_get.return_value = TEST_APPLICANTS[0]
                response = client.http.get(
                    f"/applicant/{TEST_APPLICANTS[0]['applicantId']}",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )
                # Check the response status code and body
                assert response.status_code == 200
                assert response.json_body == TEST_APPLICANTS[0]


def test_get_all_applicants():
    # Create a Chalice test client
    with Client(app) as client:
        # Mock applicant_service's get method
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"roles": ["admin"]}
            with patch(
                "chalicelib.services.ApplicantService.applicant_service.get_all"
            ) as mock_get_all:
                mock_get_all.return_value = TEST_APPLICANTS
                response = client.http.get(
                    "/applicants",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                # Check the response status code and body
                assert response.status_code == 200
                assert response.json_body == TEST_APPLICANTS


def test_get_all_applicants_from_listing():
    # Create a Chalice test client
    with Client(app) as client:
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"roles": ["admin"]}
            with patch(
                "chalicelib.services.ApplicantService.applicant_service.get_all_from_listing"
            ) as mock_get_all_from_listing:
                mock_get_all_from_listing.return_value = TEST_APPLICANTS
                response = client.http.get(
                    "/applicants/test_listing_id",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                # Check the response status code and body
                assert response.status_code == 200
                assert response.json_body == TEST_APPLICANTS
