import pytest
from unittest.mock import patch, Mock
from chalicelib.services.ApplicantService import ApplicantService
from chalicelib.services.ListingService import ListingService


@pytest.fixture
def service():
    with patch(
        "chalicelib.services.ApplicantService.RepositoryFactory"
    ) as mock_factory:
        mock_applicants_repo = Mock()
        mock_listings_repo = Mock()
        mock_factory.applications.return_value = mock_applicants_repo
        mock_factory.listings.return_value = mock_listings_repo

        # services: will use the patched RepositoryFactory
        applicants_service = ApplicantService()
        listings_service = ListingService()
        yield applicants_service, listings_service, mock_applicants_repo, mock_listings_repo


def test_get_applicant(service):
    applicants_service, _, mock_applicants_repo, _ = service

    sample_data = {"id": "sample_id", "name": "John Doe"}
    mock_applicants_repo.get_by_id.return_value = sample_data

    result = applicants_service.get("sample_id")
    mock_applicants_repo.get_by_id.assert_called_once_with(id_value="sample_id")

    assert result == sample_data


def test_get_all_applicants(service):
    applicants_service, _, mock_applicants_repo, _ = service

    sample_data = [
        {"id": "sample_id1", "name": "John Doe"},
        {"id": "sample_id2", "name": "Bob"},
    ]
    mock_applicants_repo.get_all.return_value = sample_data

    result = applicants_service.get_all()
    mock_applicants_repo.get_all.assert_called_once_with()

    assert result == sample_data
    assert len(result) == 2


# def test_get_all_applicants_from_listing(service):
#     applicant_service, mock_db = service

#     listing_id = "1"
#     sample_data = [
#         {"applicantId": "sample_id1", "name": "John Doe"},
#         {"applicantId": "sample_id2", "name": "Bob"},
#     ]
#     mock_db.get_applicants.return_value = sample_data
#     mock_db.get_item.return_value = {}

#     result = applicant_service.get_all_from_listing(listing_id)
#     mock_db.get_applicants.assert_called_once_with(
#         table_name="zap-applications", listing_id=listing_id
#     )

#     assert result == sample_data
#     assert len(result) == 2
