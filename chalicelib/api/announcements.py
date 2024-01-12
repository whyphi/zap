from chalice import Blueprint
from chalicelib.modules.ses import SesMailSender, SesDestination
from chalicelib.modules.mongo import MongoService
import boto3

announcements_api = Blueprint(__name__)

ses_client = boto3.client('ses')


# why is GET needed?
@announcements_api.route("/announcement", methods=["GET", "POST"], cors=True)
def send_announcement():
    MongoServer = MongoService()
    MongoServer.connect()
    users_data = MongoServer.get_all_data()

    emails = [user['email'] for user in users_data]

    request = announcements_api.current_request
    request_body = request.json_body

    ses = SesMailSender(ses_client)
    for email in emails:
        ses_destination = SesDestination(
            tos=[email]
        )
        ses.send_email(
            source="techteampct@gmail.com",
            destination=ses_destination,
            subject=request_body['subject'],
            text=request_body['content'],
            html=request_body['content']
        )

    return


@announcements_api.route("/test-email")
def test_email():
    # PLEASE REPLACE WITH YOUR OWN EMAIL FOR TESTING
    emails = ['cwilliam.gough@gmail.com']

    ses = SesMailSender(ses_client)
    for email in emails:
        ses_destination = SesDestination(
            tos=[email]
        )
        ses.send_email(
            source="techteampct@gmail.com",
            destination=ses_destination,
            subject="Subject Test",
            text="test data",
            html="<h1>test</h1>"
        )
    return f'Sent emails to {len(emails)} people: {emails}'
