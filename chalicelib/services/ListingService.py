from chalice.app import NotFoundError, Response
from chalicelib.models.application import Application
from chalicelib.validators.listings import UpdateFieldRequest
from chalicelib.repositories.repository_factory import RepositoryFactory
from chalicelib.db import db
from chalicelib.s3 import s3
from chalicelib.utils import get_file_extension_from_base64
from chalicelib.modules.ses import ses, SesDestination
from chalicelib.services.EventsRushService import events_rush_service
from chalicelib.utils import convert_to_camel_case, convert_to_snake_case
import json
import uuid
from datetime import datetime, timedelta, timezone
from pydantic import ValidationError


class ListingService:
    def __init__(self):
        self.listings_repo = RepositoryFactory.listings()

    # TODO: prevent duplicate names... (also for rush-category)
    def create(self, data: dict):
        data = convert_to_snake_case(data=data)
        id = str(uuid.uuid4())
        data["id"] = id
        data["is_visible"] = True
        data["date_created"] = datetime.now(timezone.utc).isoformat()
        data["is_encrypted"] = False

        # TODO: check for dup name BEFORE going to rush-category creation
        # if includeEventsAttended, create corresponding rush category (and create foreign-key)
        # if data.get("includeEventsAttended", None):
        #     events_rush_data = {"name": data["title"], "defaultRushCategory": False}
        #     rush_category_id = events_rush_service.create_rush_category(
        #         data=events_rush_data
        #     )
        #     data["rushCategoryId"] = str(rush_category_id)

        self.listings_repo.create(data=data)

        return {"msg": True}

    def apply(self, data):
        """Handles the form submission application"""

        try:
            Application.model_validate(data)

            listing_data = db.get_item(
                table_name="zap-listings", key={"listingId": data["listingId"]}
            )

            if not listing_data["isVisible"]:
                raise NotFoundError("Invalid listing.")

            deadline = datetime.strptime(
                listing_data["deadline"], "%Y-%m-%dT%H:%M:%S.%f%z"
            )
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

        except ValidationError as e:
            return {"msg": False, "error": str(e)}

    def get(self, id: str):
        data = self.listings_repo.get_by_id(id_value=id)
        return convert_to_camel_case(data)

    def get_all(self):
        data = self.listings_repo.get_all()
        return convert_to_camel_case(data)

    # TODO: also delete corresponding rush-category
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
        field = data["field"]
        value = data["value"]

        self.listings_repo.update_field(id_value=id, field=field, value=value)
        return {"msg": True}


listing_service = ListingService()
