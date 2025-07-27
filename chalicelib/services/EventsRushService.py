from chalicelib.repositories.repository_factory import RepositoryFactory
from chalice.app import BadRequestError, UnauthorizedError
import json
from chalicelib.s3 import s3
from chalicelib.utils import get_prev_image_version
from typing import Optional
from datetime import datetime, timezone
import uuid

##### EDIT: make sure to handle exceptions that may arise from the database operations
##### EDIT: procedure for handling exceptions is to catch and raise the exception, then handle the exception in the original API call using the @handlers.error_handler decorator


class EventsRushService:
    # class BSONEncoder(json.JSONEncoder):
    #     """JSON encoder that converts Mongo ObjectIds and datetime.datetime to strings."""

    #     def default(self, o):
    #         if isinstance(o, datetime.datetime):
    #             return o.isoformat()
    #         elif isinstance(o, ObjectId):
    #             return str(o)
    #         return super().default(o)

    def __init__(self):
        self.event_timeframes_rush_repo = RepositoryFactory.event_timeframes_rush()
        self.events_rush_repo = RepositoryFactory.events_rush()
        self.events_rush_attendees_repo = RepositoryFactory.events_rush_attendees()
        self.rushees_repo = RepositoryFactory.rushees()

    def get_rush_categories_and_events(self):
        try:
            timeframes_with_events = self.event_timeframes_rush_repo.get_all(
                select_query="*, events_rush(*)"
            )
            return timeframes_with_events
        except Exception as e:
            raise BadRequestError(f"Failed to get rush categories and events: {e}")

    def get_rush_event(
        self, event_id: str, hide_attendees: bool = False, hide_code: bool = True
    ):
        try:

            # 1. Get event
            event = self.events_rush_repo.get_by_id(id_value=event_id)

            if not event:
                raise BadRequestError("Event does not exist.")

            if hide_code:
                event.pop("code", None)

            # 2. Get rushees associated with event (if possible)
            rushees = []
            if not hide_attendees:
                attendees_with_rushees = (
                    self.events_rush_attendees_repo.get_with_custom_select(
                        filters={"event_id": event_id},
                        select_query="checkin_time, rushees(*)",
                    )
                )

                for attendee in attendees_with_rushees:
                    # Returns single rushee table row
                    rushee = attendee.get("rushees", None)

                    if not rushee:
                        raise BadRequestError("Rushee not found.")

                    rushee["checkin_time"] = attendee["checkin_time"]
                    rushees.append(rushee)

            event["attendees"] = rushees
            return event
        except Exception as e:
            raise BadRequestError(f"Failed to get rush event: {e}")

    def create_rush_timeframe(self, data: dict):
        try:
            id = str(uuid.uuid4())
            data["id"] = id
            # TODO: remove comments as needed
            # data["dateCreated"] = datetime.datetime.now()
            # data["events"] = []
            response = self.event_timeframes_rush_repo.create(data)
            return response
        except Exception as e:
            raise BadRequestError(f"Failed to get rush category: {e}")

    def create_rush_event(self, data: dict):
        try:
            event_id = str(uuid.uuid4())
            data["id"] = event_id

            # upload eventCoverImage to s3 bucket (convert everything to png files for now... can adjust later)
            image_path = f"image/rush/{data['timeframe_id']}/{event_id}/{data['event_cover_image_version']}.png"  # MUST initialize version to v0
            image_url = s3.upload_binary_data(image_path, data["event_cover_image"])

            # add image_url to data object (this also replaces the original base64 image url)
            data["event_cover_image"] = image_url

            event = self.events_rush_repo.create(data)
            return event
        except Exception as e:
            raise BadRequestError(f"Failed to create rush event: {e}")

    def modify_rush_event(self, data: dict):

        try:
            event_id = data["id"]
            data["last_modified"] = datetime.now(tz=timezone.utc).isoformat()

            # get existing image and image versions
            event_cover_image: str = data["event_cover_image"]
            event_cover_image_version = data["event_cover_image_version"]
            prev_event_cover_image_version = get_prev_image_version(
                version=event_cover_image_version
            )

            # Check if event exists in the rush-event collection
            event = self.events_rush_repo.get_by_id(event_id)
            if not event:
                raise Exception("Event does not exist.")

            # get timeframe_id from event (for s3 path)
            timeframe_id = event["timeframe_id"]

            # obtain image paths using versioning
            image_path = (
                f"image/rush/{timeframe_id}/{event_id}/{event_cover_image_version}.png"
            )
            prev_image_path = f"image/rush/{timeframe_id}/{event_id}/{prev_event_cover_image_version}.png"

            # only need to re-upload and delete old image if even_cover_image does NOT contain https://whyphi-zap.s3.amazonaws.com
            if "https://whyphi-zap.s3.amazonaws.com" not in event_cover_image:

                # upload eventCoverImage to s3 bucket
                image_url = s3.upload_binary_data(
                    path=image_path, data=event_cover_image
                )

                # remove previous eventCoverImage from s3 bucket
                s3.delete_binary_data(object_id=prev_image_path)

                # add image_url to data object (this also replaces the original base64 image url)
                data["event_cover_image"] = image_url

            response = self.events_rush_repo.update(id_value=event_id, data=data)
            return response
        except Exception as e:
            raise BadRequestError(str(e))

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
        try:
            default_rush_category_id = data.get("defaultRushCategoryId")

            collection = self.event_timeframes_rush_repo.get_all()

            # Set all defaultRushCategory fields to false
            for i in collection:
                if i.get("defaultRushCategory", False):
                    self.event_timeframes_rush_repo.update(
                        i["id"], {"defaultRushCategory": False}
                    )

            # if default_rush_category_id is "" --> reset defaultRushCategory
            if not default_rush_category_id:
                return

            # Update the specified document to set its defaultRushCategory to true
            result = self.event_timeframes_rush_repo.update(
                default_rush_category_id, {"defaultRushCategory": True}
            )

            if not result:
                raise ValueError(
                    f"Document with ID {default_rush_category_id} was not found or could not be updated."
                )

        except Exception as e:
            raise BadRequestError(f"Failed to modify rush settings: {e}")

    def checkin_rush(self, event_id: str, user_data: dict):
        try:
            event = self.events_rush_repo.get_by_id(event_id)
            if not event:
                raise BadRequestError("Event does not exist.")

            raw_user_code: str = user_data.get("code", "")
            user_code = raw_user_code.lower().strip()

            raw_event_code: Optional[str] = event.get("code", None)
            if raw_event_code:
                event_code = raw_event_code.lower().strip()

            user_data.pop("code", None)

            # Parse the timestamp string to a datetime object
            deadline = datetime.datetime.strptime(
                event["deadline"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )

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
            self.events_rush_repo.update(event_id, event)

            # update event inside rush-categories.events list manually
            rush_category = self.event_timeframes_rush_repo.get_by_id(
                event["categoryId"]
            )
            events = []
            for i in rush_category["events"]:
                if i.get("id") == event_id or i.get("_id") == event_id:
                    events.append(event)
                else:
                    events.append(i)
            self.event_timeframes_rush_repo.update(
                event["categoryId"], {"events": events}
            )

        except Exception as e:
            raise BadRequestError(f"Check-in failed: {e}")

        """
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
        """

    def get_rush_events_default_category(self, data: dict):
        try:
            rush_categories = self.event_timeframes_rush_repo(
                {"defaultRushCategory": True}
            )
            if not rush_categories:
                return []

            if len(rush_categories) == 0:
                return []

            rush_category = rush_categories[0]

            # remove code from every rush event
            for event in rush_category.get("events", []):
                event.pop("code", None)

                # check if user attended event (boolean)
                checkedIn = any(
                    attendee["email"] == data["email"]
                    for attendee in event.get("attendees", [])
                )
                event["checkedIn"] = checkedIn

            # Sort events by the date field
            try:
                rush_category["events"].sort(
                    key=lambda e: datetime.datetime.strptime(
                        e["date"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    ),
                    reverse=True,
                )
            except ValueError as ve:
                # Handle the case where the date format might be different or invalid
                print(f"Date format error: {ve}")

            return json.dumps(rush_category, cls=self.BSONEncoder)
        except Exception as e:
            raise BadRequestError(f"Failed to get rush event: {e}")

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
            # Check if event exists in the rush-event collection
            event = self.events_rush_repo.get_by_id(event_id)

            if not event:
                raise Exception("Event does not exist.")

            event_category_id = event["categoryId"]
            event_cover_image_version = event["event_cover_image_version"]

            # Get eventCoverImage path
            image_path = f"image/rush/{event_category_id}/{event_id}/{event_cover_image_version}.png"

            # remove previous eventCoverImage from s3 bucket
            s3.delete_binary_data(object_id=image_path)

            """
            # Delete the event from its category
            update_category = self.rush_categories_repo.update(
                event_category_id,
                {"$pull": {"events": {"_id": event_oid}}},
            )
            if not update_category:
                raise Exception("Failed to update rush category.")
            """

            # Remove event from rush-categories events list manually
            rush_category = self.event_timeframes_rush_repo.get_by_id(event_category_id)
            updated = [
                i
                for i in rush_category["events"]
                if i.get("_id") != event_id and i.get("id") != event_id
            ]
            self.event_timeframes_rush_repo.update(
                event_category_id, {"events": updated}
            )

            # Delete event data from the rush-event table
            delete_event = self.events_rush_repo.delete_by_id(event_id)
            if not delete_event:
                raise Exception("Failed to delete rush category.")

            return

        except Exception as e:
            raise BadRequestError(e)

    def get_rush_category_analytics(self, category_id: str):
        try:
            category = self.event_timeframes_rush_repo.get_by_id(category_id)
            if not category:
                raise BadRequestError("Rush category not found.")

            # attendees : dict of all users (user: { name, email, eventsAttended: list of objects })
            attendees = {}

            # events: list of objects (event: { name, eventId })
            events = []

            for event in category.get("events", []):
                new_event = {
                    "eventId": event.get("_id") or event.get("id"),
                    "eventName": event.get("name"),
                }

                # accumulate list of events
                events.append(new_event)

                # accumulate attendance
                for attendee in event.get("attendees", []):
                    email = attendee["email"]
                    if email in attendees:
                        attendees[email]["eventsAttended"].append(new_event)
                    else:
                        attendees[email] = {**attendee, "eventsAttended": [new_event]}

            result = {
                "categoryName": category["name"],
                "attendees": attendees,
                "events": events,
            }

            return json.dumps(result, cls=self.BSONEncoder)
        except Exception as e:
            raise BadRequestError(f"Failed to get rush category analytics: {e}")


events_rush_service = EventsRushService()
