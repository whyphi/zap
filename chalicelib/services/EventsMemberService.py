from chalicelib.repositories.repository_factory import RepositoryFactory
from chalice.app import NotFoundError, BadRequestError, UnauthorizedError
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
            timeframe_data["date_created"] = datetime.datetime.now().isoformat()
            
            if timeframe_data.get("spreadsheetId"):
                spreadsheet_id = timeframe_data.get("spreadsheetId", "")
                timeframe_data.pop("spreadsheetId", None)
                timeframe_data["spreadsheet_id"] = spreadsheet_id

            timeframe_data.pop("events", None)
            return self.event_timeframes_member_repo.create(timeframe_data)
        except Exception as e:
            raise BadRequestError(f"Failed to create timeframe: {str(e)}")

    def get_timeframe(self, timeframe_id: str):
        try:
            timeframe = self.event_timeframes_member_repo.get_by_id(timeframe_id)
            return json.dumps(timeframe, cls=self.BSONEncoder)
        except Exception as e:
            raise NotFoundError(f"Failed to retrieve timeframe: {str(e)}")

    def get_all_timeframes(self):
        """Retrieve all timeframes from the database."""
        try:
            timeframes = self.event_timeframes_member_repo.get_all()
            return json.dumps(timeframes, cls=self.BSONEncoder)
        except Exception as e:
            raise NotFoundError(f"Failed to retrieve timeframes: {str(e)}")

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
            timeframe_doc = self.event_timeframes_member_repo.get_by_id(timeframe_id)
        except Exception as e:
            raise BadRequestError(f"Failed to retrieve timeframe: {str(e)}")

        spreadsheet_id = timeframe_doc["spreadsheet_id"]

        # Add event name to Google Sheets
        if not spreadsheet_id:
            raise NotFoundError("No associated spreadsheet found for timeframe.")
        
        gs = GoogleSheetsModule()
        col = gs.find_next_available_col(spreadsheet_id, event_data["sheetTab"])
        gs.add_event(spreadsheet_id, event_data["sheetTab"], event_data["name"], col)

        # Insert the event in events_member table
        try:
            event_id = str(uuid.uuid4())
            self.events_member_repo.create({
                "id": event_id,
                "timeframe_id": timeframe_id,
                "name": event_data.get("name", ""),
                "date_created": datetime.datetime.now().isoformat(),
                "spreadsheet_tab": event_data.get("sheetTab", ""),
                "spreadsheet_col": col,
                "code": event_data.get("code", ""),
            })
        except Exception as e:
            raise BadRequestError(f"Failed to create event: {str(e)}")

        # Insert tags into tags table
        tag_ids = []
        try:
            for tag in event_data.get("tags", []):
                existing_tag = self.tag_repo.get_all_by_field("name", tag)
                if not existing_tag:
                    tag_id = str(uuid.uuid4())
                    self.tag_repo.create({
                        "id": tag_id,
                        "name": tag,
                    })
                    tag_ids.append(tag_id)
                else:
                    tag_ids.append(existing_tag[0]["id"])
        except Exception as e:
            raise BadRequestError(f"Failed to create tags: {str(e)}")

        try:
            for tag_id in tag_ids:
                self.event_tag_repo.create({
                    "events_member_id": event_id,
                    "tag_id": tag_id
                })
        except Exception as e:
            raise BadRequestError(f"Failed to associate tags with event: {str(e)}")

        return json.dumps(event_data, cls=self.BSONEncoder)

    def get_event(self, event_id: str):
        event = self.events_member_repo.get_all_by_field("id", event_id)

        return json.dumps(event, cls=self.BSONEncoder)

    def checkin(self, event_id: str, user: dict) -> dict:
        """Checks in a user to an event.

        Arguments:
            event_id {str} -- ID of the event to check into.
            user {dict} -- Dictionary containing user ID and name.

        Returns:
            dict -- Dictionary containing status and message.
        """
        user_id, user_email, code = user["id"], user["email"], user["code"]
        try:
            member = self.users_repo.get_by_id(user_id)
        except Exception as e:
            raise BadRequestError(f"Failed to retrieve user: {str(e)}")
        
        if member is None:
            raise NotFoundError(f"User with ID {user_id} does not exist.")

        user_name = member.get("name", "")

        try:
            event = self.events_member_repo.get_by_id(event_id)
        except Exception as e:
            raise BadRequestError(f"Failed to retrieve event: {str(e)}")

        # need to add code field into event_member
        if code.lower().strip() != event.get("code", "").lower().strip():
            raise UnauthorizedError("Invalid code.")
        
        try:
            # Check if user has already checked in
            checked_in_users = self.events_member_attendees_repo.get_all_by_field("event_id", event_id, "user_id")
        except Exception as e:
            raise BadRequestError(f"Failed to retrieve checked-in users: {str(e)}")

        if any(d["userId"] == user_id for d in checked_in_users):
            raise BadRequestError(f"{user_name} has already checked in.")

        # Get timeframe document to get Google Sheets info
        timeframe = self.event_timeframes_member_repo.get_by_id(event.get("timeframe_id", ""))

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
            return {
                "status": False,
                "message": f"{user_name} was not found in the sheet.",
            }

        # Update Google Sheets cell with a "1" if user has checked in
        gs.update_row(
            spreadsheet_id=ss_id,
            sheet_name=event["spreadsheet_tab"],
            col=event["spreadsheet_col"],
            row=row_num + 1,
            data=[["1"]],
        )

        # Update events_member_attendees with checkin data
        self.events_member_attendees_repo.create({
            "event_id": event_id,
            "user_id": user_id,
            "checkin_time": datetime.datetime.now().isoformat(),
        })

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
