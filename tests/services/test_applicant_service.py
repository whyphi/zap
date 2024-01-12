import pytest
from unittest.mock import MagicMock, patch
from chalicelib.services.ApplicantService import ApplicantService


@pytest.fixture
def service():
    with patch("chalicelib.services.ApplicantService.db") as mock_db:
        yield ApplicantService(), mock_db


def test_get_applicant(service):
    applicant_service, mock_db = service

    sample_data = {"applicantId": "sample_id", "name": "John Doe"}
    mock_db.get_item.return_value = sample_data

    result = applicant_service.get("sample_id")
    mock_db.get_item.assert_called_once_with(
        table_name="zap-applications", key={"applicantId": "sample_id"}
    )

    assert result == sample_data


def test_get_all_applicants(service):
    applicant_service, mock_db = service

    sample_data = [
        {"applicantId": "sample_id1", "name": "John Doe"},
        {"applicantId": "sample_id2", "name": "Bob"},
    ]
    mock_db.get_all.return_value = sample_data

    result = applicant_service.get_all()
    mock_db.get_all.assert_called_once_with(
        table_name="zap-applications"
    )

    assert result == sample_data
    assert len(result) == 2

def test_get_all_applicants_from_listing(service):
    applicant_service, mock_db = service

    listing_id = "1"
    sample_data = [
        {"applicantId": "sample_id1", "name": "John Doe"},
        {"applicantId": "sample_id2", "name": "Bob"},
    ]
    mock_db.get_applicants.return_value = sample_data

    result = applicant_service.get_all_from_listing(listing_id)
    mock_db.get_applicants.assert_called_once_with(
        table_name="zap-applications",
        listing_id=listing_id
    )

    assert result == sample_data
    assert len(result) == 2