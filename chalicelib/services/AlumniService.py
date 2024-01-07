from chalicelib.db import db
from chalice import NotFoundError, BadRequestError
import uuid


class AlumniService:
    def __init__(self, table_name: str):
        self.table_name = table_name

    def create(self, data):
        id = str(uuid.uuid4())
        data["id"] = id
        db.put_data(self.table_name, data)

        return {"msg": True}

    def get_all(self):
        data = db.get_all(self.table_name)
        return data

    def delete(self, id: str):
        try:
            # Perform delete operation in the database
            deleted_listing = db.delete_item(self.table_name, key={"id": id})

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

    def update(self):
        pass


alumni_service = AlumniService(table_name="zap-alumni")
