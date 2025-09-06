import pytest
from unittest.mock import patch, Mock
from chalicelib.services.ApplicantService import ApplicantService

SAMPLE_LISTING = {
    "id": "1",
    "title": "PCT Fall 2023 Rush Application",
    "date_created": "2023-09-15T17:03:29.156Z",
    "deadline": "2023-09-19T04:00:00.000Z",
    "is_visible": True,
    "is_encrypted": False,
    "questions": [
        {
            "question": "Tell us about yourself. What are you passionate about/what motivates you? (200 words max)",
            "context": "",
        },
    ],
}


SAMPLE_APPLICANTS = [
    {"id": "sample_id1", "name": "John Doe"},
    {"id": "sample_id2", "name": "Bob"},
]


@pytest.fixture
def service():
    mock_applicants_repo = Mock()
    mock_listings_repo = Mock()
    mock_event_timeframes_rush_repo = Mock()
    mock_events_rush_service = Mock()

    mock_applicants_service = ApplicantService(
        applications_repo=mock_applicants_repo,
        listings_repo=mock_listings_repo,
        event_timeframes_rush_repo=mock_event_timeframes_rush_repo,
        events_rush_service=mock_events_rush_service,
    )
    return (
        mock_applicants_service,
        mock_events_rush_service,
        mock_applicants_repo,
        mock_listings_repo,
        # TODO: potentially yield and test events (mock_event_timeframes_rush_repo, mock_events_rush_service)
    )


def test_get_applicant(service):
    applicants_service, _, mock_applicants_repo, _ = service

    mock_applicants_repo.get_by_id.return_value = SAMPLE_APPLICANTS

    result = applicants_service.get("sample_id")
    mock_applicants_repo.get_by_id.assert_called_once_with(id_value="sample_id")

    assert result == SAMPLE_APPLICANTS


# def test_get_all_applicants(service):
#     applicants_service, mock_applicants_repo, _ = service

#     mock_applicants_repo.get_all.return_value = SAMPLE_APPLICANTS

#     result = applicants_service.get_all()
#     mock_applicants_repo.get_all.assert_called_once_with()

#     assert result == SAMPLE_APPLICANTS
#     assert len(result) == 2


# def test_get_all_applicants_from_listing_unencrypted(service):
#     applicants_service, mock_applicants_repo, mock_listings_repo = service

#     mock_listings_repo.get_by_id.return_value = SAMPLE_LISTING
#     mock_applicants_repo.get_all_by_field.return_value = SAMPLE_APPLICANTS

#     result = applicants_service.get_all_from_listing(SAMPLE_LISTING["id"])

#     mock_listings_repo.get_by_id.assert_called_once_with(id_value=SAMPLE_LISTING["id"])
#     mock_applicants_repo.get_all_by_field.assert_called_once_with(
#         field="listing_id", value=SAMPLE_LISTING["id"]
#     )

#     assert result == SAMPLE_APPLICANTS
#     assert len(result) == 2
