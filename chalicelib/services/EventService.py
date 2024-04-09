from chalicelib.modules.mongo import mongo_module
from chalice import NotFoundError, BadRequestError
import json
from bson import ObjectId
import datetime
from chalicelib.modules.google_sheets import GoogleSheetsModule


class EventService:
    class BSONEncoder(json.JSONEncoder):
        """JSON encoder that converts Mongo ObjectIds and datetime.datetime to strings."""

        def default(self, o):
            if isinstance(o, datetime.datetime):
                return o.isoformat()
            elif isinstance(o, ObjectId):
                return str(o)
            return super().default(o)

    def __init__(self):
        self.collection_prefix = "events-"

    def create_timeframe(self, timeframe_data: dict):
        timeframe_data["dateCreated"] = datetime.datetime.now()
        mongo_module.insert_document(
            f"{self.collection_prefix}timeframe", timeframe_data
        )

    def get_timeframe(self, timeframe_id: str):
        timeframe = mongo_module.get_document_by_id(
            f"{self.collection_prefix}timeframe", timeframe_id
        )

        return json.dumps(timeframe, cls=self.BSONEncoder)

    def get_all_timeframes(self):
        """Retrieve all timeframes from the database."""
        timeframes = mongo_module.get_all_data_from_collection(
            f"{self.collection_prefix}timeframe"
        )

        return json.dumps(timeframes, cls=self.BSONEncoder)

    def delete_timeframe(self, timeframe_id: str):
        # Check if timeframe exists and if it doesn't return errors
        timeframe = mongo_module.get_document_by_id(
            f"{self.collection_prefix}timeframe", timeframe_id
        )

        if timeframe is None:
            raise NotFoundError(f"Timeframe with ID {timeframe_id} does not exist.")

        # If timeframe exists, get the eventIds (children)
        event_ids = [str(event["_id"]) for event in timeframe["events"]]

        # Delete all the events in the timeframe
        for event_id in event_ids:
            mongo_module.delete_document_by_id(
                f"{self.collection_prefix}event", event_id
            )

        # If timeframe exists, delete the timeframe document
        mongo_module.delete_document_by_id(
            f"{self.collection_prefix}timeframe", timeframe_id
        )

    def create_event(self, timeframe_id: str, event_data: dict):
        event_data["dateCreated"] = datetime.datetime.now()
        event_data["timeframeId"] = timeframe_id
        event_data["usersAttended"] = []

        event_id = mongo_module.insert_document(
            f"{self.collection_prefix}event", event_data
        )

        event_data["eventId"] = str(event_id)

        mongo_module.update_document(
            f"{self.collection_prefix}timeframe",
            timeframe_id,
            {"$push": {"events": event_data}},
        )

    def get_event(self, event_id: str):
        event = mongo_module.get_document_by_id(
            f"{self.collection_prefix}event", event_id
        )

        return json.dumps(event, cls=self.BSONEncoder)

    def checkin(self, event_id: str, data: dict):
        # Check if user exists
        user_id = data["userId"]
        member = mongo_module.get_document_by_id(f"users", user_id)
        if member is None:
            raise NotFoundError(f"User with ID {user_id} does not exist.")

        user_name = member["name"]

        # Check if user has already checked in
        event = mongo_module.get_document_by_id(
            f"{self.collection_prefix}event", event_id
        )

        if any(d["userId"] == user_id for d in event["usersAttended"]):
            raise BadRequestError(f"{user_name} has already checked in.")

        data["name"] = user_name
        data["dateCheckedIn"] = datetime.datetime.now()

        # Update the event document
        mongo_module.update_document(
            f"{self.collection_prefix}event",
            event_id,
            {"$push": {"usersAttended": data}},
        )

        # Update the Google Sheets document as user attended
        gs = GoogleSheetsModule()
        ss_id = event["spreadsheetId"]
        sheet_title = data["sheetTitle"]
        first_name, last_name = data["firstName"], data["lastName"]
        matching_row_num = gs.find_matching_row(
            spreadsheet_id=ss_id,
            sheet_name=sheet_title,
            cols=["A", "B"],
            val_to_match=[first_name, last_name],
        )

        if matching_row_num == -1:
            return {
                "status": False,
                "message": f"{first_name} {last_name} was not found in the sheet.",
            }

        # Update the matching row to meet Google Sheets standards
        matching_row_num += 1

        gs.update_row(
            spreadsheet_id=ss_id,
            sheet_name=sheet_title,
            col="F",
            row=matching_row_num,
            data=[["1"]],
        )

        # Return success message with the user's name
        return {
            "status": True,
            "message": f"{user_name} has successfully been checked in.",
        }

    def delete(self, event_id: str):
        # Check if event exists and if it doesn't return errors
        event = mongo_module.get_document_by_id(
            f"{self.collection_prefix}event", event_id
        )

        if event is None:
            raise NotFoundError(f"Event with ID {event_id} does not exist.")

        # If event exists, get the timeframeId (parent)
        timeframe_id = event["timeframeId"]

        # Remove event from timeframe
        mongo_module.update_document(
            f"{self.collection_prefix}timeframe",
            timeframe_id,
            {"$pull": {"events": {"_id": ObjectId(event_id)}}},
        )

        # Delete the event document
        mongo_module.delete_document_by_id(f"{self.collection_prefix}event", event_id)

    def get_timeframe_sheets(self, timeframe_id: str):
        timeframe = mongo_module.get_document_by_id(
            f"{self.collection_prefix}timeframe", timeframe_id
        )

        if "spreadsheetId" not in timeframe or timeframe["spreadsheetId"] == "":
            return []

        gs = GoogleSheetsModule()
        sheets = gs.get_sheets(timeframe["spreadsheetId"], include_properties=False)
        return [sheet["title"] for sheet in sheets]


event_service = EventService()
