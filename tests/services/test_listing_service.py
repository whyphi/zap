import pytest
from unittest.mock import MagicMock, patch
from chalicelib.services.ListingService import ListingService

SAMPLE_LISTING = {
    "deadline": "2023-09-19T04:00:00.000Z",
    "dateCreated": "2023-09-15T17:03:29.156Z",
    "questions": [
        {
            "question": "Tell us about yourself. What are you passionate about/what motivates you? (200 words max)",
            "additional": "",
        },
        {"question": "Why did you rush PCT? (200 words max)", "additional": ""},
        {
            "question": " How do you plan to contribute to PCT? Why should we choose you? (200 words max)",
            "additional": "",
        },
        {
            "question": "What are your career goals, and why did you choose this particular path? (200 words max)",
            "additional": "",
        },
        {
            "question": "Describe your most notable brother interaction at any rush event. (200 words max)",
            "additional": "",
        },
        {"question": "Which rush events did you attend?", "additional": ""},
    ],
    "listingId": "1",
    "isVisible": True,
    "title": "PCT Fall 2023 Rush Application",
}


@pytest.fixture
def service():
    with patch("chalicelib.services.ListingService.db") as mock_db:
        yield ListingService(), mock_db


def test_create_listing(service):
    import uuid

    CREATED_LISTING = {
        "title": "test",
        "questions": [],
        "deadline": "2023-12-26T22:56:15.035Z",
        "dateCreated": "2023-12-26T22:56:20.287Z",
    }
    CREATED_LISTING_ID = "12345678123456781234567812345678"

    with patch("uuid.uuid4") as mock_uuid:
        mock_uuid.return_value = uuid.UUID(CREATED_LISTING_ID)
        listing_service, mock_db = service
        result = listing_service.create(CREATED_LISTING)

        CREATED_LISTING["listingId"] = CREATED_LISTING_ID
        CREATED_LISTING["isVisislbe"] = True
        mock_db.put_data.assert_called_once_with(
            table_name="zap-listings", data=CREATED_LISTING
        )

        assert result == {"msg": True}


def test_get_listing(service):
    listing_service, mock_db = service

    mock_db.get_item.return_value = SAMPLE_LISTING

    result = listing_service.get(SAMPLE_LISTING["listingId"])
    mock_db.get_item.assert_called_once_with(
        table_name="zap-listings", key={"listingId": SAMPLE_LISTING["listingId"]}
    )

    assert result == SAMPLE_LISTING
