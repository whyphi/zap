import pytest
from unittest.mock import patch, Mock
from chalicelib.services.ListingService import ListingService
from chalice import NotFoundError
from pydantic import ValidationError
import json


SAMPLE_LISTINGS = [
    {
        "deadline": "2023-09-19T04:00:00.000Z",
        "dateCreated": "2023-09-15T17:03:29.156Z",
        "questions": [
            {
                "question": "Tell us about yourself. What are you passionate about/what motivates you? (200 words max)",
                "additional": "",
            },
        ],
        "listingId": "1",
        "isVisible": True,
        "title": "PCT Fall 2023 Rush Application",
    },
    {
        "deadline": "2023-09-19T04:00:00.000Z",
        "dateCreated": "2023-09-15T17:03:29.156Z",
        "questions": [],
        "listingId": "2",
        "isVisible": True,
        "title": "PCT Fall 2024 Rush Application",
    },
]


@pytest.fixture
def service():
    with patch("chalicelib.services.ListingService.db") as mock_db:
        yield ListingService(), mock_db


def test_create_listing(service):
    import uuid

    listing_service, mock_db = service

    CREATED_LISTING = {
        "title": "test",
        "questions": [],
        "deadline": "2023-12-26T22:56:15.035Z",
        "dateCreated": "2023-12-26T22:56:20.287Z",
    }
    CREATED_LISTING_ID = "12345678123456781234567812345678"

    with patch("uuid.uuid4") as mock_uuid:
        mock_uuid.return_value = uuid.UUID(CREATED_LISTING_ID)
        result = listing_service.create(CREATED_LISTING)
        CREATED_LISTING["listingId"] = CREATED_LISTING_ID
        CREATED_LISTING["isVisislbe"] = True
        mock_db.put_data.assert_called_once_with(
            table_name="zap-listings", data=CREATED_LISTING
        )

        assert result == {"msg": True}


def test_get_listing(service):
    listing_service, mock_db = service

    mock_db.get_item.return_value = SAMPLE_LISTINGS[0]

    result = listing_service.get(SAMPLE_LISTINGS[0]["listingId"])
    mock_db.get_item.assert_called_once_with(
        table_name="zap-listings", key={"listingId": SAMPLE_LISTINGS[0]["listingId"]}
    )

    assert result == SAMPLE_LISTINGS[0]


def test_get_all_listings(service):
    listing_service, mock_db = service

    mock_db.get_all.return_value = SAMPLE_LISTINGS

    result = listing_service.get_all()
    mock_db.get_all.assert_called_once_with(table_name="zap-listings")

    assert result == SAMPLE_LISTINGS


def test_delete_listing(service):
    listing_service, mock_db = service

    mock_db.delete_item.return_value = True

    result = listing_service.delete(SAMPLE_LISTINGS[0]["listingId"])
    assert result["statusCode"] == 200


def test_delete_listing_not_found(service):
    listing_service, mock_db = service

    mock_db.delete_item.return_value = False

    result = listing_service.delete(SAMPLE_LISTINGS[0]["listingId"])

    assert result["statusCode"] == 404


def test_delete_listing_exception(service):
    listing_service, mock_db = service

    mock_db.delete_item.side_effect = Exception("Error")

    result = listing_service.delete(SAMPLE_LISTINGS[0]["listingId"])

    assert result["statusCode"] == 500


def test_toggle_visibility(service):
    listing_service, mock_db = service

    mock_db.toggle_visibility.return_value = True
    mock_listing_id = SAMPLE_LISTINGS[0]["listingId"]

    result = json.loads(listing_service.toggle_visibility(mock_listing_id))

    mock_db.toggle_visibility.assert_called_once_with(
        table_name="zap-listings", key={"listingId": mock_listing_id}
    )
    assert result["statusCode"] == 200


def test_toggle_visibility_invalid_listing_id(service):
    listing_service, mock_db = service

    mock_db.toggle_visibility.return_value = None
    mock_listing_id = "3"

    result = json.loads(listing_service.toggle_visibility(mock_listing_id))

    mock_db.toggle_visibility.assert_called_once_with(
        table_name="zap-listings", key={"listingId": mock_listing_id}
    )

    print(result)

    assert result["statusCode"] == 400


def test_toggle_visibility_exception(service):
    listing_service, mock_db = service

    mock_db.toggle_visibility.side_effect = Exception("Error")

    result = json.loads(
        listing_service.toggle_visibility(SAMPLE_LISTINGS[0]["listingId"])
    )
    assert result["statusCode"] == 500


def test_update_field_route(service):
    listing_service, mock_db = service

    # Mocking UpdateFieldRequest
    with patch(
        "chalicelib.validators.listings.UpdateFieldRequest"
    ) as MockUpdateFieldRequest:
        # Simulating the behavior of UpdateFieldRequest
        MockUpdateFieldRequest.return_value.field = "title"
        MockUpdateFieldRequest.return_value.value = "new test title"

        mock_db.get_item.return_value = SAMPLE_LISTINGS[0]
        mock_updated_listing = SAMPLE_LISTINGS[0]
        mock_updated_listing["title"] = "new test title"

        mock_db.update_listing_field.return_value = mock_updated_listing

        result = json.loads(
            listing_service.update_field_route(
                SAMPLE_LISTINGS[0]["listingId"],
                {"field": "title", "value": "new test title"},
            )
        )

        assert result["statusCode"] == 200
        assert result["updated_listing"] == mock_updated_listing


def test_update_field_listing_not_found(service):
    listing_service, mock_db = service

    with patch(
        "chalicelib.validators.listings.UpdateFieldRequest"
    ) as MockUpdateFieldRequest:
        # Simulating the behavior of UpdateFieldRequest
        MockUpdateFieldRequest.return_value.field = "title"
        MockUpdateFieldRequest.return_value.value = "new test title"

        mock_db.get_item.return_value = {}

        with pytest.raises(NotFoundError) as exc_info:
            listing_service.update_field_route(
                "non_existent_id",
                {"field": "title", "value": "new test title"},
            )

        assert str(exc_info.value) == "Listing not found"


def test_update_field_updated_listing_not_found(service):
    listing_service, mock_db = service

    with patch(
        "chalicelib.validators.listings.UpdateFieldRequest"
    ) as MockUpdateFieldRequest:
        # Simulating the behavior of UpdateFieldRequest
        MockUpdateFieldRequest.return_value.field = "title"
        MockUpdateFieldRequest.return_value.value = "new test title"

        mock_db.get_item.return_value = SAMPLE_LISTINGS[0]

        mock_updated_listing = SAMPLE_LISTINGS[0]
        mock_updated_listing["title"] = "new test title"
        mock_db.update_listing_field.return_value = None

        with pytest.raises(NotFoundError) as exc_info:
            listing_service.update_field_route(
                SAMPLE_LISTINGS[0]["listingId"],
                {"field": "title", "value": "new test title"},
            )

        assert str(exc_info.value) == "Listing not found"


def test_update_field_validation_error(service):
    listing_service, _ = service

    validation_error_mock = Mock()
    validation_error_mock.side_effect = ValidationError.from_exception_data(
        title="Invalid data", line_errors=[]
    )

    # Using pytest.raises to check if a ValidationError is raised
    with pytest.raises(Exception) as exc_info:
        listing_service.update_field_route(
            SAMPLE_LISTINGS[0]["listingId"],
            {"field": "non_existent_field", "value": "new test title"},
        )

    exc_msgs = str(exc_info.value).split("\n")
    exc_msgs = [msg.strip() for msg in exc_msgs]

    assert exc_msgs[0] == "1 validation error for UpdateFieldRequest"
    assert (
        exc_msgs[2]
        == "Value error, Invalid field: non_existent_field. Allowed fields: ['listingId', 'dateCreated', 'deadline', 'isVisible', 'isEncrypted', 'questions', 'title'] [type=value_error, input_value='non_existent_field', input_type=str]"
    )


def test_update_field_exception(service):
    listing_service, mock_db = service

    with patch(
        "chalicelib.validators.listings.UpdateFieldRequest"
    ) as MockUpdateFieldRequest:
        MockUpdateFieldRequest.return_value.field = "title"
        MockUpdateFieldRequest.return_value.value = "new test title"

        mock_db.get_item.side_effect = Exception("Error")

        with pytest.raises(Exception) as exc_info:
            listing_service.update_field_route(
                SAMPLE_LISTINGS[0]["listingId"],
                {"field": "title", "value": "new test title"},
            )

        assert str(exc_info.value) == "Error"


def test_toggle_encryption_succeeds(service):
    listing_service, mock_db = service

    mock_db.toggle_encryption.return_value = True
    mock_listing_id = SAMPLE_LISTINGS[0]["listingId"]

    result = json.loads(listing_service.toggle_encryption(mock_listing_id))

    mock_db.toggle_encryption.assert_called_once_with(
        table_name="zap-listings", key={"listingId": mock_listing_id}
    )
    assert result["statusCode"] == 200


def test_toggle_encryption_invalid_listing_id_raises_not_found(service):
    listing_service, mock_db = service

    mock_db.toggle_encryption.return_value = None
    mock_listing_id = "3"

    with pytest.raises(NotFoundError) as exc_info:
        listing_service.toggle_encryption(mock_listing_id)

    mock_db.toggle_encryption.assert_called_once_with(
        table_name="zap-listings", key={"listingId": mock_listing_id}
    )

    assert str(exc_info.value) == "Listing not found: 3"
