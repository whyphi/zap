from chalice import Blueprint
from chalicelib.decorators import auth
from chalicelib.services.EventsMemberService import events_member_service

events_member_api = Blueprint(__name__)


@events_member_api.route("/timeframes", methods=["POST"], cors=True)
@auth(events_member_api, roles=["admin"])
def create_timeframe():
    data = events_member_api.current_request.json_body
    return events_member_service.create_timeframe(data)


@events_member_api.route("/timeframes", methods=["GET"], cors=True)
@auth(events_member_api, roles=["admin"])
def get_all_timeframes():
    return events_member_service.get_all_timeframes()


@events_member_api.route("/timeframes/{timeframe_id}", methods=["GET"], cors=True)
@auth(events_member_api, roles=["admin"])
def get_timeframe(timeframe_id: str):
    return events_member_service.get_timeframe(timeframe_id)


@events_member_api.route("/timeframes/{timeframe_id}", methods=["DELETE"], cors=True)
@auth(events_member_api, roles=["admin"])
def delete_timeframe(timeframe_id: str):
    return events_member_service.delete_timeframe(timeframe_id)


@events_member_api.route("/timeframes/{timeframe_id}/events", methods=["POST"], cors=True)
@auth(events_member_api, roles=["admin"])
def create_event(timeframe_id: str):
    data = events_member_api.current_request.json_body
    return events_member_service.create_event(timeframe_id, data)


@events_member_api.route("/events/{event_id}", methods=["GET"], cors=True)
@auth(events_member_api, roles=["admin"])
def get_event(event_id: str):
    return events_member_service.get_event(event_id)


@events_member_api.route("/timeframes/{timeframe_id}/sheets", methods=["GET"], cors=True)
@auth(events_member_api, roles=["admin"])
def get_timeframe_sheets(timeframe_id: str):
    return events_member_service.get_timeframe_sheets(timeframe_id)


@events_member_api.route("/events/{event_id}/checkin", methods=["POST"], cors=True)
@auth(events_member_api, roles=["admin"])
def checkin(event_id: str):
    data = events_member_api.current_request.json_body
    return events_member_service.checkin(event_id, data)


@events_member_api.route("/events/{event_id}", methods=["PATCH"], cors=True)
@auth(events_member_api, roles=["admin"])
def update_event(event_id: str):
    pass


@events_member_api.route("/events/{event_id}", methods=["DELETE"], cors=True)
@auth(events_member_api, roles=["admin"])
def delete_event(event_id: str):
    return events_member_service.delete(event_id)