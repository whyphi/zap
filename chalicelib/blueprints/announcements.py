from chalice import Blueprint
from chalicelib.services.ses import SesMailSender, SesDestination
from chalicelib.services.mongo import MongoService
import boto3

announcements_routes = Blueprint(__name__)

ses_client = boto3.client('ses')

message = """
            Hey all! Wanted to send a quick update on the email broadcast feature. As you can tell, 
            the first version of the backend is complete. All that's left is to make the API call from the frontend 
            and we can deploy the feature (after the necessary tests, of course).
            <br /><br />
            Just as a reminder, if you want to track the progress on this feature, you can check out this 
            <a href="https://github.com/whyphi/zap/pull/9">draft PR!</a> Looking forward to making more 
            git commits with all of you.
            <br /><br />
            Happy coding!
            <br /><br />
            Best,
            <br /><br />
            Chris
        """


@announcements_routes.route("/announcement")
def send_announcement():
    MongoServer = MongoService()
    MongoServer.connect()
    users_data = MongoServer.get_all_data()
    
    emails = [user['email'] for user in users_data]
    # print(emails)

    # emails = ['cwgough@bu.edu', 'cwilliam.gough@gmail.com']

    ses = SesMailSender(ses_client)
    for email in emails:
        ses_destination = SesDestination(
            tos=[email]
        )
        ses.send_email(
            source="techteampct@gmail.com",
            destination=ses_destination,
            subject="Hello World",
            text="test",
            html=message
        )

    return f'Sent emails to {len(emails)} people: {emails}'

@announcements_routes.route("/test-email")
def test_email():
    ses_destination = SesDestination(
        tos=["cwgough@bu.edu"]
    )
    ses = SesMailSender(ses_client)
    ses.send_email(
        source="techteampct@gmail.com",
        destination=ses_destination,
        subject="Subject Test",
        text="test data",
        html="<h1>test</h1>"
    )
    return 'success'