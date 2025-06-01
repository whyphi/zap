import pytest
from unittest.mock import patch, Mock
from chalicelib.services.ApplicantService import ApplicantService
from datetime import datetime, timezone
import uuid

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
    with patch(
        "chalicelib.services.ApplicantService.RepositoryFactory"
    ) as mock_factory:
        mock_applicants_repo = Mock()
        mock_listings_repo = Mock()
        mock_factory.applications.return_value = mock_applicants_repo
        mock_factory.listings.return_value = mock_listings_repo

        # services: will use the patched RepositoryFactory
        applicants_service = ApplicantService()
        yield applicants_service, mock_applicants_repo, mock_listings_repo


def test_get_applicant(service):
    applicants_service, mock_applicants_repo, _ = service

    mock_applicants_repo.get_by_id.return_value = SAMPLE_APPLICANTS

    result = applicants_service.get("sample_id")
    mock_applicants_repo.get_by_id.assert_called_once_with(id_value="sample_id")

    assert result == SAMPLE_APPLICANTS


def test_get_all_applicants(service):
    applicants_service, mock_applicants_repo, _ = service

    mock_applicants_repo.get_all.return_value = SAMPLE_APPLICANTS

    result = applicants_service.get_all()
    mock_applicants_repo.get_all.assert_called_once_with()

    assert result == SAMPLE_APPLICANTS
    assert len(result) == 2


def test_get_all_applicants_from_listing_unencrypted(service):
    applicants_service, mock_applicants_repo, mock_listings_repo = service

    mock_listings_repo.get_by_id.return_value = SAMPLE_LISTING
    mock_applicants_repo.get_all_by_field.return_value = SAMPLE_APPLICANTS

    result = applicants_service.get_all_from_listing(SAMPLE_LISTING["id"])

    mock_listings_repo.get_by_id.assert_called_once_with(id_value=SAMPLE_LISTING["id"])
    mock_applicants_repo.get_all_by_field.assert_called_once_with(
        field="listing_id", value=SAMPLE_LISTING["id"]
    )

    assert result == SAMPLE_APPLICANTS
    assert len(result) == 2


@patch(
    "chalicelib.services.ApplicantService.uuid.uuid4",
    return_value=uuid.UUID("12345678-1234-5678-1234-567812345678"),
)
@patch("chalicelib.services.ApplicantService.Application.model_validate")
@patch(
    "chalicelib.services.ApplicantService.get_file_extension_from_base64",
    return_value="png",
)
@patch("chalicelib.services.ApplicantService.s3.upload_binary_data")
@patch("chalicelib.services.ApplicantService.ses.send_email")
@patch("chalicelib.services.ApplicantService.datetime")
def test_apply_success(
    mock_datetime,
    mock_send_email,
    mock_upload,
    mock_get_ext,
    mock_validate,
    mock_uuid,
    service,
):
    applicants_service, mock_applicants_repo, mock_listings_repo = service

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

    result = applicants_service.apply(application_data.copy())

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
