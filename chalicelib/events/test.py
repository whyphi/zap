
from chalice import Blueprint, Rate
from chalice.app import CloudWatchEvent

from chalicelib.services.BroadcastService import broadcast_service
from datetime import datetime
from chalicelib.services.BroadcastService import broadcast_service
from datetime import datetime

test_events = Blueprint(__name__)


@test_events.schedule(Rate(24 * 60, unit=Rate.MINUTES))
def test_event_handler(event: CloudWatchEvent):
    return "Test event"

@test_events.schedule(Rate(3, unit=Rate.MINUTES))
def test_send_job_posting_email(event: CloudWatchEvent):
    """
    This function is triggered by a CloudWatch event every week.
    It sends job posting reminders to all subscribers.
    The event is passed to the function, but it is not used in this case.
    """
    # Call the service to send job posting reminders
    html = broadcast_service.generate_newsletter_content()
    emails = ["mhyan@bu.edu"]
    
    todays_date = datetime.now().strftime("%Y-%m-%d")
    
    for email in emails:
        broadcast_service.send_newsletter(
            subject=f"PCT Weekly Newsletter Beta Test {todays_date}",
            content=html["html"],
            recipients=[email],
        )
    return f"Sent emails to {len(emails)} people: {emails}"


@test_events.schedule(Rate(3, unit=Rate.MINUTES))
def test_send_job_posting_email(event: CloudWatchEvent):
    """
    This function is triggered by a CloudWatch event every week.
    It sends job posting reminders to all subscribers.
    The event is passed to the function, but it is not used in this case.
    """
    # Call the service to send job posting reminders
    html = broadcast_service.generate_newsletter_content()
    emails = ["mhyan@bu.edu"]
    
    todays_date = datetime.now().strftime("%Y-%m-%d")
    
    for email in emails:
        broadcast_service.send_newsletter(
            subject=f"PCT Weekly Newsletter Beta Test {todays_date}",
            content=html["html"],
            recipients=[email],
        )
    return f"Sent emails to {len(emails)} people: {emails}"