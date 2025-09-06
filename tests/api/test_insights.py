from chalice.test import Client
from unittest.mock import patch
import json

from app import app

with open("tests/fixtures/insights/general/sample_dashboard.json") as f:
    SAMPLE_DASHBOARD = json.load(f)

with open("tests/fixtures/insights/general/sample_distribution.json") as f:
    SAMPLE_DISTRIBUTION = json.load(f)


def test_get_insights_from_listing():
    # Create a Chalice test client
    with Client(app) as client:
        # Mock applicant_service's get method
        with patch("chalicelib.decorators.jwt.decode") as mock_decode:
            # Assuming the decoded token has the required role
            mock_decode.return_value = {"roles": ["admin"]}
            with patch(
                "chalicelib.services.InsightsService.insights_service.get_insights_from_listing",
            ) as mock_get_insights_from_listing:
                mock_get_insights_from_listing.return_value = [
                    SAMPLE_DASHBOARD,
                    SAMPLE_DISTRIBUTION,
                ]
                response = client.http.get(
                    "/insights/listing/test_listing_id",
                    headers={"Authorization": "Bearer SAMPLE_TOKEN_STRING"},
                )

                # Check the response status code and body
                assert response.status_code == 200
                assert response.json_body == [SAMPLE_DASHBOARD, SAMPLE_DISTRIBUTION]
