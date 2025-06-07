import pytest
from unittest.mock import patch, Mock
from chalicelib.services.ListingService import ListingService
from chalice.app import NotFoundError
from chalice.app import Response, NotFoundError
from datetime import datetime, timezone
import uuid

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
        mock_applicants_repo = Mock()
        mock_listings_repo = Mock()
        mock_factory.applications.return_value = mock_applicants_repo
        mock_factory.listings.return_value = mock_listings_repo

        # services: will use the patched RepositoryFactory
        listing_service = ListingService()
        yield listing_service, mock_listings_repo, mock_applicants_repo


def test_create_listing(service):
    import uuid

    listing_service, mock_listings_repo, _ = service

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
    listing_service, mock_listings_repo, _ = service

    mock_listings_repo.get_by_id.return_value = SAMPLE_LISTINGS[0]

    result = listing_service.get(SAMPLE_LISTINGS[0]["id"])
    mock_listings_repo.get_by_id.assert_called_once_with(
        id_value=SAMPLE_LISTINGS[0]["id"]
    )

    assert result == SAMPLE_LISTINGS[0]


def test_get_all_listings(service):
    listing_service, mock_listings_repo, _ = service

    mock_listings_repo.get_all.return_value = SAMPLE_LISTINGS

    result = listing_service.get_all()
    mock_listings_repo.get_all.assert_called_once_with()

    assert result == SAMPLE_LISTINGS


def test_delete_listing(service):
    listing_service, mock_listings_repo, _ = service

    mock_listings_repo.delete.return_value = True

    result = listing_service.delete(id=SAMPLE_LISTINGS[0]["id"])
    mock_listings_repo.delete.assert_called_once_with(id_value=SAMPLE_LISTINGS[0]["id"])

    assert result == {"msg": True}


def test_delete_listing_not_found(service):
    listing_service, mock_listings_repo, _ = service

    mock_listings_repo.delete.side_effect = NotFoundError("Listing not found.")

    with pytest.raises(NotFoundError):
        listing_service.delete(SAMPLE_LISTINGS[0]["id"])


def test_toggle_visibility(service):
    listing_service, mock_listings_repo, _ = service

    mock_listing_id = SAMPLE_LISTINGS[0]["id"]
    result = listing_service.toggle_visibility(id=mock_listing_id)

    mock_listings_repo.toggle_boolean_field.assert_called_once_with(
        id_value=SAMPLE_LISTINGS[0]["id"], field="is_visible"
    )

    assert result == {"msg": True}


def test_toggle_visibility_invalid_listing_id(service):
    listing_service, mock_listings_repo, _ = service

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
    listing_service, mock_listings_repo, _ = service

    mock_listings_repo.toggle_boolean_field.return_value = None
    mock_listings_repo.toggle_boolean_field.side_effect = Exception("Error.")

    with pytest.raises(Exception):
        listing_service.toggle_visibility(id=SAMPLE_LISTINGS[0]["id"])

    mock_listings_repo.toggle_boolean_field.assert_called_once_with(
        id_value=SAMPLE_LISTINGS[0]["id"], field="is_visible"
    )


def test_update_field_route(service):
    listing_service, mock_listings_repo, _ = service

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
    listing_service, mock_listings_repo, _ = service

    mock_listings_repo.update_field.side_effect = NotFoundError("Listing not found.")

    with pytest.raises(NotFoundError) as exc_info:
        listing_service.update_field_route(
            "non_existent_id",
            {"field": "title", "value": "new test title"},
        )

    assert str(exc_info.value) == "Listing not found."


def test_update_field_exception(service):
    listing_service, mock_listings_repo, _ = service

    mock_listings_repo.update_field.side_effect = Exception("Error.")

    with pytest.raises(Exception) as exc_info:
        listing_service.update_field_route(
            "non_existent_id",
            {"field": "title", "value": "new test title"},
        )

    assert str(exc_info.value) == "Error."


def test_toggle_encryption_succeeds(service):
    listing_service, mock_listings_repo, _ = service

    mock_listings_repo.toggle_boolean_field.return_value = True
    mock_listing_id = SAMPLE_LISTINGS[0]["id"]

    result = listing_service.toggle_encryption(mock_listing_id)

    mock_listings_repo.toggle_boolean_field.assert_called_once_with(
        id_value=mock_listing_id, field="is_encrypted"
    )

    assert result == {"msg": True}


def test_toggle_encryption_invalid_listing_id_raises_not_found(service):
    listing_service, mock_listings_repo, _ = service

    mock_listings_repo.toggle_boolean_field.side_effect = NotFoundError(
        "Listing not found: 3."
    )
    mock_listing_id = "3"

    with pytest.raises(NotFoundError) as exc_info:
        listing_service.toggle_encryption(mock_listing_id)

    mock_listings_repo.toggle_boolean_field.assert_called_once_with(
        id_value=mock_listing_id, field="is_encrypted"
    )

    assert str(exc_info.value) == "Listing not found: 3."


@patch(
    "chalicelib.services.ListingService.uuid.uuid4",
    return_value=uuid.UUID("12345678-1234-5678-1234-567812345678"),
)
@patch("chalicelib.services.ListingService.Application.model_validate")
@patch(
    "chalicelib.services.ListingService.get_file_extension_from_base64",
    return_value="png",
)
@patch("chalicelib.services.ListingService.s3.upload_binary_data")
@patch("chalicelib.services.ListingService.ses.send_email")
@patch("chalicelib.services.ListingService.datetime")
def test_apply_success(
    mock_datetime,
    mock_send_email,
    mock_upload,
    mock_get_ext,
    mock_validate,
    mock_uuid,
    service,
):
    listing_service, mock_listings_repo, mock_applicants_repo = service

    # Setup fixed current time and deadline
    mock_datetime.now.return_value = datetime(2023, 9, 10, tzinfo=timezone.utc)
    mock_datetime.fromisoformat.return_value = datetime(
        2023, 9, 19, tzinfo=timezone.utc
    )

    # Mock listing from repo
    mock_listings_repo.get_by_id.return_value = {
        "deadline": "2023-09-19T04:00:00.000Z",
        "is_visible": True,
    }

    # Mock S3 upload return values
    mock_upload.side_effect = [
        "https://s3/resume.pdf",
        "https://s3/image.png",
    ]

    # Sample application input
    application_data = {
        "listing_id": "1",
        "first_name": "Jane",
        "last_name": "Doe",
        "resume": b"resume-bytes",
        "image": "base64-image-data",
        "email": "jane@example.com",
    }

    result = listing_service.apply(application_data.copy())

    # Validate calls and result
    mock_validate.assert_called_once()
    assert mock_upload.call_count == 2
    assert mock_send_email.called
    mock_applicants_repo.create.assert_called_once()

    assert result == {
        "msg": True,
        "resumeUrl": "https://s3/resume.pdf",
    }

    # Also check that `resume` and `image` were replaced with URLs
    uploaded_data = mock_applicants_repo.create.call_args[1]["data"]
    assert uploaded_data["resume"] == "https://s3/resume.pdf"
    assert uploaded_data["image"] == "https://s3/image.png"


@patch("chalicelib.services.ListingService.Application.model_validate")
def test_apply_listing_not_found(model_validate, service):
    listing_service, mock_listings_repo, _ = service

    # Mock invisible listing
    mock_listings_repo.get_by_id.return_value = {
        "is_visible": False,
        "deadline": "2100-01-01T00:00:00.000Z",
    }

    with pytest.raises(NotFoundError, match="Invalid listing."):
        listing_service.apply(
            {
                "listing_id": "1",
                "last_name": "Doe",
                "first_name": "John",
                "resume": "fake_resume",
                "image": "fake_image",
                "email": "john@example.com",
            }
        )


@patch("chalicelib.services.ListingService.datetime")
@patch("chalicelib.services.ListingService.Application.model_validate")
def test_apply_deadline_passed(mock_validate, mock_datetime, service):
    listing_service, mock_listings_repo, _ = service

    # Listing is visible but deadline is in the past
    mock_listings_repo.get_by_id.return_value = {
        "is_visible": True,
        "deadline": "2000-01-01T00:00:00.000+00:00",
    }

    # Force "now" to be far in the future
    mock_datetime.now.return_value = datetime(2025, 1, 1, tzinfo=timezone.utc)
    mock_datetime.fromisoformat.side_effect = datetime.fromisoformat

    response = listing_service.apply(
        {
            "listing_id": "1",
            "last_name": "Doe",
            "first_name": "John",
            "resume": "fake_resume",
            "image": "fake_image",
            "email": "john@example.com",
        }
    )

    assert isinstance(response, Response)
    assert response.status_code == 410
    assert "deadline" in response.body.lower()
