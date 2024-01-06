from chalicelib.db import db
from chalice import NotFoundError, BadRequestError
from chalicelib.validators.listings import UpdateFieldRequest

import uuid
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
                return {"status": True}
            else:
                raise NotFoundError("Listing not found")

        except NotFoundError as e:
            # app.log.error(f"An error occurred: {str(e)}")
            return {"status": False, "message": "Listing not found"}, 404

        except Exception as e:
            # app.log.error(f"An error occurred: {str(e)}")
            return {"status": False, "message": "Internal Server Error"}, 500

    def toggle_visibility(self, id: str):
        try:
            # Perform visibility toggle in the database
            data = db.toggle_visibility(
                table_name="zap-listings", key={"listingId": id}
            )

            # Check the result and return the appropriate response
            if data:
                return {"status": True}
            else:
                return {"status": False, "message": "Invalid listing ID"}, 400

        except Exception as e:
            return {"status": False, "message": "Internal Server Error"}, 500

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
                return {"status": True, "updated_listing": updated_listing}
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
