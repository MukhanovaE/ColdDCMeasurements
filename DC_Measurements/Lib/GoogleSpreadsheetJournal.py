import os
from os import path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


class GoogleSpreadsheetJournal:
    def _get_auth_file(self, filename):
        return path.join(os.getcwd(), 'Cloud_auth', filename)

    def _load_document_id(self):
        auth_file = self._get_auth_file('Journal_document_id')
        with open(auth_file, 'r') as f:
            return f.read().strip()

    def _count_values(self):
        sheet = self._sheet
        column = sheet.values().get(spreadsheetId=self._document_id, range='A:A').execute()
        return len(column['values'])

    def __init__(self):
        self._document_id = self._load_document_id()
        scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

        google_auth_file = self._get_auth_file('Google_auth.json')
        client_secrets_file = self._get_auth_file('client_secrets.json')

        creds = None
        if os.path.exists(google_auth_file):
            creds = Credentials.from_authorized_user_file(google_auth_file, scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            '''if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())'''
            # else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(google_auth_file, 'w') as token:
                token.write(creds.to_json())

        service = build('sheets', 'v4', credentials=creds)
        self._sheet = service.spreadsheets()

    def add_entry(self, sample_name, structure_name, contacts, date, time, meas_title):
        pos_to_insert = self._count_values() + 1
        body = {
            'values': [[sample_name, structure_name, contacts, date, time, meas_title]],
        }
        sheet = self._sheet
        rng = f'A{pos_to_insert}:F{pos_to_insert}'
        sheet.values().update(spreadsheetId=self._document_id, range=rng, valueInputOption='RAW',
                              body=body).execute()
