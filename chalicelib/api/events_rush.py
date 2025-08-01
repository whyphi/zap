from chalice.app import Blueprint
from chalicelib.decorators import auth
from chalicelib.handlers.error_handler import handle_exceptions
from chalicelib.services.EventsRushService import events_rush_service
from chalicelib.models.roles import Roles


events_rush_api = Blueprint(__name__)

# TODO: eventually add auth for the following endpoints (but allow rushees to hit endpoint)
# Endpoints: get_rush_event, checkin_rush, get_rush_events_default_category


@events_rush_api.route("/events/rush", methods=["GET"], cors=True)
@auth(events_rush_api, roles=[Roles.ADMIN, Roles.MEMBER])
@handle_exceptions
def get_rush_events():
    return events_rush_service.get_rush_categories_and_events()


@events_rush_api.route("/events/rush/{event_id}", methods=["GET"], cors=True)
@handle_exceptions
def get_rush_event(event_id):
    query_params = events_rush_api.current_request.query_params or {}

    # By default, hide both attendees AND code
    hide_attendees = query_params.get("hideAttendees", "true").lower() == "true"
    hide_code = query_params.get("hideCode", "true").lower() == "true"

    return events_rush_service.get_rush_event(
        event_id=event_id, hide_attendees=hide_attendees, hide_code=hide_code
    )


@events_rush_api.route("/events/rush/timeframe", methods=["POST"], cors=True)
@auth(events_rush_api, roles=[Roles.ADMIN])
@handle_exceptions
def create_rush_timeframe():
    data = events_rush_api.current_request.json_body
    return events_rush_service.create_rush_timeframe(data)


@events_rush_api.route("/events/rush", methods=["POST"], cors=True)
@auth(events_rush_api, roles=[Roles.ADMIN])
@handle_exceptions
def create_rush_event():
    data = events_rush_api.current_request.json_body
    return events_rush_service.create_rush_event(data)


@events_rush_api.route("/events/rush", methods=["PATCH"], cors=True)
@auth(events_rush_api, roles=[Roles.ADMIN])
@handle_exceptions
def modify_rush_event():
    data = events_rush_api.current_request.json_body
    return events_rush_service.modify_rush_event(data)


@events_rush_api.route("/events/rush/settings", methods=["PATCH"], cors=True)
@auth(events_rush_api, roles=[Roles.ADMIN])
@handle_exceptions
def modify_rush_settings():
    data = events_rush_api.current_request.json_body
    return events_rush_service.modify_rush_settings(data)


@events_rush_api.route("/events/rush/checkin/{event_id}", methods=["POST"], cors=True)
@handle_exceptions
def checkin_rush(event_id):
    data = events_rush_api.current_request.json_body
    return events_rush_service.checkin_rush(event_id, data)


@events_rush_api.route("/events/rush/timeframe/default", methods=["POST"], cors=True)
@handle_exceptions
def get_rush_events_default_timeframe():
    data = events_rush_api.current_request.json_body
    rushee_id = data["rushee_id"]
    return events_rush_service.get_rush_events_default_timeframe(rushee_id=rushee_id)


@events_rush_api.route("/events/rush/{event_id}", methods=["DELETE"], cors=True)
@auth(events_rush_api, roles=[Roles.ADMIN])
@handle_exceptions
def delete_rush_event(event_id):
    return events_rush_service.delete_rush_event(event_id)


@events_rush_api.route(
    "/events/rush/category/{category_id}/analytics", methods=["GET"], cors=True
)
@auth(events_rush_api, roles=[Roles.ADMIN])
@handle_exceptions
def get_rush_category_analytics(category_id):
    return events_rush_service.get_rush_category_analytics(category_id=category_id)
