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

        # Get Google Spreadsheet ID from timeframe
        timeframe_doc = mongo_module.get_document_by_id(
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
        event_id = mongo_module.insert_document(
            f"{self.collection_prefix}event", event_data
        )

        event_data["eventId"] = str(event_id)

        # Insert child event in timeframe collection
        mongo_module.update_document(
            f"{self.collection_prefix}timeframe",
            timeframe_id,
            {"$push": {"events": event_data}},
        )

        return json.dumps(event_data, cls=self.BSONEncoder)

    def get_event(self, event_id: str):
        event = mongo_module.get_document_by_id(
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
        user_id = user["userId"]
        member = mongo_module.get_document_by_id(f"users", user_id)
        if member is None:
            raise NotFoundError(f"User with ID {user_id} does not exist.")

        user_name = member["name"]

        event = mongo_module.get_document_by_id(
            f"{self.collection_prefix}event", event_id
        )

        if any(d["userId"] == user_id for d in event["usersAttended"]):
            raise BadRequestError(f"{user_name} has already checked in.")

        checkin_data = {
            "userId": user_id,
            "name": user_name,
            "dateCheckedIn": datetime.datetime.now(),
        }

        # Update event collection with checkin data
        mongo_module.update_document(
            f"{self.collection_prefix}event",
            event_id,
            {"$push": {"usersAttended": checkin_data}},
        )

        # Get timeframe document to get Google Sheets info
        timeframe = mongo_module.get_document_by_id(
            f"{self.collection_prefix}timeframe", event["timeframeId"]
        )

        # Get Google Sheets information
        ss_id = timeframe["spreadsheetId"]

        # Initialize Google Sheets Module
        gs = GoogleSheetsModule()

        # Find row in Google Sheets that matches user's name
        row_num = gs.find_matching_name(
            spreadsheet_id=ss_id,
            sheet_name=event["sheetTab"],
            cols=["A", "B"],
            name_to_match=user_name,
            use_similarity=True
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