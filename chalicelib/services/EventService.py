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





event_service = EventService()

