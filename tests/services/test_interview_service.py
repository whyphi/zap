import pytest
import datetime
from unittest.mock import MagicMock, patch
from chalice import NotFoundError
from chalicelib.services.InterviewService import InterviewService

SAMPLE_INTERVIEW_LISTING = [
    {
        "title": "test 1",
        "semester": "spring",
        "questions": [],
        "deadline": "2023-09-19T04:00:00.000Z",
        "isVisible": True,
        "active": True,
        "type": "Case",
        "response_ids": [],
    },
    {
        "title": "test 2",
        "semester": "spring",
        "questions": [],
        "deadline": "2023-09-19T04:00:00.001Z",
        "isVisible": False,
        "active": True,
        "type": "Case",
        "response_ids": ["response_id_1", "response_id_2"],
    },
]


@pytest.fixture
def service():
    with patch("chalicelib.services.InterviewService.mongo_module") as mock_mongo:
        yield InterviewService(), mock_mongo


def test_create_interview_listing(service):
    interview_service, mock_mongo = service

    CREATED_LISTING = {
        "title": "test",
        "semester": "spring",
        "questions": [],
        "type": "technical",
        "response_ids": [],
        "deadline": "2023-12-26T22:56:15.035Z",
    }
    with patch("datetime.datetime") as mock_datetime:
        mock_now = datetime.datetime(2023, 1, 1, 12, 0)
        mock_datetime.now.return_value = mock_now

        interview_service.create_interview(CREATED_LISTING)

        expected_data = CREATED_LISTING.copy()
        expected_data["dateCreated"] = mock_now

        mock_mongo.insert_document.assert_called_once_with(
            "interviews-listings", expected_data
        )


def test_get_interview_listing(service):
    interview_service, mock_mongo = service

    mock_mongo.get_document_by_id.return_value = SAMPLE_INTERVIEW_LISTING[0]

    result = interview_service.get_interview_listing("123")

    assert result == (
        '{"title": "test 1", "semester": "spring", "questions": [], '
        '"deadline": "2023-09-19T04:00:00.000Z", "isVisible": true, '
        '"active": true, "type": "Case", "response_ids": []}'
    )


def test_get_all_interivews(service):
    interview_service, mock_mongo = service

    mock_mongo.get_all_data_from_collection.return_value = SAMPLE_INTERVIEW_LISTING

    result = interview_service.get_all_interviews()

    assert result == (
        '[{"title": "test 1", "semester": "spring", "questions": [], '
        '"deadline": "2023-09-19T04:00:00.000Z", "isVisible": true, '
        '"active": true, "type": "Case", "response_ids": []}, '
        '{"title": "test 2", "semester": "spring", "questions": [], '
        '"deadline": "2023-09-19T04:00:00.001Z", "isVisible": false, '
        '"active": true, "type": "Case", "response_ids": ["response_id_1", "response_id_2"]}]'
    )


def test_delete_interview_listing_with_nonexisting_interview(service):
    interview_service, mock_mongo = service

    nonexistent_id = "nonexistent123"
    mock_mongo.get_document_by_id.return_value = None

    with pytest.raises(NotFoundError) as excinfo:
        interview_service.delete_interview_listing(nonexistent_id)

    assert (
        str(excinfo.value)
        == f"Interview Listing with ID {nonexistent_id} does not exist."
    )
    mock_mongo.get_document_by_id.assert_called_once_with(
        "interviews-listings", nonexistent_id
    )
    mock_mongo.delete_document_by_id.assert_not_called()


def test_delete_interview_listing_with_no_responses(service):
    interview_service, mock_mongo = service

    interview_listing_id = "123"
    mock_mongo.delete_document_by_id.return_value = False
    mock_mongo.get_document_by_id.return_value = SAMPLE_INTERVIEW_LISTING[0]

    interview_service.delete_interview_listing(interview_listing_id)

    mock_mongo.get_document_by_id.assert_called_once_with(
        "interviews-listings", interview_listing_id
    )

    assert mock_mongo.delete_document_by_id.call_count == 1
    mock_mongo.delete_document_by_id.assert_any_call(
        "interviews-listings", interview_listing_id
    )

def test_delete_interview_listing(service):
    interview_service, mock_mongo = service

    interview_listing_id = "123"
    mock_mongo.delete_document_by_id.return_value = False
    mock_mongo.get_document_by_id.return_value = SAMPLE_INTERVIEW_LISTING[1]

    interview_service.delete_interview_listing(interview_listing_id)

    mock_mongo.get_document_by_id.assert_called_once_with(
        "interviews-listings", interview_listing_id
    )

    assert mock_mongo.delete_document_by_id.call_count == 3
    mock_mongo.delete_document_by_id.assert_any_call(
        "interviews-responses", "response_id_1"
    )
    mock_mongo.delete_document_by_id.assert_any_call(
        "interviews-responses", "response_id_2"
    )
    mock_mongo.delete_document_by_id.assert_any_call(
        "interviews-listings", interview_listing_id
    )
