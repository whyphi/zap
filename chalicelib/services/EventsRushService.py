from chalicelib.repositories.repository_factory import RepositoryFactory
from chalice.app import BadRequestError, UnauthorizedError
import json
from bson import ObjectId
import datetime
from chalicelib.s3 import s3
from chalicelib.utils import get_prev_image_version
from typing import Optional
import datetime
import uuid

##### EDIT: make sure to handle exceptions that may arise from the database operations
##### EDIT: procedure for handling exceptions is to catch and raise the exception, then handle the exception in the original API call using the @handlers.error_handler decorator

class EventsRushService:
    class BSONEncoder(json.JSONEncoder):
        """JSON encoder that converts Mongo ObjectIds and datetime.datetime to strings."""

        def default(self, o):
            if isinstance(o, datetime.datetime):
                return o.isoformat()
            elif isinstance(o, ObjectId):
                return str(o)
            return super().default(o)

    def __init__(self):
        ##### EDIT: use the correct table names (reference https://dbdiagram.io/d/WhyPhi-6817d0c31ca52373f5689e84)
        ##### EDIT: change all future invocations of incorrect table names
        self.rush_categories_repo = RepositoryFactory.rush_categories()
        self.rush_events_repo = RepositoryFactory.rush_events()

    def get_rush_categories_and_events(self):
        categories = self.rush_categories_repo.get_all()
        return json.dumps(categories)

    def create_rush_category(self, data: dict):
        data["dateCreated"] = datetime.datetime.now()
        data["events"] = []
        created = self.rush_categories_repo.create(data)
        return created[0]["id"]

    def create_rush_event(self, data: dict):
        event_id = str(uuid.uuid4())
        data["dateCreated"] = datetime.datetime.now()
        data["lastModified"] = data["dateCreated"]
        data["_id"] = event_id
        data["attendees"] = []
        data["numAttendees"] = 0

        # upload eventCoverImage to s3 bucket (convert everything to png files for now... can adjust later)
        image_path = f"image/rush/{data['categoryId']}/{event_id}/{data['eventCoverImageVersion']}.png" # MUST initialize version to v0
        image_url = s3.upload_binary_data(image_path, data["eventCoverImage"])

        # add image_url to data object (this also replaces the original base64 image url)
        data["eventCoverImage"] = image_url

        self.rush_events_repo.create(data)
        
        ##### EDIT: the api route that calls this function requires this function to return something. Make sure to include a return statement.
        ##### EDIT: prolly can just return whatever the .create() call returns / just call an empty return statement (returns a None value as far as I know)
        
        """
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
        """

    def modify_rush_event(self, data: dict):

        try:
            event_id = data["id"]

            data["lastModified"] = datetime.datetime.now()

            # get existing image and image versions
            eventCoverImage: str = data["eventCoverImage"]
            eventCoverImageVersion = data["eventCoverImageVersion"]
            prevEventCoverImageVersion = get_prev_image_version(version=eventCoverImageVersion)
            
            # Check if event exists in the rush-event collection
            event = self.rush_events_repo.get_by_id(event_id)
            if not event:
                raise Exception("Event does not exist.")

            # update eventCoverImageVersion in db
            event["eventCoverImageVersion"] = eventCoverImageVersion
            
            # get categoryId (for s3 path)
            event_category_id = event["categoryId"]
            
            # obtain image paths using versioning
            image_path = f"image/rush/{event_category_id}/{event_id}/{eventCoverImageVersion}.png"
            prev_image_path = f"image/rush/{event_category_id}/{event_id}/{prevEventCoverImageVersion}.png"

            # only need to re-upload and delete old image if eventCoverImage does NOT contain https://whyphi-zap.s3.amazonaws.com
            if "https://whyphi-zap.s3.amazonaws.com" not in eventCoverImage:
                # remove previous eventCoverImage from s3 bucket
                s3.delete_binary_data(object_id=prev_image_path)
                
                # upload eventCoverImage to s3 bucket
                image_url = s3.upload_binary_data(path=image_path, data=eventCoverImage)

                # add image_url to data object (this also replaces the original base64 image url)
                data["eventCoverImage"] = image_url

            # Merge data with event (from client + mongo) --> NOTE: event must be unpacked first so 
            # that data overrides the matching keys
            merged_data = { **event, **data }
            
            """
            i remove these bc supabase dont support mongodb array filtering or ops (?)
            
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
            """
            #i fetched entire rush-categories record, located and replaced specific event inside
            #events array in py and updated whole array (idk if this even makes sense)

            # update in rush categories table w/ event list
            rush_category = self.rush_categories_repo.get_by_id(event_category_id)
            update_events = []
            for i in rush_category["events"]:
                if i["id"] == event_id or i.get("_id") == event_id:
                    update_events.append(merged_data) #replace old w/ updated
                else:
                    update_events.append(i)
            
            # save event list back into rush_categories
            self.rush_categories_repo.update(event_category_id, {"events": update_events})

            # update rush events table
            merged_data.pop("_id", None)
            self.rush_events_repo.update(event_id, merged_data)

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
        
        collection = self.rush_categories_repo.get_all()

        # Set all defaultRushCategory fields to false
        for i in collection:
            if i.get("defaultRushCategory", False):
                self.rush_categories_repo.update(
                i["id"], {"defaultRushCategory": False}
            )

        # if default_rush_category_id is "" --> reset defaultRushCategory
        if not default_rush_category_id:
            return

        # Update the specified document to set its defaultRushCategory to true
        result = self.rush_categories_repo.update(
            default_rush_category_id,
            {"defaultRushCategory": True}
        )

        if not result:
            raise ValueError(f"Document with ID {default_rush_category_id} was not found or could not be updated.")

        return

    def get_rush_event(self, event_id: str, data: dict):
        hide_attendees = data.get("hideAttendees", False) # TODO: only hideAttendees if specifically requested
        hide_code = data.get("hideCode", True)
        
        event = self.rush_events_repo.get_by_id(event_id)
        if not event:
            raise BadRequestError("Event does not exist.")

        if hide_attendees:
            event.pop("attendees", None)

        if hide_code:
            event.pop("code")

        return json.dumps(event, cls=self.BSONEncoder)

    def checkin_rush(self, event_id: str, user_data: dict):
        event_oid = ObjectId(event_id)
        
        event = self.rush_events_repo.get_by_id(event_id)
        if not event:
            raise BadRequestError("Event does not exist.")

        raw_user_code: str = user_data.get("code", "")
        user_code = raw_user_code.lower().strip()

        raw_event_code: Optional[str] = event.get("code", None)
        if raw_event_code:
            event_code = raw_event_code.lower().strip()

        user_data.pop("code")
        
        # Parse the timestamp string to a datetime object
        deadline = datetime.datetime.strptime(event["deadline"], "%Y-%m-%dT%H:%M:%S.%fZ")

        if datetime.datetime.now() > deadline:
            raise UnauthorizedError("Event deadline has passed.")

        if user_code != event_code:
            raise UnauthorizedError("Invalid code.")

        if any(d["email"] == user_data["email"] for d in event["attendees"]):
            raise BadRequestError("User has already checked in.")

        user_data["checkinTime"] = datetime.datetime.now()
        event["attendees"].append(user_data)
        event["numAttendees"] += 1

        # STEP 1: update events-rush-event collection
        self.rush_events_repo.update(event_id, event)
        
        # Define array update query and filters
        update_query = {
            "$set": {
                "events.$[eventElem]": event
            }
        }

        array_filters = [
            {"eventElem._id": event_oid}
        ]

        # STEP 2: Modify the event in its category (rush collection)
        self.rush_categories_repo.update(
            document_id=event["categoryId"],
            query=update_query,
            array_filters=array_filters
        )

        return
    
    def get_rush_events_default_category(self, data: dict):
        rush_categories = self.rush_categories_repo(
            {"defaultRushCategory": True}
        )
        
        if len(rush_categories) == 0:
            return []
        
        rush_category = rush_categories[0]
        
        # remove code from every rush event
        for event in rush_category.get("events", []):
            event.pop("code", None)
            
            # check if user attended event (boolean)
            checkedIn = any(attendee["email"] == data["email"] for attendee in event["attendees"])
            event["checkedIn"] = checkedIn
            
        # Sort events by the date field
        try:
            rush_category["events"].sort(
                key=lambda e: datetime.datetime.strptime(e["date"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                reverse=True
            )
        except ValueError as ve:
            # Handle the case where the date format might be different or invalid
            print(f"Date format error: {ve}")

        return json.dumps(rush_category, cls=self.BSONEncoder)

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
            event = self.rush_events_repo.get_by_id(event_id)
            
            if not event:
                raise Exception("Event does not exist.")

            event_category_id = event["categoryId"]
            event_cover_image_version = event["eventCoverImageVersion"]

            # Get eventCoverImage path
            image_path = f"image/rush/{event_category_id}/{event_id}/{event_cover_image_version}.png"
            
            # remove previous eventCoverImage from s3 bucket
            s3.delete_binary_data(object_id=image_path)
            
            # Delete the event from its category
            update_category = self.rush_categories_repo.update(
                event_category_id,
                {"$pull": {"events": {"_id": event_oid}}},
            )
            if not update_category:
                raise Exception("Failed to update rush category.")
            
            # Delete event data from the rush-event collection
            delete_event = self.rush_events_repo.delete_by_id(event_id)
            if not delete_event:
                raise Exception("Failed to update rush category.")
            
            return

        except Exception as e:
            raise BadRequestError(e)

    def get_rush_category_analytics(self, category_id: str):
        category = self.rush_categories_repo(category_id)
        if not category:
            raise BadRequestError("Rush category not found.")
        
        # attendees : dict of all users (user: { name, email, eventsAttended: list of objects })
        attendees = {}
        
        # events: list of objects (event: { name, eventId })
        events = []
        
        for event in category.get("events", []):
            new_event = { 
                "eventId": event["_id"], 
                "eventName": event["name"] 
            }
            
            # accumulate list of events
            events.append(new_event)
            
            # accumulate attendance
            for attendee in event.get("attendees", []):
                email = attendee["email"]
                if email in attendees:
                    attendees[email]["eventsAttended"].append(new_event)
                else:
                    attendees[email] = { **attendee, "eventsAttended": [new_event] }
                    
        result = { 
            "categoryName": category["name"], 
            "attendees": attendees,
            "events": events,
        }
        
        return json.dumps(result, cls=self.BSONEncoder)
        
events_rush_service = EventsRushService()