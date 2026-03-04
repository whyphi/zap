"""Rush event threshold evaluation helpers."""

# TODO: eventually this should be configurable in by admins for each rush-timeframe (to prevent "false-negative" thresholds)
MANDATORY_EVENT_NAMES = ["Info Session 1", "Info Session 2"]
REMAINING_EVENT_NAMES = ["Professional Panel", "Resume Night", "Social Event"]
MINIMUM_REQUIRED_REMAINING_EVENTS = 2

# Backward-compatible aliases.
mandatory_events = MANDATORY_EVENT_NAMES
remaining_events = REMAINING_EVENT_NAMES
minimum_remaining_events = MINIMUM_REQUIRED_REMAINING_EVENTS


def _get_attended_event_names(events_attended: list[dict], events: dict) -> list[str]:
    """Return names for events marked as attended."""
    return [
        events[attendance["id"]]["name"]
        for attendance in events_attended
        if attendance.get("attended")
    ]


def _has_attended_mandatory_event(attended_names: list[str]) -> bool:
    """Return True if at least one attended event is mandatory."""
    return any(name in MANDATORY_EVENT_NAMES for name in attended_names)


def _count_attended_remaining_events(attended_names: list[str]) -> int:
    """Count attended events that satisfy the remaining-events requirement."""
    return sum(1 for name in attended_names if name in REMAINING_EVENT_NAMES)


def is_rush_threshold_met(events_attended: list[dict], events: dict) -> bool:
    """
    Determine if rushee has attended enough events to apply.

    Args:
        events_attended (list[dict]): list of dicts with 'id' and 'attended' keys
        events (dict): dict of event_id -> event object

    Returns:
        bool: True if attended at least 1 mandatory and 2 remaining events
    """
    attended_event_names = _get_attended_event_names(
        events_attended=events_attended, events=events
    )
    has_required_mandatory_event = _has_attended_mandatory_event(
        attended_names=attended_event_names
    )
    remaining_events_attended_count = _count_attended_remaining_events(
        attended_names=attended_event_names
    )
    return (
        has_required_mandatory_event
        and remaining_events_attended_count >= MINIMUM_REQUIRED_REMAINING_EVENTS
    )
