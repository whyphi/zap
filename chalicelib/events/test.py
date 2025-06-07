from chalice.app import CloudWatchEvent, Blueprint, Rate


test_events = Blueprint(__name__)


@test_events.schedule(Rate(24 * 60, unit=Rate.MINUTES))
def test_event_handler(event: CloudWatchEvent):
    return "Test event"
