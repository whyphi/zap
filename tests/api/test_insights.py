from chalice.app import Request
from chalice.test import Client
from unittest.mock import MagicMock, patch
import json

from app import app

with open('tests/fixtures/sample_dashboard.json') as f:
    SAMPLE_DASHBOARD = json.load(f)

with open('tests/fixtures/sample_distribution.json') as f:
    SAMPLE_DISTRIBUTION = json.load(f)


def test_get_insights_from_listing():
    # Create a Chalice test client
    with Client(app) as client:
        # Mock applicant_service's get method
        with patch(
            "chalicelib.services.InsightsService.insights_service.get_insights_from_listing"
        ) as mock_get_insights_from_listing:
            mock_get_insights_from_listing.return_value = [SAMPLE_DASHBOARD, SAMPLE_DISTRIBUTION]
            response = client.http.get(f"/insights/listing/test_listing_id")

            # Check the response status code and body
            assert response.status_code == 200
            assert response.json_body == [SAMPLE_DASHBOARD, SAMPLE_DISTRIBUTION]