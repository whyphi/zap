from chalice import Chalice

from chalicelib.api.listings import listings_api
from chalicelib.api.applicants import applicants_api
from chalicelib.api.announcements import announcements_api
from chalicelib.api.insights import insights_api
from chalicelib.api.members import members_api
from chalicelib.api.events import events_api
from chalicelib.api.accountability import accountability_api
from chalicelib.api.monitoring import monitoring_api
from chalicelib.api.interviews import interviews_api

app = Chalice(app_name="zap")
app.register_blueprint(announcements_api)
app.register_blueprint(listings_api)
app.register_blueprint(applicants_api)
app.register_blueprint(insights_api)
app.register_blueprint(members_api)
app.register_blueprint(events_api)
app.register_blueprint(accountability_api)
app.register_blueprint(monitoring_api)
app.register_blueprint(interviews_api)


@app.route("/")
def index():
    return {"hello": "world"}
