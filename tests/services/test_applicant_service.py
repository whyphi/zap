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

SAMPLE_APPLICANTS_WITH_EMAILS = [
    {"id": "sample_id1", "name": "John Doe", "email": "john@example.com"},
    {"id": "sample_id2", "name": "Bob", "email": "bob@example.com"},
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
        mock_event_timeframes_rush_repo,
    )


def test_get_applicant(service):
    applicants_service, _, mock_applicants_repo, _, _ = service

    mock_applicants_repo.get_by_id.return_value = SAMPLE_APPLICANTS

    result = applicants_service.get("sample_id")
    mock_applicants_repo.get_by_id.assert_called_once_with(id_value="sample_id")

    assert result == SAMPLE_APPLICANTS


def test_get_all_applicants(service):
    applicants_service, _, mock_applicants_repo, _, _ = service

    mock_applicants_repo.get_all.return_value = SAMPLE_APPLICANTS

    result = applicants_service.get_all()
    mock_applicants_repo.get_all.assert_called_once_with()

    assert result == SAMPLE_APPLICANTS
    assert len(result) == 2


def test_get_all_applicants_from_listing_unencrypted_no_events(service):
    (
        applicants_service,
        _,
        mock_applicants_repo,
        mock_listings_repo,
        mock_event_timeframes_rush_repo,
    ) = service

    mock_applicants_repo.get_all_by_field.return_value = SAMPLE_APPLICANTS
    mock_listings_repo.get_by_id.return_value = SAMPLE_LISTING
    mock_event_timeframes_rush_repo.get_with_custom_select.return_value = None

    result = applicants_service.get_all_from_listing(SAMPLE_LISTING["id"])

    mock_listings_repo.get_by_id.assert_called_once_with(id_value=SAMPLE_LISTING["id"])
    mock_applicants_repo.get_all_by_field.assert_called_once_with(
        field="listing_id", value=SAMPLE_LISTING["id"]
    )

    assert result == SAMPLE_APPLICANTS
    assert len(result) == 2


def test_get_all_applicants_from_listing_with_rush_events(service):
    (
        applicants_service,
        mock_events_rush_service,
        mock_applicants_repo,
        mock_listings_repo,
        mock_event_timeframes_rush_repo,
    ) = service

    mock_applicants_repo.get_all_by_field.return_value = SAMPLE_APPLICANTS_WITH_EMAILS
    mock_listings_repo.get_by_id.return_value = SAMPLE_LISTING
    mock_event_timeframes_rush_repo.get_with_custom_select.return_value = [
        {"id": "rush_timeframe_1"}
    ]
    mock_events_rush_service.get_rush_timeframe_analytics.return_value = {
        "rushees": {
            "rushee_1": {
                "email": "john@example.com",
                "events_attended": [{"id": "event_1", "attended": True}],
                "threshold": True,
            }
        },
        "events": {"event_1": {"name": "Info Session 1"}},
    }

    result = applicants_service.get_all_from_listing(SAMPLE_LISTING["id"])

    assert result[0]["threshold"] is True
    assert result[0]["events"] == {"Info Session 1": True}
    assert "threshold" not in result[1]
    assert "events" not in result[1]


def test_get_all_applicants_from_listing_encrypted_hashes_result(service):
    (
        applicants_service,
        _,
        mock_applicants_repo,
        mock_listings_repo,
        mock_event_timeframes_rush_repo,
    ) = service
    encrypted_listing = {**SAMPLE_LISTING, "is_encrypted": True}
    hashed_applications = [{"id": "hashed"}]

    mock_applicants_repo.get_all_by_field.return_value = SAMPLE_APPLICANTS
    mock_listings_repo.get_by_id.return_value = encrypted_listing
    mock_event_timeframes_rush_repo.get_with_custom_select.return_value = None

    with patch("chalicelib.services.ApplicantService.hash_value") as mock_hash_value:
        mock_hash_value.return_value = hashed_applications
        result = applicants_service.get_all_from_listing(SAMPLE_LISTING["id"])

    mock_hash_value.assert_called_once_with(SAMPLE_APPLICANTS)
    assert result == hashed_applications
