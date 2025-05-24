from chalicelib.db import db
from chalicelib.services.EventsRushService import events_rush_service
from chalice.app import Response, BadRequestError, NotFoundError
from pydantic import ValidationError
from chalicelib.utils import hash_value
from chalicelib.models.application import Application
from chalicelib.modules.ses import ses, SesDestination
from datetime import datetime, timedelta, timezone
from chalicelib.utils import get_file_extension_from_base64
from chalicelib.utils import CaseConverter, JSONType
from chalicelib.handlers.error_handler import GENERIC_CLIENT_ERROR
from chalicelib.db import db
from chalicelib.s3 import s3
import json
import uuid
import logging

logger = logging.getLogger(__name__)


class ApplicantService:
    def __init__(self):
        pass

    def get(self, id: str):
        data = db.get_item(table_name="zap-applications", key={"applicantId": id})
        return data

    def get_all(self):
        data = db.get_all(table_name="zap-applications")
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

    def apply(self, data: JSONType):
        """Handles the form submission application"""
        if not isinstance(data, dict):
            raise ValueError("Expected a dictionary")

        data["gradYear"] = "2025"
        applicant_id = str(uuid.uuid4())
        data["id"] = applicant_id

        data = CaseConverter.convert_keys(
            data=data, convert_func=CaseConverter.to_snake_case
        )

        if not isinstance(data, dict):
            logger.error(f"[ApplicantService.apply] Invalid inputs: {data}")
            raise ValidationError(GENERIC_CLIENT_ERROR)

        Application.model_validate(data)

        # TODO: implement remaining function
        raise Exception

        listing_data = db.get_item(
            table_name="zap-listings", key={"listingId": data["listingId"]}
        )

        if not listing_data["isVisible"]:
            raise NotFoundError("Invalid listing.")

        deadline = datetime.strptime(listing_data["deadline"], "%Y-%m-%dT%H:%M:%S.%f%z")
        utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
        curr_est_time = utc_now.astimezone(timezone(timedelta(hours=-5)))

        if curr_est_time > deadline:
            return Response(
                body="Sorry. The deadline for this application has passed.",
                headers={"Content-Type": "text/plain"},
                status_code=410,
            )

        applicant_id = str(uuid.uuid4())
        data["applicantId"] = applicant_id
        data["dateApplied"] = curr_est_time.isoformat()

        # Upload resume and retrieve, then set link to data
        resume_path = f"resume/{data['listingId']}/{data['lastName']}_{data['firstName']}_{applicant_id}.pdf"
        resume_url = s3.upload_binary_data(resume_path, data["resume"])

        # Upload photo and retrieve, then set link to data
        image_extension = get_file_extension_from_base64(data["image"])
        image_path = f"image/{data['listingId']}/{data['lastName']}_{data['firstName']}_{applicant_id}.{image_extension}"
        image_url = s3.upload_binary_data(image_path, data["image"])

        # Reset data properties as S3 url
        data["resume"], data["image"] = resume_url, image_url

        # Upload data to DynamoDB
        db.put_data(table_name="zap-applications", data=data)

        # Send confirmation email
        email_content = f"""
            Dear {data["firstName"]},<br><br>

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
