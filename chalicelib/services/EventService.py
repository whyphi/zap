from chalicelib.modules.mongo import mongo_module

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


event_service = EventService()
