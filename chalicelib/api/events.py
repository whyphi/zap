from chalice import Blueprint
from chalicelib.decorators import auth
from chalicelib.services.EventService import event_service

events_api = Blueprint(__name__)


@events_api.route("/timeframes", methods=["POST"], cors=True)
@auth(events_api, roles=["admin"])
def create_timeframe():
    pass


@events_api.route("/timeframes", methods=["GET"], cors=True)
@auth(events_api, roles=["admin"])
def get_all_timeframes():
    pass


@events_api.route("/timeframes/{timeframe_id}/events", methods=["POST"], cors=True)
@auth(events_api, roles=["admin"])
def create_event(timeframe_id: str):
    pass


@events_api.route(
    "/timeframes/{timeframe_id}/events/{event_id}", methods=["POST"], cors=True
)
@auth(events_api, roles=["admin"])
def get_event(timeframe_id: str, event_id: str):
    pass


@events_api.route(
    "/timeframes/{timeframe_id}/events/{event_id}", methods=["PATCH"], cors=True
)
@auth(events_api, roles=["admin"])
def update_event(timeframe_id: str, event_id: str):
    pass


@events_api.route(
    "/timeframes/{timeframe_id}/events/{event_id}", methods=["DELETE"], cors=True
)
@auth(events_api, roles=["admin"])
def delete(timeframe_id: str, event_id: str):
    pass
