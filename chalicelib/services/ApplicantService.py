from chalicelib.db import db
from chalicelib.services.EventsRushService import events_rush_service
from chalice.app import Response, BadRequestError, NotFoundError
from pydantic import ValidationError
from chalicelib.utils import hash_value
from chalicelib.repositories.repository_factory import RepositoryFactory
from chalicelib.models.application import Application
from chalicelib.modules.ses import ses, SesDestination
from datetime import datetime, timezone
from chalicelib.utils import get_file_extension_from_base64
from chalicelib.db import db
from chalicelib.s3 import s3
import json
import uuid
import logging

logger = logging.getLogger(__name__)


class ApplicantService:
    def __init__(self):
        self.listings_repo = RepositoryFactory.listings()
        self.applications_repo = RepositoryFactory.applications()

    def get(self, id: str):
        data = self.applications_repo.get_by_id(id_value=id)
        return data

    def get_all(self):
        data = self.applications_repo.get_all()
        return data

    def get_all_from_listing(self, id: str):
        listing = db.get_item(table_name="zap-listings", key={"listingId": id})
        data = db.get_applicants(table_name="zap-applications", listing_id=id)

        # automated rush event logic (NOTE: does not override existing rush event logic)
        rush_category_id = listing.get("rushCategoryId", None)
        if rush_category_id:
            analytics = self._get_rush_analytics(rush_category_id)
            attendees = analytics.get("attendees", {})
            events = analytics.get("events", [])

            for applicant in data:
                applicant["events"] = self._get_applicant_events(
                    email=applicant["email"], attendees=attendees, events=events
                )

        if "isEncrypted" in listing and listing["isEncrypted"]:
            data = hash_value(data)

        return data

    def _get_rush_analytics(self, rush_category_id: str) -> dict:
        """Helper method for `get_all_from_listing`"""
        analytics = events_rush_service.get_rush_category_analytics(rush_category_id)
        try:
            return json.loads(analytics)
        except json.JSONDecodeError as e:
            raise BadRequestError(f"Error decoding JSON: {e}")

    def _get_applicant_events(self, email: str, attendees: dict, events: list) -> dict:
        """Helper method for `get_all_from_listing`"""
        return {
            event["eventName"]: any(
                event_attended["eventId"] == event["eventId"]
                for event_attended in attendees.get(email, {}).get("eventsAttended", [])
            )
            for event in events
        }

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

        deadline_utc = datetime.fromisoformat(deadline).astimezone(timezone.utc)
        curr_time_utc = datetime.now(tz=timezone.utc)

        if curr_time_utc > deadline_utc:
            return Response(
                body="Sorry. The deadline for this application has passed.",
                headers={"Content-Type": "text/plain"},
                status_code=410,
            )

        # Date tests...
        # datetime_deadline_est = deadline_utc.astimezone(ZoneInfo("America/New_York"))
        # curr_time_utc = datetime.now(timezone.utc)
        # curr_time_est = curr_time_utc.astimezone(ZoneInfo("America/New_York"))
        # pretty_format = "%d/%m/%Y %I:%M %p"
        # print(f"[UTC] Current Time:    {curr_time_utc.strftime(pretty_format)}")
        # print(f"[UTC] Deadline:        {deadline_utc.strftime(pretty_format)}")
        # print(f"[EST] Current Time:    {curr_time_est.strftime(pretty_format)}")
        # print(f"[EST] Deadline:        {datetime_deadline_est.strftime(pretty_format)}")

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


applicant_service = ApplicantService()
