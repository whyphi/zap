from chalice import Blueprint
from chalicelib.services.ses import SesMailSender, SesDestination
import boto3

announcements_routes = Blueprint(__name__)

client = boto3.client('ses')

@announcements_routes.route("/announcement")
def send_announcement():
    # TODO: 1. Get all email data from MongoDB (Consider creating a mongodb wrapper in services)
    
    # TODO: 2. Convert all emails to a list

    # TODO: 3. Create a new object with the list initialized into to (either send To to techteampct@gmail.com or all the users)

    # TODO: 4. Send Email using SesMailSender Class

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