import os
import boto3
import sentry_sdk
from sentry_sdk.integrations.chalice import ChaliceIntegration

from chalice.app import Chalice


# API imports
from chalicelib.api.listings import listings_api
from chalicelib.api.applicants import applicants_api
from chalicelib.api.broadcast import broadcast_api
from chalicelib.api.insights import insights_api
from chalicelib.api.members import members_api
from chalicelib.api.events_member import events_member_api
from chalicelib.api.events_rush import events_rush_api
from chalicelib.api.accountability import accountability_api
from chalicelib.api.monitoring import monitoring_api

# Event imports
from chalicelib.events.test import test_events


# Configure and initialize sentry
sentry_sdk.init(
    dsn=boto3.client("ssm").get_parameter(Name="/Zap/sentry/dsn", WithDecryption=True)[
        "Parameter"
    ]["Value"],
    integrations=[ChaliceIntegration()],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
    environment="production" if os.environ.get("ENV") == "prod" else "development",
)

app = Chalice(app_name="zap")

# Register APIs
app.register_blueprint(broadcast_api)
app.register_blueprint(listings_api)
app.register_blueprint(applicants_api)
app.register_blueprint(insights_api)
app.register_blueprint(members_api)
app.register_blueprint(events_member_api)
app.register_blueprint(events_rush_api)
app.register_blueprint(accountability_api)
app.register_blueprint(monitoring_api)

# Register events
app.register_blueprint(test_events)


@app.route("/")
def index():
    return {"hello": "world"}
