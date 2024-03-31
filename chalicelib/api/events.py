from chalice import Blueprint
from chalicelib.decorators import auth
from chalicelib.services.EventService import event_service

events_api = Blueprint(__name__)


@events_api.route("/timeframes", methods=["POST"], cors=True)
@auth(events_api, roles=["admin"])
def create_timeframe():
    data = events_api.current_request.json_body
    return event_service.create_timeframe(data["name"])


@events_api.route("/timeframes", methods=["GET"], cors=True)
@auth(events_api, roles=["admin"])
def get_all_timeframes():
    return event_service.get_all_timeframes()


@events_api.route("/timeframes/{timeframe_id}/events", methods=["POST"], cors=True)
@auth(events_api, roles=["admin"])
def create_event(timeframe_id: str):
    data = events_api.current_request.json_body
    return event_service.create_event(timeframe_id, data)


@events_api.route("/events/{event_id}", methods=["GET"], cors=True)
@auth(events_api, roles=["admin"])
def get_event(event_id: str):
    return event_service.get_event(event_id)


@events_api.route("/events/{event_id}/checkin", methods=["POST"], cors=True)
@auth(events_api, roles=["admin"])
def checkin(event_id: str):
    data = events_api.current_request.json_body
    return event_service.checkin(event_id, data)


@events_api.route("/events/{event_id}", methods=["PATCH"], cors=True)
@auth(events_api, roles=["admin"])
def update_event(event_id: str):
    pass


@events_api.route("/events/{event_id}", methods=["DELETE"], cors=True)
@auth(events_api, roles=["admin"])
def delete(event_id: str):
    return event_service.delete(event_id)
