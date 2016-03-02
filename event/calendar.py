import httplib2
import os
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import datetime
from django.http import HttpResponse

from oauth2client.service_account import ServiceAccountCredentials
import argparse
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(__file__), '..', 'client_secret.json')
SCOPES = 'https://www.googleapis.com/auth/calendar'
APPLICATION_NAME = 'SD Burner Events'

def get_10_events():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CLIENT_SECRET_FILE, scopes=SCOPES)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        return HttpResponse('No upcoming events found.')
    response = HttpResponse()
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        response.write(start, event['summary'])

    return response