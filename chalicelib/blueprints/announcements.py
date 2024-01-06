from chalice import Blueprint
from chalicelib.services.ses import SesMailSender, SesDestination
from chalicelib.services.mongo import MongoService
import boto3

announcements_routes = Blueprint(__name__)

ses_client = boto3.client('ses')


# why is GET needed?
@announcements_routes.route("/announcement", methods=["GET", "POST"], cors=True)
def send_announcement():
    MongoServer = MongoService()
    MongoServer.connect()
    users_data = MongoServer.get_all_data()

    emails = [user['email'] for user in users_data]

    # PLEASE REPLACE WITH YOUR OWN EMAIL FOR TESTING
    # emails = ['cwilliam.gough@gmail.com']

    request = announcements_routes.current_request
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

    return f'Sent emails to {len(emails)} people: {emails}'


# @announcements_routes.route("/test-email")
# def test_email():
#     ses_destination = SesDestination(
#         tos=["techteampct@gmail.com"]
#     )
#     ses = SesMailSender(ses_client)
#     ses.send_email(
#         source="techteampct@gmail.com",
#         destination=ses_destination,
#         subject="Subject Test",
#         text="test data",
#         html="<h1>test</h1>"
#     )
#     return 'success'
