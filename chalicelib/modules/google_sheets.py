from google.oauth2 import service_account

# import google.auth
# from googleapiclient.discovery import build
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
    
    def update(self):
        pass