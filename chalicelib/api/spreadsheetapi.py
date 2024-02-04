import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
"""
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

"""
The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1n87Cor44wQZJqIEdSOLz_whRgZX3KOhkALhwVOLAEIA"
SAMPLE_RANGE_NAME = "Class Data!A2:E"
"""

def getdata(fileId, datarange):
      
      creds = None
      # The file token.json stores the user's access and refresh tokens, and is
      # created automatically when the authorization flow completes for the first
      # time.
      if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
      # If there are no (valid) credentials available, let the user log in.
      if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
          creds.refresh(Request())
        else:
          flow = InstalledAppFlow.from_client_secrets_file(
              "credentials.json", SCOPES
          )
          creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
          token.write(creds.to_json())
      
      try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=fileId, range=datarange)
            .execute()
        )
        values = result.get("values", [])

        if not values:
          print("No data found.")
          return None
        return values
      except HttpError as err:
        print(err)

def extractFileId(url):
      #get full url of the google spread sheet and extract file ID
      #extract google spread sheet ID
      #https://docs.google.com/spreadsheets/d/spreadsheetId/edit#gid=0     
      #after https://docs.google.com/spreadsheets/d/ ; before /


      fileId = str(url)[39:82]
      
      return fileId