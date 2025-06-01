import pytest
from unittest.mock import patch, Mock
from chalicelib.services.ListingService import ListingService
from chalice.app import NotFoundError


SAMPLE_LISTINGS = [
    {
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
    },
    {
        "id": "2",
        "title": "PCT Fall 2024 Rush Application",
        "date_created": "2023-09-15T17:03:29.156Z",
        "deadline": "2023-09-19T04:00:00.000Z",
        "is_visible": True,
        "is_encrypted": False,
        "questions": [],
    },
]


@pytest.fixture
def service():
    with patch("chalicelib.services.ListingService.RepositoryFactory") as mock_factory:
        mock_listings_repo = Mock()
        mock_factory.listings.return_value = mock_listings_repo

        service = ListingService()  # will use the patched RepositoryFactory
        yield service, mock_listings_repo


def test_create_listing(service):
    import uuid

    listing_service, mock_listings_repo = service

    CREATED_LISTING = {
        "title": "test",
        "date_created": "2023-12-26T22:56:20.287Z",
        "deadline": "2023-12-26T22:56:15.035Z",
        "questions": [],
    }

    CREATED_LISTING_ID = uuid.UUID("12345678123456781234567812345678")

    with patch("uuid.uuid4") as mock_uuid:
        # Mock uuid and execute ListingService
        mock_uuid.return_value = CREATED_LISTING_ID
        result = listing_service.create(CREATED_LISTING.copy())

        # Validate listing_repo method call
        expected_data = CREATED_LISTING.copy()
        expected_data["id"] = str(CREATED_LISTING_ID)
        expected_data["is_visible"] = True
        expected_data["is_encrypted"] = False

        mock_listings_repo.create.assert_called_once_with(data=expected_data)
        assert result == {"msg": True}


def test_get_listing(service):
    listing_service, mock_listings_repo = service

    mock_listings_repo.get_by_id.return_value = SAMPLE_LISTINGS[0]

    result = listing_service.get(SAMPLE_LISTINGS[0]["id"])
    mock_listings_repo.get_by_id.assert_called_once_with(
        id_value=SAMPLE_LISTINGS[0]["id"]
    )

    assert result == SAMPLE_LISTINGS[0]


def test_get_all_listings(service):
    listing_service, mock_listings_repo = service

    mock_listings_repo.get_all.return_value = SAMPLE_LISTINGS

    result = listing_service.get_all()
    mock_listings_repo.get_all.assert_called_once()

    assert result == SAMPLE_LISTINGS


def test_delete_listing(service):
    listing_service, mock_listings_repo = service

    mock_listings_repo.delete.return_value = True

    result = listing_service.delete(id=SAMPLE_LISTINGS[0]["id"])
    mock_listings_repo.delete.assert_called_once_with(id_value=SAMPLE_LISTINGS[0]["id"])

    assert result == {"msg": True}


def test_delete_listing_not_found(service):
    listing_service, mock_listings_repo = service

    mock_listings_repo.delete.side_effect = NotFoundError("Listing not found.")

    with pytest.raises(NotFoundError):
        listing_service.delete(SAMPLE_LISTINGS[0]["id"])


def test_toggle_visibility(service):
    listing_service, mock_listings_repo = service

    mock_listing_id = SAMPLE_LISTINGS[0]["id"]
    result = listing_service.toggle_visibility(id=mock_listing_id)

    mock_listings_repo.toggle_boolean_field.assert_called_once_with(
        id_value=SAMPLE_LISTINGS[0]["id"], field="is_visible"
    )

    assert result == {"msg": True}


def test_toggle_visibility_invalid_listing_id(service):
    listing_service, mock_listings_repo = service

    mock_listings_repo.toggle_boolean_field.return_value = None
    mock_listings_repo.toggle_boolean_field.side_effect = NotFoundError(
        "Listing not found."
    )

    mock_listing_id = "3"

    with pytest.raises(NotFoundError):
        listing_service.toggle_visibility(id=mock_listing_id)

    mock_listings_repo.toggle_boolean_field.assert_called_once_with(
        id_value=mock_listing_id, field="is_visible"
    )


def test_toggle_visibility_exception(service):
    listing_service, mock_listings_repo = service

    mock_listings_repo.toggle_boolean_field.return_value = None
    mock_listings_repo.toggle_boolean_field.side_effect = Exception("Error.")

    with pytest.raises(Exception):
        listing_service.toggle_visibility(id=SAMPLE_LISTINGS[0]["id"])

    mock_listings_repo.toggle_boolean_field.assert_called_once_with(
        id_value=SAMPLE_LISTINGS[0]["id"], field="is_visible"
    )


def test_update_field_route(service):
    listing_service, mock_listings_repo = service

    mock_listings_repo.update_field.return_value = None
    mock_listings_repo.update.return_value = None

    result = listing_service.update_field_route(
        SAMPLE_LISTINGS[0]["id"],
        {"field": "title", "value": "new test title"},
    )

    mock_listings_repo.update_field.assert_called_once_with(
        id_value=SAMPLE_LISTINGS[0]["id"], field="title", value="new test title"
    )

    assert result == {"msg": True}


def test_update_field_listing_not_found(service):
    listing_service, mock_listings_repo = service

    mock_listings_repo.update_field.side_effect = NotFoundError("Listing not found.")

    with pytest.raises(NotFoundError) as exc_info:
        listing_service.update_field_route(
            "non_existent_id",
            {"field": "title", "value": "new test title"},
        )

    assert str(exc_info.value) == "Listing not found."


def test_update_field_exception(service):
    listing_service, mock_listings_repo = service

    mock_listings_repo.update_field.side_effect = Exception("Error.")

    with pytest.raises(Exception) as exc_info:
        listing_service.update_field_route(
            "non_existent_id",
            {"field": "title", "value": "new test title"},
        )

    assert str(exc_info.value) == "Error."


def test_toggle_encryption_succeeds(service):
    listing_service, mock_listings_repo = service

    mock_listings_repo.toggle_boolean_field.return_value = True
    mock_listing_id = SAMPLE_LISTINGS[0]["id"]

    result = listing_service.toggle_encryption(mock_listing_id)

    mock_listings_repo.toggle_boolean_field.assert_called_once_with(
        id_value=mock_listing_id, field="is_encrypted"
    )

    assert result == {"msg": True}


def test_toggle_encryption_invalid_listing_id_raises_not_found(service):
    listing_service, mock_listings_repo = service

    mock_listings_repo.toggle_boolean_field.side_effect = NotFoundError("Listing not found: 3.")
    mock_listing_id = "3"

    with pytest.raises(NotFoundError) as exc_info:
        listing_service.toggle_encryption(mock_listing_id)

    mock_listings_repo.toggle_boolean_field.assert_called_once_with(
        id_value=mock_listing_id, field="is_encrypted"
    )

    assert str(exc_info.value) == "Listing not found: 3."