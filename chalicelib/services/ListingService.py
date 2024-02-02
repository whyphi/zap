from chalice import NotFoundError, Response
from chalicelib.models.application import Application
from chalicelib.validators.listings import UpdateFieldRequest
from chalicelib.db import db
from chalicelib.s3 import s3
from chalicelib.utils import get_file_extension_from_base64
from chalicelib.modules.ses import ses, SesDestination

import json
import uuid
from datetime import datetime, timedelta, timezone

from pydantic import ValidationError


class ListingService:
    def __init__(self):
        pass

    def create(self, data):
        listing_id = str(uuid.uuid4())
        data["listingId"] = listing_id
        data["isVisible"] = True

        db.put_data(table_name="zap-listings", data=data)

        return {"msg": True}

    def apply(self, data):
        """Handles the form submission application"""

        """
        TODO: Implement validator for deadline and isVisible
        - Since making an additional call to fetch listing data is unnecessary, maybe the frontend can pass these
        attributes as a header, that the backend can read and validate before processing the data. 
        - The apply method can take in deadline and isVisible as another input to work with.
        """

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
        data = db.get_item(table_name="zap-listings", key={"listingId": id})
        return data

    def get_all(self):
        data = db.get_all(table_name="zap-listings")
        return data

    def delete(self, id: str):
        try:
            # Perform delete operation in the database
            deleted_listing = db.delete_item(
                table_name="zap-listings", key={"listingId": id}
            )

            # Check the result and return the appropriate response
            if deleted_listing:
                return {"statusCode": 200}
            else:
                raise NotFoundError("Listing not found")

        except NotFoundError as e:
            # app.log.error(f"An error occurred: {str(e)}")
            return {"statusCode": 404, "message": "Listing not found"}

        except Exception as e:
            # app.log.error(f"An error occurred: {str(e)}")
            return {"statusCode": 500, "message": "Internal Server Error"}

    def toggle_visibility(self, id: str):
        try:
            # Perform visibility toggle in the database
            data = db.toggle_visibility(
                table_name="zap-listings", key={"listingId": id}
            )

            # Check the result and return the appropriate response
            if data:
                return json.dumps({"statusCode": 200})
            else:
                return json.dumps({"statusCode": 400, "message": "Invalid listing ID"})

        except Exception as e:
            return json.dumps({"statusCode": 500, "message": str(e)})

    def update_field_route(self, id, data):
        try:
            request_body = UpdateFieldRequest(**data)

            # Get field and value from object
            field = request_body.field
            new_value = request_body.value

            # Check if the listing exists
            existing_listing = db.get_item(
                table_name="zap-listings", key={"listingId": id}
            )
            if not existing_listing:
                raise NotFoundError("Listing not found")

            # Update the specified field in the database
            updated_listing = db.update_listing_field(
                table_name="zap-listings",
                key={"listingId": id},
                field=field,
                new_value=new_value,
            )

            # Check the result and return the appropriate response
            if updated_listing:
                return json.dumps(
                    {"statusCode": 200, "updated_listing": updated_listing}
                )
            else:
                raise NotFoundError("Listing not found")

        except ValidationError as e:
            # https://aws.github.io/chalice/topics/views.html
            # app.log.error(f"An error occurred: {str(e)}")
            raise Exception(str(e))

        except NotFoundError as e:
            # app.log.error(f"An error occurred: {str(e)}")
            raise NotFoundError(str(e))  # Let the caller handle this exception

        except Exception as e:
            # app.log.error(f"An error occurred: {str(e)}")
            raise Exception(e)  # Re-raise the exception for global handling


listing_service = ListingService()
