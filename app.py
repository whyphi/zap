import os
import boto3
import sentry_sdk
from sentry_sdk.integrations.chalice import ChaliceIntegration

from chalice import Chalice

from chalicelib.api.listings import listings_api
from chalicelib.api.applicants import applicants_api
from chalicelib.api.announcements import announcements_api
from chalicelib.api.insights import insights_api
from chalicelib.api.members import members_api
from chalicelib.api.events import events_api
from chalicelib.api.accountability import accountability_api
from chalicelib.api.monitoring import monitoring_api

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
app.register_blueprint(announcements_api)
app.register_blueprint(listings_api)
app.register_blueprint(applicants_api)
app.register_blueprint(insights_api)
app.register_blueprint(members_api)
app.register_blueprint(events_api)
app.register_blueprint(accountability_api)
app.register_blueprint(monitoring_api)


@app.route("/")
def index():
    return {"hello": "world"}
