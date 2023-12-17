from chalicelib.db import db
from chalice import NotFoundError

import uuid


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
            app.log.error(f"An error occurred: {str(e)}")
            return {"status": False, "message": "Listing not found"}, 404

        except Exception as e:
            app.log.error(f"An error occurred: {str(e)}")
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

    def update_field_route(self):
        pass


listing_service = ListingService()
