from chalicelib.repositories.repository_factory import RepositoryFactory
from chalice.app import BadRequestError, UnauthorizedError
import json
from chalicelib.s3 import s3
from chalicelib.utils.utils import get_prev_image_version, extract_relative_path_from_url
from chalicelib.utils.rush_events import is_rush_threshold_met
from typing import Optional
from datetime import datetime, timezone
import uuid
from chalicelib.handlers.error_handler import GENERIC_CLIENT_ERROR
from postgrest.exceptions import APIError
from pytz import timezone as pytz_timezone
from chalicelib.repositories.base_repository import BaseRepository
from chalicelib.services.service_utils import resolve_repo
from typing import Optional

# TODO: refactor base_repo to pass errors to service classes


class EventsRushService:

    def __init__(
        self,
        event_timeframes_rush_repo: Optional[BaseRepository] = None,
        events_rush_repo: Optional[BaseRepository] = None,
        events_rush_attendees_repo: Optional[BaseRepository] = None,
        rushees_repo: Optional[BaseRepository] = None,
    ):
        self.event_timeframes_rush_repo = resolve_repo(event_timeframes_rush_repo, RepositoryFactory.event_timeframes_rush)
        self.events_rush_repo = resolve_repo(events_rush_repo, RepositoryFactory.events_rush)
        self.events_rush_attendees_repo = resolve_repo(events_rush_attendees_repo, RepositoryFactory.events_rush_attendees)
        self.rushees_repo = resolve_repo(rushees_repo, RepositoryFactory.rushees)

    def get_rush_categories_and_events(self):
        try:
            timeframes_with_events = self.event_timeframes_rush_repo.get_all(
                select_query="*, events_rush(*)"
            )
            return timeframes_with_events
        except Exception as e:
            raise BadRequestError(GENERIC_CLIENT_ERROR)

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
            raise BadRequestError(GENERIC_CLIENT_ERROR)

    def create_rush_timeframe(self, data: dict):
        try:
            id = str(uuid.uuid4())
            data["id"] = id
            response = self.event_timeframes_rush_repo.create(data)
            return response
        except Exception as e:
            raise BadRequestError(GENERIC_CLIENT_ERROR)

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

            # only need to re-upload and delete old image if event_cover_image is NOT a URL (S3 or LocalStack)
            is_s3_url = event_cover_image.startswith(
                "https://whyphi-zap.s3.amazonaws.com"
            )
            is_localstack_url = event_cover_image.startswith(
                "http://localhost:9000/whyphi-zap"
            )
            if not (is_s3_url or is_localstack_url):

                # upload eventCoverImage to s3 bucket
                image_url = s3.upload_binary_data(
                    relative_path=image_path, data=event_cover_image
                )

                # remove previous eventCoverImage from s3 bucket
                s3.delete_binary_data(relative_path=prev_image_path)

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
            default_rush_category_id = data.get("default_rush_timeframe_id")

            if not default_rush_category_id:
                raise BadRequestError("Missing default rush category.")

            response = self.event_timeframes_rush_repo.update_all(
                data={"default_rush_timeframe": False}
            )

            result = self.event_timeframes_rush_repo.update(
                id_value=default_rush_category_id, data={"default_rush_timeframe": True}
            )

            return result

        except Exception as e:
            raise BadRequestError(f"Failed to modify rush settings: {e}")

    def checkin_rush(self, event_id: str, user_data: dict):
        # 1. Ensure if event exists
        event = self.events_rush_repo.get_by_id(event_id)
        if not event:
            raise BadRequestError("Event does not exist.")

        # 2. Extract code and id
        raw_user_code: str = user_data.get("code", "")
        user_code = raw_user_code.lower().strip()

        raw_event_code: Optional[str] = event.get("code", None)
        if not raw_event_code:
            raise UnauthorizedError("Invalid code.")

        event_code = raw_event_code.lower().strip()

        rushee_id = user_data["rusheeId"]

        # 3. Validate time + code
        deadline = datetime.fromisoformat(event["deadline"])
        now = datetime.now(tz=timezone.utc)

        if now > deadline:
            est = pytz_timezone("US/Eastern")
            print(f"now (EST): {now.astimezone(est).strftime('%Y-%m-%d %H:%M:%S')}")
            print(
                f"deadline (EST): {deadline.astimezone(est).strftime('%Y-%m-%d %H:%M:%S')}"
            )
            raise UnauthorizedError("Event deadline has passed.")

        if user_code != event_code:
            raise UnauthorizedError("Invalid code.")

        # 4. Attempt checkin
        try:
            self.events_rush_attendees_repo.create(
                data={"event_id": event_id, "rushee_id": rushee_id}
            )
        except APIError as e:
            if e.code == "23505":
                raise BadRequestError("User has already checked in.")
            raise BadRequestError(GENERIC_CLIENT_ERROR)

        return {"msg": True}

    def get_rush_events_default_timeframe(self, rushee_id: str):
        """Gets all events for current timeframe and status for
        whether rushee has checked in.

        Args:
            rushee_id (str): UUID of requesting rushee

        Raises:
            BadRequestError: Invalid default timeframe configuration.

        Returns:
            dict: Event timeframe and events
        """
        # Gets all rush events for a given rush timeframe
        # RUSH ONLY METHOD

        default_timeframes = self.event_timeframes_rush_repo.get_all_by_field(
            field="default_rush_timeframe", value=True
        )
        if not default_timeframes:
            raise BadRequestError("No default rush timeframe found.")
        if len(default_timeframes) > 1:
            raise BadRequestError(
                "Multiple default rush timeframes found. There should only be one."
            )

        default_timeframe = default_timeframes[0]

        rush_events = self.events_rush_repo.get_with_custom_select(
            filters={"timeframe_id": default_timeframe["id"]},
            select_query="*, rushees(*)",
        )

        for re in rush_events:
            rushees = re.get("rushees", [])
            re["checked_in"] = any(r.get("id") == rushee_id for r in rushees)
            re.pop("rushees", None)

        # Sort events newest to oldest
        rush_events.sort(key=lambda e: e.get("date", ""), reverse=True)

        default_timeframe["events"] = rush_events

        return default_timeframe

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

            # Get eventCoverImage path
            # image_path = f"image/rush/{event_category_id}/{event_id}/{event_cover_image_version}.png"
            image_path = extract_relative_path_from_url(event["event_cover_image"])

            s3.delete_binary_data(relative_path=image_path)

            delete_event = self.events_rush_repo.delete(id_value=event_id)
            if not delete_event:
                raise Exception("Failed to delete rush category.")

            return

        except Exception as e:
            raise BadRequestError(e)

    def get_rush_timeframe_analytics(self, timeframe_id: str):
        try:
            timeframe = self.event_timeframes_rush_repo.get_by_id(id_value=timeframe_id)
            rush_events = self.events_rush_repo.get_with_custom_select(
                filters={"timeframe_id": timeframe_id}, select_query="*, rushees(*)"
            )
        except Exception as e:
            raise BadRequestError(GENERIC_CLIENT_ERROR)

        rush_events.sort(key=lambda e: e.get("date", ""))

        rushee_dict = {}
        rush_events_dict = {}

        # Extract all rushees and events
        for event in rush_events:
            # Get rushees
            event_id = event["id"]
            for rushee in event.get("rushees", []):
                rushee_id = rushee["id"]
                if rushee_id not in rushee_dict:
                    rushee_dict[rushee_id] = rushee.copy()

            # Get map of events (for quick lookups)
            event_copy = event.copy()
            event_copy.pop("rushees", None)
            event_copy["num_attendees"] = len(event["rushees"])

            rush_events_dict[event_id] = event_copy

        # Track rushee event attendance
        for rushee_id, rushee in rushee_dict.items():
            events_attended = []
            for event in rush_events:
                event_id = event["id"]
                event_rushees = event.get("rushees", [])

                attended = False
                if any(r.get("id") == rushee_id for r in event_rushees):
                    attended = True

                events_attended.append({"id": event_id, "attended": attended})

            rushee["events_attended"] = events_attended
            rushee["threshold"] = is_rush_threshold_met(
                events_attended=events_attended, events=rush_events_dict
            )
            rushee["num_events_attended"] = sum(
                [e["attended"] for e in events_attended]
            )

        return {
            "timeframe": timeframe,
            "rushees": rushee_dict,
            "events": rush_events_dict,
        }


events_rush_service = EventsRushService()
