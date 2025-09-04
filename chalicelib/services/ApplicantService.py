from chalicelib.services.EventsRushService import events_rush_service
from chalice.app import BadRequestError
from chalicelib.utils.utils import hash_value
from chalicelib.repositories.repository_factory import RepositoryFactory
import json
import logging

logger = logging.getLogger(__name__)


class ApplicantService:
    def __init__(self):
        self.listings_repo = RepositoryFactory.listings()
        self.applications_repo = RepositoryFactory.applications()
        self.event_timeframes_rush_repo = RepositoryFactory.event_timeframes_rush()

    def get(self, id: str):
        data = self.applications_repo.get_by_id(id_value=id)
        return data

    def get_all(self):
        data = self.applications_repo.get_all()
        return data

    def get_all_from_listing(self, id: str):
        listing = self.listings_repo.get_by_id(id_value=id)
        listing_id = listing["id"]
        applications = self.applications_repo.get_all_by_field(
            field="listing_id", value=id
        )

        # Collect rush information (events-attended)
        rush_category = self.event_timeframes_rush_repo.get_with_custom_select(
            filters={"listing_id": listing_id}
        )[0]
        rush_category_id = rush_category["id"]
        if rush_category_id:
            analytics = self._get_rush_analytics(rush_category_id)
            rushees = analytics.get("rushees", {})
            events = analytics.get("events", {})

            for applicant in applications:
                email = applicant["email"]
                rushee = rushees[email]
                events_attended = rushee["events_attended"]

                applicant["threshold"] = rushee["threshold"]
                applicant["events"] = self._get_applicant_events(
                    events_attended=events_attended, events=events
                )

        is_encrypted = listing.get("is_encrypted", False)
        if is_encrypted:
            applications = hash_value(applications)

        return applications

    def _get_rush_analytics(self, rush_category_id: str) -> dict:
        """Helper method for `get_all_from_listing`"""
        analytics = events_rush_service.get_rush_timeframe_analytics(rush_category_id)

        # remap rushees dict from rush_id → email
        rushees_by_email = {
            rushee_data["email"]: rushee_data
            for rushee_data in analytics.get("rushees", {}).values()
        }

        analytics["rushees"] = rushees_by_email
        return analytics

    def _get_applicant_events(self, events_attended: dict, events: dict) -> dict:
        """Helper method for `get_all_from_listing`"""
        return {
            events[event_attended["id"]]["name"]: event_attended["attended"]
            for event_attended in events_attended
        }


applicant_service = ApplicantService()
