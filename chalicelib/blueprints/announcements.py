from chalice import Blueprint
from chalicelib.services.ses import SesMailSender, SesDestination
import boto3

announcements_routes = Blueprint(__name__)

client = boto3.client('ses')

@announcements_routes.route("/announcement")
def send_announcement():
    pass

@announcements_routes.route("/test-email")
def test_email():
    ses_destination = SesDestination(
        tos=["techteampct@gmail.com"]
    )
    ses = SesMailSender(client)
    ses.send_email(
        source="techteampct@gmail.com",
        destination=ses_destination,
        subject="Subject Test",
        text="test data",
        html="<h1>test</h1>"
    )
    return 'success'