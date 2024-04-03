from google.oauth2 import service_account

# import google.auth
from googleapiclient.discovery import build

# from googleapiclient.errors import HttpError
# from google_auth_oauthlib.flow import InstalledAppFlow
import boto3
import json


class GoogleSheetsModule:
    def __init__(self):
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        ssm = boto3.client("ssm")
        creds = json.loads(
            ssm.get_parameter(
                Name="/Zap/GOOGLE_SERVICE_ACCOUNT_CREDENTIALS", WithDecryption=True
            )["Parameter"]["Value"]
        )
        self.creds = service_account.Credentials.from_service_account_info(
            creds, scopes=self.scopes
        )
        self.service = build("sheets", "v4", credentials=self.creds)

    def get_sheets(self, spreadsheet_id: str, include_properties: bool = False):
        sheet_metadata = (
            self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        )
        sheets = sheet_metadata.get("sheets", "")
        sheets_properties = [sheet.get("properties", {}) for sheet in sheets]
        # Only include id and title
        if not include_properties:
            sheets_properties = [
                {"sheetId": sheet.get("sheetId"), "title": sheet.get("title")}
                for sheet in sheets_properties
            ]
        return sheets_properties

    def find_matching_row(
        self, spreadsheet_id: str, sheet_name: str, cols: list[str], val_to_match: list
    ):
        range = f"{sheet_name}!{cols[0]}:{cols[-1]}"
        response = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range)
            .execute()
        )
        rows = list(response["values"])
        for idx, row in enumerate(rows):
            if row[0] == val_to_match[0] and row[1] == val_to_match[1]:
                return idx

        return -1

    def update_row(
        self, spreadsheet_id: str, sheet_name: str, col: str, row: int, data: list
    ):
        body = {"values": data}
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!{col.upper()}{row}",
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()
