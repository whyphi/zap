from chalice import Chalice

from chalicelib.api.listings import listings_api
from chalicelib.api.applicants import applicants_api
from chalicelib.api.announcements import announcements_api
from chalicelib.api.insights import insights_api
from chalicelib.api.members import members_api

app = Chalice(app_name="zap")
app.register_blueprint(announcements_api)
app.register_blueprint(listings_api)
app.register_blueprint(applicants_api)
app.register_blueprint(insights_api)
app.register_blueprint(members_api)


@app.route("/")
def index():
    return {"hello": "world"}