import pytest

from chalicelib.utils.rush_events import is_rush_threshold_met


def test_threshold_met_with_mandatory_and_minimum_remaining_events():
    events = {
        "1": {"name": "Info Session 1"},
        "2": {"name": "Professional Panel"},
        "3": {"name": "Resume Night"},
    }
    events_attended = [
        {"id": "1", "attended": True},
        {"id": "2", "attended": True},
        {"id": "3", "attended": True},
    ]

    assert is_rush_threshold_met(events_attended=events_attended, events=events) is True


def test_threshold_not_met_without_mandatory_event():
    events = {
        "2": {"name": "Professional Panel"},
        "3": {"name": "Resume Night"},
        "4": {"name": "Social Event"},
    }
    events_attended = [
        {"id": "2", "attended": True},
        {"id": "3", "attended": True},
        {"id": "4", "attended": True},
    ]

    assert (
        is_rush_threshold_met(events_attended=events_attended, events=events) is False
    )


def test_threshold_not_met_with_insufficient_remaining_events():
    events = {
        "1": {"name": "Info Session 2"},
        "2": {"name": "Professional Panel"},
    }
    events_attended = [
        {"id": "1", "attended": True},
        {"id": "2", "attended": True},
    ]

    assert (
        is_rush_threshold_met(events_attended=events_attended, events=events) is False
    )


def test_threshold_ignores_unattended_events():
    events = {
        "1": {"name": "Info Session 1"},
        "2": {"name": "Professional Panel"},
        "3": {"name": "Resume Night"},
    }
    events_attended = [
        {"id": "1", "attended": True},
        {"id": "2", "attended": False},
        {"id": "3", "attended": True},
    ]

    assert (
        is_rush_threshold_met(events_attended=events_attended, events=events) is False
    )


def test_threshold_raises_keyerror_for_unknown_event_id():
    events = {"1": {"name": "Info Session 1"}}
    events_attended = [{"id": "unknown", "attended": True}]

    with pytest.raises(KeyError):
        is_rush_threshold_met(events_attended=events_attended, events=events)
