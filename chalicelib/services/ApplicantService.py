from chalicelib.services.EventsRushService import EventsRushService
from chalicelib.utils.utils import hash_value
from chalicelib.repositories.repository_factory import RepositoryFactory
from chalicelib.repositories.base_repository import BaseRepository
from chalicelib.services.service_utils import resolve_repo
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ApplicantService:
    def __init__(
        self,
        applications_repo: Optional[BaseRepository] = None,
        listings_repo: Optional[BaseRepository] = None,
        event_timeframes_rush_repo: Optional[BaseRepository] = None,
        events_rush_service: Optional[EventsRushService] = None,
    ):
        self.applications_repo = resolve_repo(
            applications_repo, RepositoryFactory.applications
        )
        self.listings_repo = resolve_repo(listings_repo, RepositoryFactory.listings)
        self.event_timeframes_rush_repo = resolve_repo(
            event_timeframes_rush_repo, RepositoryFactory.event_timeframes_rush
        )
        self.events_rush_service = events_rush_service

    def get(self, id: str):
        return self.applications_repo.get_by_id(id_value=id)

    def get_all(self):
        return self.applications_repo.get_all()

    def get_all_from_listing(self, id: str):
        listing = self.listings_repo.get_by_id(id_value=id)
        listing_id = listing["id"]
        applications = self.applications_repo.get_all_by_field(
            field="listing_id", value=id
        )
        logger.debug(
            "Fetched applications for listing",
            extra={
                "listing_id": listing_id,
                "applications_count": len(applications),
            },
        )
        self._attach_rush_metadata(applications=applications, listing_id=listing_id)
        is_encrypted = listing.get("is_encrypted", False)
        if is_encrypted:
            logger.info(
                "Hashing encrypted listing applications",
                extra={
                    "listing_id": listing_id,
                    "applications_count": len(applications),
                },
            )
            return hash_value(applications)
        logger.debug(
            "Returning plain applications for listing",
            extra={
                "listing_id": listing_id,
                "applications_count": len(applications),
            },
        )
        return applications

    def _attach_rush_metadata(self, applications: list[dict], listing_id: str):
        # Collect rush information (events-attended)
        rush_category_data = self.event_timeframes_rush_repo.get_with_custom_select(
            filters={"listing_id": listing_id}
        )
        if not rush_category_data:
            logger.debug(
                "No rush timeframe found for listing",
                extra={"listing_id": listing_id},
            )
            return

        rush_category_id = rush_category_data[0]["id"]
        logger.debug(
            "Fetched rush timeframe for listing",
            extra={"listing_id": listing_id, "rush_timeframe_id": rush_category_id},
        )
        analytics = self._get_rush_analytics(rush_category_id)
        self._merge_rush_analytics_into_applications(
            applications=applications,
            analytics=analytics,
            listing_id=listing_id,
        )

    def _merge_rush_analytics_into_applications(
        self, applications: list[dict], analytics: dict, listing_id: str
    ):
        rushees = analytics.get("rushees", {})
        events = analytics.get("events", {})
        matched_rushees = 0

        for applicant in applications:
            rushee = rushees.get(applicant["email"])
            if not rushee:
                continue

            matched_rushees += 1
            events_attended = rushee["events_attended"]
            applicant["threshold"] = rushee["threshold"]
            applicant["events"] = self._get_applicant_events(
                events_attended=events_attended, events=events
            )
        logger.debug(
            "Merged rush metadata into applications",
            extra={
                "listing_id": listing_id,
                "applications_count": len(applications),
                "matched_rushees_count": matched_rushees,
                "events_catalog_count": len(events),
            },
        )

    def _get_rush_analytics(self, rush_category_id: str) -> dict:
        """Helper method for `get_all_from_listing`"""
        assert (
            self.events_rush_service is not None
        ), "EventsRushService must be initialized"
        try:
            analytics = self.events_rush_service.get_rush_timeframe_analytics(
                rush_category_id
            )
        except Exception:
            logger.exception(
                "Failed to fetch rush analytics",
                extra={"rush_timeframe_id": rush_category_id},
            )
            raise

        # remap rushees dict from rush_id → email
        rushees_by_email = {
            rushee_data["email"]: rushee_data
            for rushee_data in analytics.get("rushees", {}).values()
        }

        analytics["rushees"] = rushees_by_email
        logger.debug(
            "Loaded rush analytics",
            extra={
                "rush_timeframe_id": rush_category_id,
                "rushees_count": len(rushees_by_email),
                "events_count": len(analytics.get("events", {})),
            },
        )
        return analytics

    def _get_applicant_events(self, events_attended: dict, events: dict) -> dict:
        """Helper method for `get_all_from_listing`"""
        return {
            events[event_attended["id"]]["name"]: event_attended["attended"]
            for event_attended in events_attended
        }
