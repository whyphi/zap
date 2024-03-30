from chalicelib.modules.mongo import mongo_module
from chalice import NotFoundError, BadRequestError
import json
from bson import ObjectId
import datetime


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

    def create_timeframe(self, timeframe_name: str):
        timeframe_doc = {"name": timeframe_name, "dateCreated": datetime.datetime.now()}
        mongo_module.insert_document(
            f"{self.collection_prefix}timeframe", timeframe_doc
        )

    def get_all_timeframes(self):
        """Retrieve all timeframes from the database."""
        timeframes = mongo_module.get_all_data_from_collection(
            f"{self.collection_prefix}timeframe"
        )

        return json.dumps(timeframes, cls=self.BSONEncoder)

    def create_event(self, timeframe_id: str, event_name: str):
        event_doc = {
            "name": event_name,
            "dateCreated": datetime.datetime.now(),
            "timeframeId": timeframe_id,
            "usersAttended": [],
        }

        event_id = mongo_module.insert_document(
            f"{self.collection_prefix}event", event_doc
        )

        event_doc["eventId"] = str(event_id)

        mongo_module.update_document(
            f"{self.collection_prefix}timeframe",
            timeframe_id,
            {"$push": {"events": event_doc}},
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
        mongo_module.delete_document_by_id(
            f"{self.collection_prefix}event", event_id
        )
 
event_service = EventService()
