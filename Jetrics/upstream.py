# Built In Modules
import datetime
import logging
import os
import os.path

# 3rd Party Modules
import requests
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# Global Variables
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.environ['SPREADSHEET_ID']
log = logging.getLogger(__name__)


def get_google_sheets():
    """
    Gets the Sheets client
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    return sheet


def get_values(client, x1, x2, y1, y2, sheet='Sheet1'):
    """
    Helper function to get values from sheet.


    :param googleapiclient.discovery.Resource client: Sheets client
    :param Int x1: X1 coordinate
    :param Int x2: X2 coordinate
    :param Int y1: Y1 coordinate
    :param Int y2: Y2 coordinate
    :param String sheet: Which sheet to parse data from (default is Sheet1)
    :return: Values
    :rtype: List
    """
    pass
    if sheet == 'Sheet1':
        resp = client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=get_coordinates_string(x1, x2, y1, y2)).execute()
    else:
        resp = client.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=get_coordinates_string(x1, x2, y1, y2, sheet=sheet)).execute()
    return resp.get('values', [])


def get_coordinates_string(x1, x2, y1, y2, sheet='Sheet1'):
    """
    Helper function to return the A1 (Google Sheet) notation.
    :param Int x1: X1 coordinate
    :param Int x2: X2 coordinate
    :param Int y1: Y1 coordinate
    :param Int y2: Y2 coordinate
    :param String sheet: Which sheet to parse data from (default is Sheet1)
    :return: A1 notation
    :rtype: String
    """
    return f"{sheet}!{get_letter_from_coordinate(x1)}{y1}:{get_letter_from_coordinate(x2)}{y2}"


def get_letter_from_coordinate(x):
    """
    Helper function to get coordinate from number


    :param Int x: X coordinate
    :return: Letter corresponding to number
    :rtype: String
    """
    alpha = ['INVALID', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
             'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
             'V', 'W', 'X', 'Y', 'Z']
    return alpha[x]


def sync_with_upstream(values):
    """
    Function to sync with upstream source.


    :param Dict values: List of values returned from downstream
    """
    # Get out Google Sheet client
    client = get_google_sheets()

    # Find the next empty row
    index = 1
    while True:
        if not get_values(client, 1, 1, index, index):
            break
        else:
            index += 1

    # Add the date to the first column
    val = [[datetime.datetime.today().strftime('%Y-%m-%d')]]
    client.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=get_coordinates_string(1, 1, index, index),
        body={'values': val},
        valueInputOption='USER_ENTERED').execute()
    # Append our values to the sheet
    for column in range(2, 15):
        title_of_column = get_values(client, column, column, 1, 1)[0][0]
        # Add the appropriate value
        if values[title_of_column.strip()] == -1:
            log.warning(f"{title_of_column.strip()} returned -1")
        val = [[values[title_of_column.strip()]]]
        client.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=get_coordinates_string(column, column, index, index),
            body={'values': val},
            valueInputOption='USER_ENTERED').execute()
