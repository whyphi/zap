from google.oauth2 import service_account

# import google.auth
from googleapiclient.discovery import build

# from googleapiclient.errors import HttpError
# from google_auth_oauthlib.flow import InstalledAppFlow
import boto3
import json
from thefuzz import fuzz


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

    def get_rows(self, spreadsheet_id: str, sheet_name: str, start_row: int, end_row: int):
        range = f"{sheet_name}!A{start_row}:Z{end_row}"
        response = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range)
            .execute()
        )
        return response

    def get_all_cells(self, spreadsheet_id: str, sheet_name: str):
        range = f"{sheet_name}!A1:Z"
        response = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range)
            .execute()
        )
        return response

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

    def find_matching_name(
        self, spreadsheet_id: str, sheet_name: str, cols: list[str], name_to_match: list, use_similarity: bool=False
    ):
        range = f"{sheet_name}!{cols[0]}:{cols[-1]}"
        response = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range)
            .execute()
        )
        rows = list(response["values"])
        
        if use_similarity:

            best_idx, score = 0, fuzz.ratio(name_to_match, f"{rows[0][0]} {rows[0][1]}")

            for idx, row in enumerate(rows):
                name = f"{row[0]} {row[1]}"
                curr_score = fuzz.ratio(name_to_match, name)
                if curr_score > score:
                    best_idx = idx
                    score = curr_score

            return best_idx
        else:
            for idx, row in enumerate(rows):
                name = f"{row[0]} {row[1]}"
                if name_to_match in name:
                    return idx

            return -1
        
    def find_matching_email(
        self, spreadsheet_id: str, sheet_name: str, col: str, email_to_match: str
    ):
        range = f"{sheet_name}!{col}:{col}"
        response = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range)
            .execute()
        )

        rows = list(response["values"])
        for idx, row in enumerate(rows):
            if email_to_match in row:
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

    def find_next_available_col(self, spreadsheet_id: str, sheet_name: str):
        # Find the next available column in row 1
        events_range = f"{sheet_name}!A1:Z1"
        response = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=events_range)
            .execute()
        )
        events = response["values"][0]

        next_col = chr(ord("A") + len(events))

        return next_col

    def add_event(self, spreadsheet_id: str, sheet_tab: str, event_name: str, col: str):
        self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_tab}!{col}{1}",
            valueInputOption="USER_ENTERED",
            body={"values": [[event_name]]},
        ).execute()
