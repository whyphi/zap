import os
import boto3
import sentry_sdk
from sentry_sdk.integrations.chalice import ChaliceIntegration

from chalice.app import Chalice


# API imports
from chalicelib.api.listings import listings_api
from chalicelib.api.applicants import applicants_api
from chalicelib.api.insights import insights_api
from chalicelib.api.members import members_api
from chalicelib.api.events_member import events_member_api
from chalicelib.api.events_rush import events_rush_api
from chalicelib.api.accountability import accountability_api
from chalicelib.api.monitoring import monitoring_api
from chalicelib.repositories.repository_factory import RepositoryFactory
from chalicelib.api import (
    listings,
    applicants,
    insights,
    members,
    events_member,
    events_rush,
    accountability,
    monitoring,
)
from chalicelib.services.ListingService import ListingService
from chalicelib.services.ApplicantService import ApplicantService
from chalicelib.services.MemberService import MemberService
from chalicelib.services.EventsMemberService import EventsMemberService
from chalicelib.services.EventsRushService import EventsRushService
from chalicelib.services.InsightsService import InsightsService
from chalicelib.services.AccountabilityService import AccountabilityService
from chalicelib.events.test import test_events


app = Chalice(app_name="zap")


def initialize_app():

    ################################################################
    # Configure and initialize sentry
    ################################################################
    env = os.environ.get("ENV", "local")

    if env != "local":  # only init for staging/prod
        sentry_sdk.init(
            dsn=boto3.client("ssm").get_parameter(
                Name="/Zap/sentry/dsn", WithDecryption=True
            )["Parameter"]["Value"],
            integrations=[ChaliceIntegration()],
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            traces_sample_rate=1.0,
            # Set profiles_sample_rate to 1.0 to profile 100%
            # of sampled transactions.
            # We recommend adjusting this value in production.
            profiles_sample_rate=1.0,
            environment=env,
        )

    ################################################################
    #  Dependency injection (services injected into api)
    ################################################################

    listing_service = ListingService(
        listings_repo=RepositoryFactory.listings(),
        applications_repo=RepositoryFactory.applications(),
        event_timeframes_rush_repo=RepositoryFactory.event_timeframes_rush(),
    )

    insights_service = InsightsService(
        applications_repo=RepositoryFactory.applications()
    )

    member_service = MemberService(
        users_repo=RepositoryFactory.users(),
        user_roles_repo=RepositoryFactory.user_roles(),
        roles_repo=RepositoryFactory.roles(),
    )

    events_member_service = EventsMemberService(
        events_member_repo=RepositoryFactory.events_member(),
        event_timeframes_member_repo=RepositoryFactory.event_timeframes_member(),
        events_member_attendees_repo=RepositoryFactory.events_member_attendees(),
        event_tags_repo=RepositoryFactory.event_tags(),
        tags_repo=RepositoryFactory.tags(),
        users_repo=RepositoryFactory.users(),
    )

    events_rush_service = EventsRushService(
        event_timeframes_rush_repo=RepositoryFactory.event_timeframes_rush(),
        events_rush_repo=RepositoryFactory.events_rush(),
        events_rush_attendees_repo=RepositoryFactory.events_rush_attendees(),
        rushees_repo=RepositoryFactory.rushees(),
    )

    applicant_service = ApplicantService(
        listings_repo=RepositoryFactory.listings(),
        applications_repo=RepositoryFactory.applications(),
        event_timeframes_rush_repo=RepositoryFactory.event_timeframes_rush(),
        events_rush_service=events_rush_service,
    )

    accountability_service = AccountabilityService()

    ################################################################
    # Register routes
    ################################################################

    listings.register_routes(listing_service=listing_service)
    applicants.register_routes(applicant_service=applicant_service)
    insights.register_routes(insights_service=insights_service)
    members.register_routes(member_service=member_service)
    events_member.register_routes(events_member_service=events_member_service)
    events_rush.register_routes(events_rush_service=events_rush_service)

    ################################################################
    # Register blueprints
    ################################################################

    app.register_blueprint(listings_api)
    app.register_blueprint(insights_api)
    app.register_blueprint(members_api)
    app.register_blueprint(events_member_api)
    app.register_blueprint(events_rush_api)
    app.register_blueprint(applicants_api)
    app.register_blueprint(accountability_api)
    app.register_blueprint(monitoring_api)

    ################################################################
    # Register events
    ################################################################

    app.register_blueprint(test_events)


# IMPORTANT: Only initialize app services/routes/blueprints outside of testing scope
if os.environ.get("CHALICE_TESTING") != "1":
    initialize_app()


@app.route("/")
def index():
    return {"hello": "world"}
