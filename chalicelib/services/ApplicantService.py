from chalicelib.services.EventsRushService import events_rush_service
from chalice.app import BadRequestError
from chalicelib.utils import hash_value
from chalicelib.repositories.repository_factory import RepositoryFactory
import json
import logging

logger = logging.getLogger(__name__)


class ApplicantService:
    def __init__(self):
        self.listings_repo = RepositoryFactory.listings()
        self.applications_repo = RepositoryFactory.applications()

    def get(self, id: str):
        data = self.applications_repo.get_by_id(id_value=id)
        return data

    def get_all(self):
        data = self.applications_repo.get_all()
        return data

    def get_all_from_listing(self, id: str):
        listing = self.listings_repo.get_by_id(id_value=id)
        data = self.applications_repo.get_all_by_field(field="listing_id", value=id)

        # TODO: re-implement this
        # # automated rush event logic (NOTE: does not override existing rush event logic)
        # rush_category_id = listing.get("rushCategoryId", None)
        # if rush_category_id:
        #     analytics = self._get_rush_analytics(rush_category_id)
        #     attendees = analytics.get("attendees", {})
        #     events = analytics.get("events", [])

        #     for applicant in data:
        #         applicant["events"] = self._get_applicant_events(
        #             email=applicant["email"], attendees=attendees, events=events
        #         )

        is_encrypted = listing.get("is_encrypted", False)
        if is_encrypted:
            data = hash_value(data)

        return data

    def _get_rush_analytics(self, rush_category_id: str) -> dict:
        """Helper method for `get_all_from_listing`"""
        analytics = events_rush_service.get_rush_category_analytics(rush_category_id)
        try:
            return json.loads(analytics)
        except json.JSONDecodeError as e:
            raise BadRequestError(f"Error decoding JSON: {e}")

    def _get_applicant_events(self, email: str, attendees: dict, events: list) -> dict:
        """Helper method for `get_all_from_listing`"""
        return {
            event["eventName"]: any(
                event_attended["eventId"] == event["eventId"]
                for event_attended in attendees.get(email, {}).get("eventsAttended", [])
            )
            for event in events
        }


applicant_service = ApplicantService()
