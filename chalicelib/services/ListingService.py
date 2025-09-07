from chalice.app import BadRequestError
from chalicelib.repositories.repository_factory import RepositoryFactory
from chalicelib.repositories.base_repository import BaseRepository
from chalicelib.services.service_utils import resolve_repo
from chalicelib.handlers.error_handler import GENERIC_CLIENT_ERROR
from chalice.app import Response, BadRequestError, NotFoundError
from chalicelib.models.application import Application
from chalicelib.modules.ses import ses, SesDestination
from datetime import datetime, timezone
from dateutil import parser
from chalicelib.utils.utils import get_file_extension_from_base64
from chalicelib.s3 import s3
import uuid
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ListingService:
    def __init__(
        self,
        listings_repo: Optional[BaseRepository] = None,
        applications_repo: Optional[BaseRepository] = None,
        event_timeframes_rush_repo: Optional[BaseRepository] = None,
    ):
        self.listings_repo = resolve_repo(listings_repo, RepositoryFactory.listings)
        self.applications_repo = resolve_repo(applications_repo, RepositoryFactory.applications)
        self.events_rush_repo = resolve_repo(event_timeframes_rush_repo, RepositoryFactory.event_timeframes_rush)

    # TODO: prevent duplicate names... (also for rush-category)..
    def create(self, data: dict, include_events_attended: bool):
        id = str(uuid.uuid4())
        data["id"] = id
        data["is_visible"] = True
        data["is_encrypted"] = False

        self.listings_repo.create(data=data)

        rush_timeframe_id = str(uuid.uuid4())
        rush_timeframe_data = {
            "id": rush_timeframe_id,
            "name": data["title"],
            "listing_id": data["id"],
        }

        if include_events_attended:
            self.events_rush_repo.create(rush_timeframe_data)

        return {"msg": True}

    def get(self, id: str):
        data = self.listings_repo.get_by_id(id_value=id)
        return data

    def get_all(self):
        data = self.listings_repo.get_all()
        return data

    def delete(self, id: str):
        self.listings_repo.delete(id_value=id)
        return {"msg": True}

    def toggle_visibility(self, id: str):
        self.listings_repo.toggle_boolean_field(id_value=id, field="is_visible")
        return {"msg": True}

    def toggle_encryption(self, id: str):
        self.listings_repo.toggle_boolean_field(id_value=id, field="is_encrypted")
        return {"msg": True}

    def update_field_route(self, id: str, data: dict):
        # Get field and value from object
        field = data.get("field", None)
        value = data.get("value", None)

        if not (field and value):
            logger.error(f"[ListingService.update_field_route] Invalid inputs: {data}")
            raise BadRequestError(GENERIC_CLIENT_ERROR)

        self.listings_repo.update_field(id_value=id, field=field, value=value)
        return {"msg": True}

    def apply(self, data: dict):
        """Handles the form submission application"""
        applicant_id = str(uuid.uuid4())
        data["id"] = applicant_id

        Application.model_validate(data)

        # Exctract necessary fields
        listing_id = data["listing_id"]
        last_name = data["last_name"]
        first_name = data["first_name"]
        resume = data["resume"]
        image = data["image"]

        # Retrieve deadline and validate current time
        listing_data = self.listings_repo.get_by_id(listing_id)
        deadline = listing_data["deadline"]

        if not listing_data["is_visible"]:
            raise NotFoundError("Invalid listing.")

        deadline_utc = parser.isoparse(deadline).astimezone(timezone.utc)
        curr_time_utc = datetime.now(tz=timezone.utc)

        if curr_time_utc > deadline_utc:
            return Response(
                body="Sorry. The deadline for this application has passed.",
                headers={"Content-Type": "text/plain"},
                status_code=410,
            )

        # Upload resume and retrieve, then set link to data
        resume_path = f"resume/{listing_id}/{last_name}_{first_name}_{applicant_id}.pdf"
        resume_url = s3.upload_binary_data(resume_path, resume)

        # Upload photo and retrieve, then set link to data
        image_extension = get_file_extension_from_base64(image)
        image_path = f"image/{listing_id}/{last_name}_{first_name}_{applicant_id}.{image_extension}"
        image_url = s3.upload_binary_data(image_path, image)

        # Reset data properties as S3 url
        data["resume"], data["image"] = resume_url, image_url

        # Upload data to Supabase
        self.applications_repo.create(data=data)

        # Send confirmation email
        email_content = f"""
            Dear {first_name},<br><br>

            Thank you for applying to Phi Chi Theta, Zeta Chapter. Your application has been received and we will review it shortly.<br><br>

            To find out more about us, visit our website: https://bupct.com/<br><br>

            Regards,<br>
            Phi Chi Theta, Zeta Chapter<br><br>

            ** Please note: Do not reply to this email. This email is sent from an unattended mailbox. Replies will not be read.
        """

        # TODO: Add email exception (invalid email causes error)

        ses_destination = SesDestination(tos=[data["email"]])
        ses.send_email(
            source="noreply@why-phi.com",
            destination=ses_destination,
            subject="Thank you for applying to PCT",
            text=email_content,
            html=email_content,
        )

        return {"msg": True, "resumeUrl": resume_url}
