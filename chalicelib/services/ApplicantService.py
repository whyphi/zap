from chalicelib.db import db
from chalicelib.services.EventsRushService import events_rush_service
from chalice import BadRequestError
import json


class ApplicantService:
    def __init__(self):
        pass

    def get(self, id: str):
        data = db.get_item(table_name="zap-applications", key={"applicantId": id})
        return data

    def get_all(self):
        data = db.get_all(table_name="zap-applications")
        return data

    def get_all_from_listing(self, id: str):
        listing = db.get_item(table_name="zap-listings", key={"listingId": id})
        data = db.get_applicants(table_name="zap-applications", listing_id=id)

        # automated rush event logic (NOTE: does not override existing rush event logic)
        rush_category_id = listing["rushCategoryId"]
        if rush_category_id:
            analytics = self._get_rush_analytics(rush_category_id)
            attendees = analytics.get("attendees", {})
            events = analytics.get("events", [])

            for applicant in data:
                applicant["events"] = self._get_applicant_events(
                    email=applicant["email"], attendees=attendees, events=events
                )

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
