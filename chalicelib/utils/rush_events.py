# TODO: eventually this should be configurable in by admins for each rush-timeframe (to prevent "false-negative" thresholds)
mandatory_events = ["Info Session 1", "Info Session 2"]
remaining_events = ["Professional Panel", "Resume Night", "Social Event"]
minimum_remaining_events = 2


def is_rush_threshold_met(events_attended: list[dict], events: dict) -> bool:
    """
    Determine if rushee has attended enough events to apply.

    Args:
        events_attended (list[dict]): list of dicts with 'id' and 'attended' keys
        events (dict): dict of event_id -> event object

    Returns:
        bool: True if attended at least 1 mandatory and 2 remaining events
    """
    # Get names of attended events
    attended_names = [
        events[ea["id"]]["name"] for ea in events_attended if ea.get("attended")
    ]

    has_attended_mandatory = any(name in mandatory_events for name in attended_names)
    attended_remaining = sum(1 for name in attended_names if name in remaining_events)
    return has_attended_mandatory and attended_remaining >= minimum_remaining_events
