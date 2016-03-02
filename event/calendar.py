import httplib2
import os
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import datetime
from django.http import HttpResponse

from django.forms.models import model_to_dict
import json
from event.models import Event

from oauth2client.service_account import ServiceAccountCredentials
import argparse
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(__file__), '..', 'client_secret.json')
SCOPES = 'https://www.googleapis.com/auth/calendar'
APPLICATION_NAME = 'SD Burner Events'

import datetime

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        dict = {'dateTime': serial, 'timeZone': 'America/Los_Angeles'}
        return dict
    raise TypeError ("Type not serializable")

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
        response.write( "%s - %s" % (start , event['summary']))

    return response

def add_event(event):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CLIENT_SECRET_FILE, scopes=SCOPES)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    event_dict= model_to_dict(event, exclude=['owner', 'approved', 'id'])

    #These should be changed and model updated###
    event_dict['summary']= event_dict.pop('title')
    event_dict['start']= event_dict.pop('date')
    event_dict['end']= event_dict['start']+ datetime.timedelta(hours=1)
    ######

    event_json= json.dumps(event_dict, default=json_serial)
    event_obj= json.loads(event_json)
    
    print(event_json)
    #httplib2.debuglevel = 4
    cal_event = service.events().insert(calendarId='primary', body=event_obj).execute()
    print ('Event created: %s' % (cal_event.get('htmlLink')))