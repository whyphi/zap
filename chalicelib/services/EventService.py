from chalicelib.modules.mongo import mongo_module
from chalice import NotFoundError, BadRequestError, UnauthorizedError
import json
from bson import ObjectId
import datetime
from chalicelib.modules.google_sheets import GoogleSheetsModule
from chalicelib.modules.ses import ses, SesDestination
from chalicelib.s3 import s3

class EventService:
    class BSONEncoder(json.JSONEncoder):
        """JSON encoder that converts Mongo ObjectIds and datetime.datetime to strings."""

        def default(self, o):
            if isinstance(o, datetime.datetime):
                return o.isoformat()
            elif isinstance(o, ObjectId):
                return str(o)
            return super().default(o)

    def __init__(self, mongo_module=mongo_module):
        self.mongo_module = mongo_module
        self.collection_prefix = "events-"

    def create_timeframe(self, timeframe_data: dict):
        timeframe_data["dateCreated"] = datetime.datetime.now()
        self.mongo_module.insert_document(
            collection=f"{self.collection_prefix}timeframe", data=timeframe_data
        )
        return {"msg": True}

    def get_timeframe(self, timeframe_id: str):
        timeframe = self.mongo_module.get_document_by_id(
            collection=f"{self.collection_prefix}timeframe", document_id=timeframe_id
        )

        return json.dumps(timeframe, cls=self.BSONEncoder)

    def get_all_timeframes(self):
        """Retrieve all timeframes from the database."""
        timeframes = self.mongo_module.get_all_data_from_collection(
            f"{self.collection_prefix}timeframe"
        )

        return json.dumps(timeframes, cls=self.BSONEncoder)

    def delete_timeframe(self, timeframe_id: str):
        # Check if timeframe exists and if it doesn't return errors
        timeframe = self.mongo_module.get_document_by_id(
            f"{self.collection_prefix}timeframe", timeframe_id
        )

        if timeframe is None:
            raise NotFoundError(f"Timeframe with ID {timeframe_id} does not exist.")

        # If timeframe exists, get the eventIds (children)
        event_ids = [str(event["_id"]) for event in timeframe["events"]]

        # Delete all the events in the timeframe
        for event_id in event_ids:
            self.mongo_module.delete_document_by_id(
                f"{self.collection_prefix}event", event_id
            )

        # If timeframe exists, delete the timeframe document
        self.mongo_module.delete_document_by_id(
            f"{self.collection_prefix}timeframe", timeframe_id
        )
        
        return {"statusCode": 200}

    def create_event(self, timeframe_id: str, event_data: dict):
        event_data["dateCreated"] = datetime.datetime.now()
        event_data["timeframeId"] = timeframe_id
        event_data["usersAttended"] = []

        # Get Google Spreadsheet ID from timeframe
        timeframe_doc = self.mongo_module.get_document_by_id(
            f"{self.collection_prefix}timeframe", timeframe_id
        )
        spreadsheet_id = timeframe_doc["spreadsheetId"]

        # Add event name to Google Sheets
        gs = GoogleSheetsModule()
        col = gs.find_next_available_col(spreadsheet_id, event_data["sheetTab"])
        gs.add_event(spreadsheet_id, event_data["sheetTab"], event_data["name"], col)

        # Append next available col value to event data
        event_data["spreadsheetCol"] = col

        # Insert the event in event collection
        event_id = self.mongo_module.insert_document(
            f"{self.collection_prefix}event", event_data
        )

        event_data["eventId"] = str(event_id)

        # Insert child event in timeframe collection
        self.mongo_module.update_document(
            f"{self.collection_prefix}timeframe",
            timeframe_id,
            {"$push": {"events": event_data}},
        )

        return json.dumps(event_data, cls=self.BSONEncoder)

    def get_event(self, event_id: str):
        event = self.mongo_module.get_document_by_id(
            f"{self.collection_prefix}event", event_id
        )

        return json.dumps(event, cls=self.BSONEncoder)

    def checkin(self, event_id: str, user: dict) -> dict:
        """Checks in a user to an event.

        Arguments:
            event_id {str} -- ID of the event to check into.
            user {dict} -- Dictionary containing user ID and name.

        Returns:
            dict -- Dictionary containing status and message.
        """
        user_id, user_email = user["id"], user["email"]
        member = self.mongo_module.get_document_by_id(f"users", user_id)
        if member is None:
            raise NotFoundError(f"User with ID {user_id} does not exist.")

        user_name = member["name"]

        event = self.mongo_module.get_document_by_id(
            f"{self.collection_prefix}event", event_id
        )

        if any(d["userId"] == user_id for d in event["usersAttended"]):
            raise BadRequestError(f"{user_name} has already checked in.")

        checkin_data = {
            "userId": user_id,
            "name": user_name,
            "dateCheckedIn": datetime.datetime.now(),
        }

        # Get timeframe document to get Google Sheets info
        timeframe = self.mongo_module.get_document_by_id(
            f"{self.collection_prefix}timeframe", event["timeframeId"]
        )

        # Get Google Sheets information
        ss_id = timeframe["spreadsheetId"]

        # Initialize Google Sheets Module
        gs = GoogleSheetsModule()

        # Find row in Google Sheets that matches user's email
        row_num = gs.find_matching_email(
            spreadsheet_id=ss_id,
            sheet_name=event["sheetTab"],
            col="C",
            email_to_match=user_email,
        )

        if row_num == -1:
            return {
                "status": False,
                "message": f"{user_name} was not found in the sheet.",
            }

        # Update Google Sheets cell with a "1" if user has checked in
        gs.update_row(
            spreadsheet_id=ss_id,
            sheet_name=event["sheetTab"],
            col=event["spreadsheetCol"],
            row=row_num + 1,
            data=[["1"]],
        )

        # Update event collection with checkin data
        self.mongo_module.update_document(
            f"{self.collection_prefix}event",
            event_id,
            {"$push": {"usersAttended": checkin_data}},
        )

        # Send email to user that has checked in
        email_content = f"""
            Hi {user_name},<br><br>

            Thank you for checking in to <b>{event["name"]}</b>! This is a confirmation that you have checked in.<br><br>

            Regards,<br>
            PCT Tech Team<br><br>

            ** Please note: Do not reply to this email. This email is sent from an unattended mailbox. Replies will not be read.
        """

        ses_destination = SesDestination(tos=[user_email])
        ses.send_email(
            source="checkin-bot@why-phi.com",
            destination=ses_destination,
            subject=f"Check-in Confirmation: {event['name']}",
            text=email_content,
            html=email_content,
        )

        return {
            "status": True,
            "message": f"{user_name} has successfully been checked in.",
        }

    def delete(self, event_id: str):
        # Check if event exists and if it doesn't return errors
        event = self.mongo_module.get_document_by_id(
            f"{self.collection_prefix}event", event_id
        )

        if event is None:
            raise NotFoundError(f"Event with ID {event_id} does not exist.")

        # If event exists, get the timeframeId (parent)
        timeframe_id = event["timeframeId"]

        # Remove event from timeframe
        self.mongo_module.update_document(
            f"{self.collection_prefix}timeframe",
            timeframe_id,
            {"$pull": {"events": {"_id": ObjectId(event_id)}}},
        )

        # Delete the event document
        self.mongo_module.delete_document_by_id(f"{self.collection_prefix}event", event_id)

    def get_timeframe_sheets(self, timeframe_id: str):
        timeframe = self.mongo_module.get_document_by_id(
            f"{self.collection_prefix}timeframe", timeframe_id
        )

        if "spreadsheetId" not in timeframe or timeframe["spreadsheetId"] == "":
            return []

        gs = GoogleSheetsModule()
        sheets = gs.get_sheets(timeframe["spreadsheetId"], include_properties=False)
        return [sheet["title"] for sheet in sheets]

    def get_rush_categories_and_events(self):
        rush_categories = self.mongo_module.get_all_data_from_collection(
            f"{self.collection_prefix}rush"
        )

        return json.dumps(rush_categories, cls=self.BSONEncoder)

    def create_rush_category(self, data: dict):
        data["dateCreated"] = datetime.datetime.now()
        data["events"] = []
        self.mongo_module.insert_document(f"{self.collection_prefix}rush", data)
        return

    def create_rush_event(self, data: dict):
        event_id = ObjectId()
        data["dateCreated"] = datetime.datetime.now()
        data["lastModified"] = data["dateCreated"]
        data["_id"] = event_id

        # upload eventCoverImage to s3 bucket (convert everything to png files for now... can adjust later)
        image_path = f"image/rush/{data['categoryId']}/{event_id}.png"
        image_url = s3.upload_binary_data(image_path, data["eventCoverImage"])

        # add image_url to data object (this also replaces the original base64 image url)
        data["eventCoverImage"] = image_url

        # initialize attendee info (for rush-event)
        data["attendees"] = []
        data["numAttendees"] = 0

        data_copy = data.copy()
        # Remove catgoryId, attendees, and numAttendees from rush category (shouldn't be persisted)
        data_copy.pop("categoryId", None)
        data_copy.pop("attendees", None)
        data_copy.pop("numAttendees", None)

        # Add event to its own collection
        self.mongo_module.insert_document(
            f"{self.collection_prefix}rush-event", data
        )

        # Add event to rush category
        self.mongo_module.update_document(
            f"{self.collection_prefix}rush",
            data["categoryId"],
            {"$push": {"events": data_copy}},
        )

        return

    def modify_rush_event(self, data: dict):

        try:
            event_id = data["_id"]
            object_event_id = ObjectId(event_id)

            data["lastModified"] = datetime.datetime.now()
            data["_id"] = object_event_id

            # Check if event exists in the rush-event collection
            event = self.mongo_module.get_document_by_id(
                f"{self.collection_prefix}rush-event", event_id
            )

            if not event:
                raise Exception("Event does not exist.")

            event_category_id = event["categoryId"]

            # if eventCoverImage contains https://whyphi-zap.s3.amazonaws.com, no need to update anything, otherwise update s3
            if "https://whyphi-zap.s3.amazonaws.com" not in data["eventCoverImage"]:
                
                # get image path
                image_path = f"image/rush/{event_category_id}/{event_id}.png"
                
                # remove previous eventCoverImage from s3 bucket
                s3.delete_binary_data(object_id=image_path)
                
                # upload eventCoverImage to s3 bucket
                image_url = s3.upload_binary_data(path=image_path, data=data["eventCoverImage"])

                # add image_url to data object (this also replaces the original base64 image url)
                data["eventCoverImage"] = image_url


            # Merge the existing event data with the new data
            updated_event = {**event, **data}

            # Remove catgoryId, attendees, and numAttendees from rush category (shouldn't be persisted)
            updated_event.pop("categoryId", None)
            updated_event.pop("attendees", None)
            updated_event.pop("numAttendees", None)

            # Define array update query and filters
            update_query = {
                "$set": {
                    "events.$[eventElem]": updated_event
                }
            }

            array_filters = [
                {"eventElem._id": object_event_id}
            ]

            # Modify the event in its category (rush collection)
            update_category_result = self.mongo_module.update_document(
                collection=f"{self.collection_prefix}rush",
                document_id=event_category_id,
                query=update_query,
                array_filters=array_filters
            )
            
            if not update_category_result:
                raise Exception("Error updating rush-event-category.")

            # cannot include _id on original document (immutable)
            data.pop("_id")
            
            # Modify actual event document (rush-event collection)
            updated_event_result = self.mongo_module.update_document(
                f"{self.collection_prefix}rush-event",
                event_id,
                {"$set": data},
            )

            if not updated_event_result:
                raise Exception("Error updating rush-event-category.")
                
            return

        
        except Exception as e:
            print("error is ", e)
            raise BadRequestError(e)

    def modify_rush_settings(self, data: dict):
        """
        Updates defaultRushCategory from the rush collection

        Parameters
        ----------
        data: dict
            contains default_rush_category_id ID of the rush category to be default

        Raises
        ------
        BadRequestError
            If default_rush_category_id is not in the rush collection
        """
        default_rush_category_id = data["defaultRushCategoryId"]
        
        collection = f"{self.collection_prefix}rush"

        # Set all defaultRushCategory fields to false
        self.mongo_module.update_many_documents(
            collection,
            {},
            {"$set": {"defaultRushCategory": False}}
        )

        # if default_rush_category_id is "" --> reset defaultRushCategory
        if not default_rush_category_id:
            return

        # Update the specified document to set its defaultRushCategory to true
        result = self.mongo_module.update_document_by_id(
            collection,
            default_rush_category_id,
            {"defaultRushCategory": True}
        )

        if not result:
            raise ValueError(f"Document with ID {default_rush_category_id} was not found or could not be updated.")

        return

    def get_rush_event(self, event_id: str, hide_attendees: bool = True):
        event = self.mongo_module.get_document_by_id(
            f"{self.collection_prefix}rush-event", event_id
        )

        if hide_attendees:
            event.pop("attendees", None)
            event.pop("numAttendees", None)

        event.pop("code")

        return json.dumps(event, cls=self.BSONEncoder)

    def checkin_rush(self, event_id: str, user_data: dict):
        event = self.mongo_module.get_document_by_id(
            f"{self.collection_prefix}rush-event", event_id
        )

        code = user_data["code"]
        user_data.pop("code")

        if code != event["code"]:
            raise UnauthorizedError("Invalid code.")

        if any(d["email"] == user_data["email"] for d in event["attendees"]):
            raise BadRequestError("User has already checked in.")

        user_data["checkinTime"] = datetime.datetime.now()
        event["attendees"].append(user_data)
        event["numAttendees"] += 1

        self.mongo_module.update_document(
            f"{self.collection_prefix}rush-event",
            event_id,
            {"$set": event},
        )

        return

    def delete_rush_event(self, event_id: str):
        """
        Deletes an rush event from the rush-event collection

        Parameters
        ----------
        event_id : str
            ID of the event to be deleted

        Raises
        ------
        BadRequestError
            If the event does not exist in the rush-event collection
        """
        try:
            # Get event_id as ObjectId
            object_event_id = ObjectId(event_id)
            
            # Check if event exists in the rush-event collection
            event = self.mongo_module.get_document_by_id(
                f"{self.collection_prefix}rush-event", object_event_id
            )
            
            if not event:
                raise Exception("Event does not exist.")

            event_category_id = event["categoryId"]

            # Get eventCoverImage path
            image_path = f"image/rush/{event_category_id}/{event_id}.png"
            
            # remove previous eventCoverImage from s3 bucket
            s3.delete_binary_data(object_id=image_path)
            
            # upload eventCoverImage to s3 bucket
            s3.delete_binary_data(object_id=image_path)

            # Delete the event from its category
            self.mongo_module.update_document(
                f"{self.collection_prefix}rush",
                event_category_id,
                {"$pull": {"events": {"_id": object_event_id}}},
            )

            # Delete event data from the rush-event collection
            self.mongo_module.delete_document_by_id(
                f"{self.collection_prefix}rush-event", object_event_id
            )
            return

        except Exception as e:
            raise BadRequestError(e)


event_service = EventService()
