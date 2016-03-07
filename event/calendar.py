import datetime
import httplib2
import json
import os
from django.forms.models import model_to_dict
from django.http import HttpResponse
from apiclient import discovery
import oauth2client
from oauth2client.service_account import ServiceAccountCredentials

CLIENT_SECRET_FILE = os.path.join(os.path.dirname(__file__), '..', 'client_secret.json')
SCOPES = 'https://www.googleapis.com/auth/calendar'
APPLICATION_NAME = 'SD Burner Events'

# def json_serial(obj):
#     """JSON serializer for objects not serializable by default json code"""

#     if isinstance(obj, datetime.datetime):
#         serial = obj.isoformat()
#         #add timezone to model
#         dict = {'dateTime': serial, 'timeZone': 'America/Los_Angeles'}
#         return dict
#     raise TypeError ("Type not serializable")

# def get_or_create_id(calendar):
#     credentials = ServiceAccountCredentials.from_json_keyfile_name(
#     CLIENT_SECRET_FILE, scopes=SCOPES)
#     http = credentials.authorize(httplib2.Http())
#     service = discovery.build('calendar', 'v3', http=http)
    
#     page_token = None
#     while True:
#       calendar_list = service.calendarList().list(pageToken=page_token).execute()
#       for calendar_list_entry in calendar_list['items']:
#         if calendar_list_entry['summary'] == calendar.summary:
#             return calendar_list_entry['id']
#       page_token = calendar_list.get('nextPageToken')
#       if not page_token:
#         break

#     cal_dict= model_to_dict(calendar, fields=['summary', 'timeZone'])
#     cal_json= json.dumps(cal_dict)
#     cal_obj= json.loads(cal_json)
#     created_calendar = service.calendars().insert(body=cal_obj).execute()
#     rule = {
#             'scope': {
#                 'type': 'default'
#             },
#             'role': 'reader'
#         }
#     created_rule = service.acl().insert(calendarId=created_calendar['id'], body=rule).execute()
#     return created_calendar['id']

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

    response = HttpResponse()
    response.write('primary<br>')
    acl = service.acl().list(calendarId='primary').execute()

    for rule in acl['items']:
        response.write( '%s: %s<br>' % (rule['id'], rule['role']))
    if not events:
        response.write('No upcoming events found.<br>')
    else:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            response.write( "%s - %s<br>" % (start , event['summary']))

    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            response.write(calendar_list_entry['summary']+'<br>')
            response.write(calendar_list_entry['accessRole']+'<br>')

            acl = service.acl().list(calendarId=calendar_list_entry['id']).execute()

            for rule in acl['items']:
                response.write( '%s: %s<br>' % (rule['id'], rule['role']))

            eventsResult = service.events().list(
                calendarId=calendar_list_entry['id'], timeMin=now, maxResults=10, singleEvents=True,
                orderBy='startTime').execute()
            events = eventsResult.get('items', [])
            if not events:
                response.write('No upcoming events found.<br>')
            else:
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    response.write( "%s - %s<br>" % (start , event['summary']))
            
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    return response


# class GoogleCalendar(object):
#     credentials = ServiceAccountCredentials.from_json_keyfile_name(
#                     CLIENT_SECRET_FILE, scopes=SCOPES)
#     http = credentials.authorize(httplib2.Http())
#     service = discovery.build('calendar', 'v3', http=http)

#     def add_event(self, event):
#         event_dict= model_to_dict(event, 
#                                   exclude=['owner', 'approved', 'rcnotes', 'timezone'
#                                            'category', 'url', 'recurrence', 'rrule'])
#         if event_dict['price']:
#             event_dict['description']= \
#                 "(TICKET PRICE %s) %s" % (event_dict.pop('price') , 
#                                           event_dict['description'])

#         if not event_dict['end']:
#             event_dict['end']= event_dict['start']+ datetime.timedelta(hours=5)
#             event_dict['endTimeUnspecified']= True
            
#         event_dict['anyoneCanAddSelf'] = True
#         event_dict['guestsCanInviteOthers'] = True
#         event_json= json.dumps(event_dict, default=json_serial)
#         event_obj= json.loads(event_json)
#         cal_event = self.service.events().insert(calendarId=self.id, 
#                                                  body=event_obj).execute()

#         print ('Event created: %s' % (cal_event.get('htmlLink')))


