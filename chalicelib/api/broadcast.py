from chalice import Blueprint
from chalicelib.modules.ses import ses, SesDestination
from chalicelib.modules.mongo import MongoModule
from chalicelib.services.BroadcastService import broadcast_service
import boto3

broadcast_api = Blueprint(__name__)

ses_client = boto3.client("ses")

@broadcast_api.route("/broadcast-test", methods=["GET", "POST"], cors=True)
def test_functions():
    html = broadcast_service.generate_newsletter_content()
    return {
        "status": "ok",
        "html": html
    }

# why is GET needed?
@broadcast_api.route("/broadcast", methods=["GET", "POST"], cors=True)
def send_announcement():
    MongoServer = MongoModule()
    MongoServer.connect()
    users_data = MongoServer.get_all_data()

    emails = [user["email"] for user in users_data]

    request = broadcast_api.current_request
    request_body = request.json_body

    for email in emails:
        ses_destination = SesDestination(tos=[email])
        ses.send_email(
            source="techteampct@gmail.com",
            destination=ses_destination,
            subject=request_body["subject"],
            text=request_body["content"],
            html=request_body["content"],
        )

    return


@broadcast_api.route("/test-email", methods=["GET", "POST"], cors=True)
def test_email():
    # PLEASE REPLACE WITH YOUR OWN EMAIL FOR TESTING
    html = broadcast_service.generate_newsletter_content()
    emails = ["vinli@bu.edu", "mhyan@bu.edu"]
    
    for email in emails:
        broadcast_service.send_newsletter(
            subject="Test Email",
            content=html["html"],
            recipients=[email],
        )
    return f"Sent emails to {len(emails)} people: {emails}"


