from chalice import Blueprint
from chalicelib.decorators import auth
from chalicelib.services.EventsRushService import events_rush_service

events_rush_api = Blueprint(__name__)


@events_rush_api.route("/events/rush", methods=["GET"], cors=True)
@auth(events_rush_api, roles=["admin"])
def get_rush_events():
    return events_rush_service.get_rush_categories_and_events()


@events_rush_api.route("/events/rush/{event_id}", methods=["GET"], cors=True)
def get_rush_event(event_id):
    return events_rush_service.get_rush_event(event_id)


@events_rush_api.route("/events/rush/category", methods=["POST"], cors=True)
@auth(events_rush_api, roles=["admin"])
def create_rush_category():
    data = events_rush_api.current_request.json_body
    return events_rush_service.create_rush_category(data)


@events_rush_api.route("/events/rush", methods=["POST"], cors=True)
@auth(events_rush_api, roles=["admin"])
def create_rush_event():
    data = events_rush_api.current_request.json_body
    return events_rush_service.create_rush_event(data)


@events_rush_api.route("/events/rush", methods=["PATCH"], cors=True)
@auth(events_rush_api, roles=["admin"])
def modify_rush_event():
    data = events_rush_api.current_request.json_body
    return events_rush_service.modify_rush_event(data)

@events_rush_api.route("/events/rush/settings", methods=["PATCH"], cors=True)
@auth(events_rush_api, roles=["admin"])
def modify_rush_settings():
    data = events_rush_api.current_request.json_body
    return events_rush_service.modify_rush_settings(data)
    

@events_rush_api.route("/events/rush/checkin/{event_id}", methods=["POST"], cors=True)
def checkin_rush(event_id):
    data = events_rush_api.current_request.json_body
    return events_rush_service.checkin_rush(event_id, data)


@events_rush_api.route("/events/rush/default", methods=["POST"], cors=True)
def get_rush_events_default_category():
    data = events_rush_api.current_request.json_body
    return events_rush_service.get_rush_events_default_category(data)


@events_rush_api.route("/events/rush/{event_id}", methods=["DELETE"], cors=True)
def delete_rush_event(event_id):
    return events_rush_service.delete_rush_event(event_id)


@events_rush_api.route("/events/rush/{category_id}/analytics", methods=["GET"], cors=True)
@auth(events_rush_api, roles=["admin"])
def get_rush_category_analytics(category_id):
    return events_rush_service.get_rush_category_analytics(category_id=category_id)