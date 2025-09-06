from google.oauth2 import service_account

# import google.auth
from googleapiclient.discovery import build

# from googleapiclient.errors import HttpError
# from google_auth_oauthlib.flow import InstalledAppFlow
import boto3
import json
from thefuzz import fuzz
import re


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

    def get_all_cells(self, spreadsheet_id: str, sheet_name: str, render_option="FORMATTED_VALUE"):
        range = f"{sheet_name}!A1:Z"
        response = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range, valueRenderOption=render_option)
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
        events_range = f"{sheet_name}!1:1"  # Get the entire first row
        response = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=events_range)
            .execute()
        )
        
        events = response.get("values", [[]])[0] if "values" in response else []
        col_index = len(events)  # 0-based index

        # Convert index to A1 notation
        def index_to_column_name(n: int) -> str:
            """Convert a zero-based index to a column name (A, B, ..., Z, AA, AB, ...)"""
            name = ""
            while n >= 0:
                n, remainder = divmod(n, 26)
                name = chr(65 + remainder) + name
                n -= 1
            return name

        return index_to_column_name(col_index)


    def get_sheet_with_grid_data(self, spreadsheet_id: str, sheet_name: str):
        """
        Retrieves full grid data including cell metadata with hyperlink information.
        
        Grid data is a detailed representation of sheet contents returned by the Google Sheets API
        when includeGridData=True. It contains comprehensive information about each cell including
        values, formatting, data validation rules, hyperlinks, notes, and other metadata. This
        structure allows access to all cell information beyond just the displayed values.
        
        Args:
            spreadsheet_id (str): The ID of the spreadsheet.
            sheet_name (str): The name of the sheet to retrieve.
            
        Returns:
            dict: The complete sheet data including grid data with hyperlinks.
        """
        # Get the sheet ID first
        sheets = self.get_sheets(spreadsheet_id, include_properties=True)
        sheet_id = next((sheet.get("sheetId") for sheet in sheets if sheet.get("title") == sheet_name), None)
        
        if sheet_id is None:
            return None
        
        # Request the sheet with full grid data including hyperlinks
        response = self.service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            ranges=[sheet_name],
            includeGridData=True
        ).execute()
        
        if "sheets" in response and len(response["sheets"]) > 0:
            return response["sheets"][0]
        
        return None
    
    def get_hyperlink_from_grid_data(self, sheet_data, row_index, col_index):
        """
        Extracts hyperlink from grid data for a specific cell.
        
        Args:
            sheet_data (dict): Sheet data returned by get_sheet_with_grid_data.
            row_index (int): The row index (1-based).
            col_index (int): The column index (0-based).
            
        Returns:
            str: The hyperlink URL or None if not found.
        """
        if sheet_data is None:
            return None
        if "data" not in sheet_data:
            return None
        if sheet_data["data"] is None:
            return None
            
        grid_data = sheet_data["data"][0]
        
        # Convert to 0-based row index
        row_index = row_index - 1
        
        # Check if the row exists
        if "rowData" not in grid_data or row_index >= len(grid_data["rowData"]):
            return None
            
        row_data = grid_data["rowData"][row_index]
        
        # Check if the cell exists in this row
        if "values" not in row_data or col_index >= len(row_data["values"]):
            return None
            
        cell = row_data["values"][col_index]
        
        # Check if the cell has a hyperlink
        if "hyperlink" in cell.get("userEnteredValue", {}).get("formulaValue", ""):
            # Extract URL from formula
            formula = cell["userEnteredValue"]["formulaValue"]
            match = re.match(r'=HYPERLINK\("(.*?)"', formula)
            if match:
                return match.group(1)
        elif "hyperlink" in cell.get("hyperlink", {}):
            return cell["hyperlink"]
        elif "hyperlinkUrl" in cell.get("dataValidation", {}):
            return cell["dataValidation"]["hyperlinkUrl"]
        elif "hyperlinkDisplayType" in cell and "hyperlinkUrl" in cell:
            return cell["hyperlinkUrl"]
        
        # For UI-inserted hyperlinks
        if "userEnteredFormat" in cell and "textFormat" in cell["userEnteredFormat"]:
            text_format = cell["userEnteredFormat"]["textFormat"]
            if "link" in text_format and "uri" in text_format["link"]:
                return text_format["link"]["uri"]
        
        return None

    def add_event(self, spreadsheet_id: str, sheet_tab: str, event_name: str, col: str):
        self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_tab}!{col}{1}",
            valueInputOption="USER_ENTERED",
            body={"values": [[event_name]]},
        ).execute()
