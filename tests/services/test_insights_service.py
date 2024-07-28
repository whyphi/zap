import pytest
from unittest.mock import patch
from chalicelib.services.InsightsService import InsightsService
import copy
import json

# Load JSON data from a file (insights test - general)
with open("tests/fixtures/insights/general/sample_applicants.json") as f:
    SAMPLE_APPLICANTS = json.load(f)

with open("tests/fixtures/insights/general/sample_dashboard.json") as f:
    SAMPLE_DASHBOARD = json.load(f)

with open("tests/fixtures/insights/general/sample_distribution.json") as f:
    SAMPLE_DISTRIBUTION = json.load(f)

# Load JSON data from a file (insights test - no applicants)
with open("tests/fixtures/insights/noApplicants/sample_applicants.json") as f:
    SAMPLE_APPLICANTS_NO_APP = json.load(f)

with open("tests/fixtures/insights/noApplicants/sample_dashboard.json") as f:
    SAMPLE_DASHBOARD_NO_APP = json.load(f)

with open("tests/fixtures/insights/noApplicants/sample_distribution.json") as f:
    SAMPLE_DISTRIBUTION_NO_APP = json.load(f)

# Load JSON data from a file (insights test - applicant with no gpa)
with open("tests/fixtures/insights/noGPAs/sample_applicants.json") as f:
    SAMPLE_APPLICANTS_NO_GPA = json.load(f)

with open("tests/fixtures/insights/noGPAs/sample_dashboard.json") as f:
    SAMPLE_DASHBOARD_NO_GPA = json.load(f)

with open("tests/fixtures/insights/noGPAs/sample_distribution.json") as f:
    SAMPLE_DISTRIBUTION_NO_GPA = json.load(f)


@pytest.fixture
def service():
    with patch("chalicelib.services.InsightsService.db") as mock_db:
        yield InsightsService(), mock_db


def test_get_insights(service):
    insights_service, mock_db = service

    listing_id = "1"
    # whenever get_item is called on the fake db, sample_data will be returned (create a deepcopy since it is being mutated)
    mock_db.get_applicants.return_value = copy.deepcopy(SAMPLE_APPLICANTS)

    result = insights_service.get_insights_from_listing(listing_id)
    # confirm that database was called once with correct inputs
    mock_db.get_applicants.assert_called_once_with(
        table_name="zap-applications", listing_id=listing_id
    )

    # Convert Python dictionary to JSON format for comparison
    result_dash = json.dumps(result[0], sort_keys=True)
    result_dist = json.dumps(result[1], sort_keys=True)

    # Convert boolean values to lowercase strings
    result_dash = result_dash.replace("True", "true").replace("False", "false")
    result_dist = result_dist.replace("True", "true").replace("False", "false")

    assert len(result) == 2
    assert result_dash == json.dumps(SAMPLE_DASHBOARD, sort_keys=True)
    assert result_dist == json.dumps(SAMPLE_DISTRIBUTION, sort_keys=True)


def test_get_insights_no_applicants(service):
    insights_service, mock_db = service

    listing_id = "1"
    # whenever get_item is called on the fake db, sample_data will be returned (create a deepcopy since it is being mutated)
    mock_db.get_applicants.return_value = copy.deepcopy(SAMPLE_APPLICANTS_NO_APP)

    result = insights_service.get_insights_from_listing(listing_id)
    # confirm that database was called once with correct inputs
    mock_db.get_applicants.assert_called_once_with(
        table_name="zap-applications", listing_id=listing_id
    )

    # Convert Python dictionary to JSON format for comparison
    result_dash = json.dumps(result[0], sort_keys=True)
    result_dist = json.dumps(result[1], sort_keys=True)

    # Convert boolean values to lowercase strings
    result_dash = result_dash.replace("True", "true").replace("False", "false")
    result_dist = result_dist.replace("True", "true").replace("False", "false")

    assert len(result) == 2
    assert result_dash == json.dumps(SAMPLE_DASHBOARD_NO_APP, sort_keys=True)
    assert result_dist == json.dumps(SAMPLE_DISTRIBUTION_NO_APP, sort_keys=True)


def test_get_insights_no_gpas(service):
    insights_service, mock_db = service

    listing_id = "1"
    # whenever get_item is called on the fake db, sample_data will be returned (create a deepcopy since it is being mutated)
    mock_db.get_applicants.return_value = copy.deepcopy(SAMPLE_APPLICANTS_NO_GPA)

    result = insights_service.get_insights_from_listing(listing_id)
    # confirm that database was called once with correct inputs
    mock_db.get_applicants.assert_called_once_with(
        table_name="zap-applications", listing_id=listing_id
    )

    # Convert Python dictionary to JSON format for comparison
    result_dash = json.dumps(result[0], sort_keys=True)
    result_dist = json.dumps(result[1], sort_keys=True)

    # Convert boolean values to lowercase strings
    result_dash = result_dash.replace("True", "true").replace("False", "false")
    result_dist = result_dist.replace("True", "true").replace("False", "false")

    assert len(result) == 2
    assert result_dash == json.dumps(SAMPLE_DASHBOARD_NO_GPA, sort_keys=True)
    assert result_dist == json.dumps(SAMPLE_DISTRIBUTION_NO_GPA, sort_keys=True)
