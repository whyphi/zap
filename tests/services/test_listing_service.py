import pytest
from unittest.mock import MagicMock, patch
from chalicelib.services.ListingService import ListingService

SAMPLE_LISTING = {
    "website": "why-phi.com",
    "listingId": "123",
    "colleges": {
        "COM": False,
        "QST": False,
        "CDS": False,
        "CAS": False,
        "Wheelock": False,
        "Sargent": False,
        "Pardee": False,
        "SHA": False,
        "CGS": False,
        "ENG": True,
        "CFA": False,
        "Other": False
    },
    "responses": [],
    "lastName": "lastName",
    "linkedin": "linkedin.com",
    "email": "test@test.com",
    "firstName": "firstName",
    "applicantId": "1",
    "minor": "test",
    "image": "https://whyphi-zap.s3.amazonaws.com/prod/image/584bdc74-edfd-48e1-9905-d354f40430f6/test_test_2d1ec5ed-11e6-4258-bb6a-4dcaea085f96.png",
    "gpa": "test",
    "gradYear": "test",
    "resume": "https://whyphi-zap.s3.amazonaws.com/prod/resume/584bdc74-edfd-48e1-9905-d354f40430f6/test_test_2d1ec5ed-11e6-4258-bb6a-4dcaea085f96.pdf",
    "major": "test",
    "phone": "123-123-1234",
    "preferredName": "test"
}


@pytest.fixture
def service():
    with patch("chalicelib.services.ListingService.db") as mock_db:
        yield ListingService(), mock_db


def test_get_listing(service):
    listing_service, mock_db = service

    mock_db.get_item.return_value = SAMPLE_LISTING

    result = listing_service.get(SAMPLE_LISTING["listingId"])
    mock_db.get_item.assert_called_once_with(
        table_name="zap-listings", key={"listingId": SAMPLE_LISTING["listingId"]}
    )

    assert result == SAMPLE_LISTING
