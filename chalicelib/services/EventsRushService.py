from chalicelib.modules.mongo import mongo_module
from chalice import BadRequestError, UnauthorizedError
import json
from bson import ObjectId
import datetime
from chalicelib.s3 import s3

class EventsRushService:
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
        attendees_id = ObjectId()
        attendees = {
            "_id": attendees_id,
            "eventId": event_id,
            "attendees": [],
            "numAttendees": 0
        }
        self.mongo_module.insert_document(
            collection=f"{self.collection_prefix}rush-event-attendees",
            data=attendees
        )
        data["attendeesId"] = attendees_id

        # Add event to its own collection
        self.mongo_module.insert_document(
            f"{self.collection_prefix}rush-event", data
        )

        # Add event to rush category
        self.mongo_module.update_document(
            f"{self.collection_prefix}rush",
            data["categoryId"],
            {"$push": { "events": data }},
        )

        return

    def modify_rush_event(self, data: dict):

        try:
            event_id = data["_id"]
            event_oid = ObjectId(event_id)

            data["lastModified"] = datetime.datetime.now()
            data["_id"] = event_oid

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

            # Merge data with event (from client + mongo) --> NOTE: event must be unpacked first so 
            # that data overrides the matching keys
            data = { **event, **data }

            # Define array update query and filters
            update_query = {
                "$set": {
                    "events.$[eventElem]": data
                }
            }

            array_filters = [
                {"eventElem._id": event_oid}
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
            event.pop("attendeesId", None)

        event.pop("code")

        return json.dumps(event, cls=self.BSONEncoder)

    def checkin_rush(self, event_id: str, user_data: dict):
        event = self.mongo_module.get_document_by_id(
            f"{self.collection_prefix}rush-event", event_id
        )
        
        attendees_oid = event["attendeesId"]
        
        attendees = self.mongo_module.get_document_by_id(
            f"{self.collection_prefix}rush-event-attendees", attendees_oid
        )

        code = user_data["code"]
        user_data.pop("code")

        if code != event["code"]:
            raise UnauthorizedError("Invalid code.")

        if any(d["email"] == user_data["email"] for d in attendees["attendees"]):
            raise BadRequestError("User has already checked in.")

        user_data["checkinTime"] = datetime.datetime.now()
        attendees["attendees"].append(user_data)
        attendees["numAttendees"] += 1

        # Update attendees collection with data
        self.mongo_module.update_document(
            collection=f"{self.collection_prefix}rush-event-attendees",
            document_id=attendees_oid,
            query={"$set": attendees},
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
            event_oid = ObjectId(event_id)
            
            # Check if event exists in the rush-event collection
            event = self.mongo_module.get_document_by_id(
                f"{self.collection_prefix}rush-event", event_oid
            )
            
            if not event:
                raise Exception("Event does not exist.")

            attendees_oid = event["attendeesId"]
            event_category_id = event["categoryId"]

            # Get eventCoverImage path
            image_path = f"image/rush/{event_category_id}/{event_id}.png"
            
            # remove previous eventCoverImage from s3 bucket
            s3.delete_binary_data(object_id=image_path)
            
            # upload eventCoverImage to s3 bucket
            s3.delete_binary_data(object_id=image_path)

            # Delete the event from its category
            self.mongo_module.update_document(
                collection=f"{self.collection_prefix}rush",
                document_id=event_category_id,
                query={"$pull": {"events": {"_id": event_oid}}},
            )

            # Delete event data from the rush-event collection
            self.mongo_module.delete_document_by_id(
                collection=f"{self.collection_prefix}rush-event", 
                document_id=event_oid
            )
            
            # Delete attendees data from rush-event-attendees collection
            self.mongo_module.delete_document_by_id(
                collection=f"{self.collection_prefix}rush-event-attendees", 
                document_id=attendees_oid
            )
            
            return

        except Exception as e:
            raise BadRequestError(e)

events_rush_service = EventsRushService()