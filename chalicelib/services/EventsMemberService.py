from chalicelib.repositories.repository_factory import RepositoryFactory
from chalice.app import NotFoundError, BadRequestError, UnauthorizedError
from chalicelib.handlers.error_handler import GENERIC_CLIENT_ERROR
from postgrest.exceptions import APIError
import json
import uuid
from bson import ObjectId
import datetime
from chalicelib.modules.google_sheets import GoogleSheetsModule
from chalicelib.modules.ses import ses, SesDestination

# IN PROGRESS


class EventsMemberService:
    class BSONEncoder(json.JSONEncoder):
        """JSON encoder that converts Mongo ObjectIds and datetime.datetime to strings."""

        def default(self, o):
            if isinstance(o, datetime.datetime):
                return o.isoformat()
            elif isinstance(o, ObjectId):
                return str(o)
            return super().default(o)

    def __init__(self):
        self.events_member_repo = RepositoryFactory.events_member()
        self.event_timeframes_member_repo = RepositoryFactory.event_timeframes_member()
        self.events_member_attendees_repo = RepositoryFactory.events_member_attendees()
        self.event_tag_repo = RepositoryFactory.event_tags()
        self.tag_repo = RepositoryFactory.tags()
        self.users_repo = RepositoryFactory.users()

    def create_timeframe(self, timeframe_data: dict):
        try:
            timeframe_data["id"] = str(uuid.uuid4())
            return self.event_timeframes_member_repo.create(timeframe_data)
        except Exception as e:
            raise BadRequestError(f"Failed to create timeframe: {str(e)}")

    def get_timeframe(self, timeframe_id: str):
        try:
            timeframe = self.event_timeframes_member_repo.get_by_id(timeframe_id)
            return json.dumps(timeframe, cls=self.BSONEncoder)
        except Exception as e:
            raise NotFoundError(f"Failed to retrieve timeframe: {str(e)}")

    def get_all_timeframes_and_events(self):
        """Retrieve all timeframes from the database."""
        try:
            timeframes = self.event_timeframes_member_repo.get_all(
                select_query="*, events_member(*)"
            )
            return timeframes
        except Exception as e:
            raise NotFoundError(GENERIC_CLIENT_ERROR)

    def delete_timeframe(self, timeframe_id: str):
        # EDIT: update to take advantage of cascading deletes
        try:
            self.event_timeframes_member_repo.delete(timeframe_id)
            return {"statusCode": 200}
        except Exception as e:
            raise BadRequestError(f"Failed to delete timeframe: {str(e)}")

    def create_event(self, timeframe_id: str, event_data: dict):
        # Get Google Spreadsheet ID from timeframe
        try:
            timeframe_data = self.event_timeframes_member_repo.get_by_id(timeframe_id)
        except Exception as e:
            raise BadRequestError(f"Failed to retrieve timeframe: {str(e)}")

        spreadsheet_id = timeframe_data["spreadsheet_id"]

        # Add event name to Google Sheets
        if not spreadsheet_id:
            raise NotFoundError("No associated spreadsheet found for timeframe.")

        gs = GoogleSheetsModule()
        col = gs.find_next_available_col(spreadsheet_id, event_data["spreadsheet_tab"])
        gs.add_event(
            spreadsheet_id, event_data["spreadsheet_tab"], event_data["name"], col
        )

        # Insert the event in events_member table
        try:
            id = str(uuid.uuid4())
            event_data["id"] = id
            event_data["timeframe_id"] = timeframe_data["id"]
            event_data["spreadsheet_col"] = col
            self.events_member_repo.create(data=event_data)
            return event_data
        except Exception as e:
            raise BadRequestError(f"Failed to create event: {str(e)}")

    def get_event(self, event_id: str):
        try:
            event = self.events_member_repo.get_by_id(
                id_value=event_id,
                select_query="*, attendees:events_member_attendees(user:users(*), checkin_time)",
            )
            return event
        except Exception as e:
            raise NotFoundError(GENERIC_CLIENT_ERROR)

    def checkin(self, event_id: str, user: dict) -> dict:
        """Checks in a user to an event.

        Arguments:
            event_id {str} -- ID of the event to check into.
            user {dict} -- Dictionary containing user ID and name.

        Returns:
            dict -- Dictionary containing status and message.
        """
        user_id, code = user["id"], user["code"]
        try:
            user = self.users_repo.get_by_id(user_id)
        except Exception as e:
            raise BadRequestError(f"Failed to retrieve user: {str(e)}")

        if user is None:
            raise NotFoundError(f"User with ID {user_id} does not exist.")

        user_name, user_email = user.get("name", ""), user.get("email", "")

        try:
            event = self.events_member_repo.get_by_id(event_id)
        except Exception as e:
            raise BadRequestError(f"Failed to retrieve event: {str(e)}")

        # need to add code field into event_member
        if code.lower().strip() != event.get("code", "").lower().strip():
            raise UnauthorizedError("Invalid code.")

        # Update events_member_attendees with checkin data
        try:
            self.events_member_attendees_repo.create(
                {
                    "event_id": event_id,
                    "user_id": user_id,
                    "checkin_time": datetime.datetime.now().isoformat(),
                }
            )
        except APIError as e:
            if e.code == "23505":
                raise BadRequestError("User has already checked in.")
            raise BadRequestError(GENERIC_CLIENT_ERROR)

        # Get timeframe document to get Google Sheets info
        timeframe = self.event_timeframes_member_repo.get_by_id(event["timeframe_id"])

        # Get Google Sheets information
        ss_id = timeframe.get("spreadsheet_id", "")

        # Initialize Google Sheets Module
        gs = GoogleSheetsModule()

        # Find row in Google Sheets that matches user's email
        row_num = gs.find_matching_email(
            spreadsheet_id=ss_id,
            sheet_name=event["spreadsheet_tab"],
            col="C",
            email_to_match=user_email,
        )

        if row_num == -1:
            # Roll-back supabse update if error updating Google Sheets
            self.events_member_attendees_repo.delete_by_field(
                field="user_id", value=user["id"]
            )
            raise BadRequestError("Error updating Google Sheets. User email not found.")

        # Update Google Sheets cell with a "1" if user has checked in
        gs.update_row(
            spreadsheet_id=ss_id,
            sheet_name=event["spreadsheet_tab"],
            col=event["spreadsheet_col"],
            row=row_num + 1,
            data=[["1"]],
        )

        # Send email to user that has checked in
        email_content = f"""
            Hi {user_name},<br><br>

            Thank you for checking in to <b>{event["name"]}</b>! This is a confirmation that you have checked in.<br><br>

            Regards,<br>
            PCT Tech Team<br><br>

            ** Please note: Do not reply to this email. This email is sent from an unattended mailbox. Replies will not be read.
        """

        ses_destination = SesDestination(tos=[user_email])
        ses.send_email(
            source="checkin-bot@why-phi.com",
            destination=ses_destination,
            subject=f"Check-in Confirmation: {event['name']}",
            text=email_content,
            html=email_content,
        )

        return {
            "status": True,
            "message": f"{user_name} has successfully been checked in.",
        }

    def delete(self, event_id: str):
        # Check if event exists and if it doesn't return errors
        try:
            event = self.events_member_repo.get_by_id(event_id)
        except Exception as e:
            raise BadRequestError(f"Failed to retrieve event: {str(e)}")

        if event is None:
            raise NotFoundError(f"Event with ID {event_id} does not exist.")

        try:
            self.events_member_repo.delete(event_id)
        except Exception as e:
            raise BadRequestError(f"Failed to delete event: {str(e)}")

        # EDIT: no return?

    def get_timeframe_sheets(self, timeframe_id: str):
        try:
            # Check if timeframe exists
            timeframe = self.event_timeframes_member_repo.get_by_id(timeframe_id)
        except Exception as e:
            raise BadRequestError(f"Failed to retrieve timeframe: {str(e)}")

        if "spreadsheet_id" not in timeframe or timeframe["spreadsheet_id"] == "":
            return []

        gs = GoogleSheetsModule()
        sheets = gs.get_sheets(timeframe["spreadsheet_id"], include_properties=False)
        return [sheet["title"] for sheet in sheets]


events_member_service = EventsMemberService()
