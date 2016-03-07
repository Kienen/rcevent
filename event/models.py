import uuid
from django.db import models
from django.contrib.auth.models import User
from account.timezones import TIMEZONES


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
credentials = ServiceAccountCredentials.from_json_keyfile_name(
                CLIENT_SECRET_FILE, scopes=SCOPES)
http = credentials.authorize(httplib2.Http())
service = discovery.build('calendar', 'v3', http=http)

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        #add timezone to model
        dict = {'dateTime': serial, 'timeZone': 'America/Los_Angeles'}
        return dict
    raise TypeError ("Type not serializable")

# Create your models here.
class Calendar(models.Model):
    order = models.PositiveIntegerField()
    summary = models.CharField(max_length=100, unique=True)
    timeZone = models.CharField(max_length=100, choices=TIMEZONES, default= "US/Pacific")
    id = models.CharField(max_length=100, primary_key= True, editable=False)

    class Meta:
        ordering = ['order']
        
    def get_or_create_id(self):
        page_token = None
        while True:
          calendar_list = service.calendarList().list(pageToken=page_token).execute()
          for calendar_list_entry in calendar_list['items']:
            if calendar_list_entry['summary'] == calendar.summary:
                return calendar_list_entry['id']
          page_token = calendar_list.get('nextPageToken')
          if not page_token:
            break

        cal_dict= model_to_dict(calendar, fields=['summary', 'timeZone'])
        cal_json= json.dumps(cal_dict)
        cal_obj= json.loads(cal_json)
        created_calendar = service.calendars().insert(body=cal_obj).execute()
        rule = {
                'scope': {
                    'type': 'default'
                },
                'role': 'reader'
            }
        created_rule = service.acl().insert(calendarId=created_calendar['id'], body=rule).execute()
        return created_calendar['id']

    def save(self, *args, **kwargs):
        self.id = self.get_or_create_id()
        super().save(self, *args, **kwargs)
        
    def __str__(self):
        return self.summary

    def add_event(self, event):
        event_dict= model_to_dict(event, 
                                  exclude=['owner', 'approved', 'rcnotes', 'timezone'
                                           'category', 'url', 'recurrence', 'rrule'])
        if event_dict['price']:
            event_dict['description']= \
                "(TICKET PRICE %s) %s" % (event_dict.pop('price') , 
                                          event_dict['description'])

        event_dict['anyoneCanAddSelf'] = True
        event_dict['guestsCanInviteOthers'] = True
        event_json= json.dumps(event_dict, default=json_serial)
        event_obj= json.loads(event_json)
        cal_event = service.events().insert(calendarId=self.id, 
                                                 body=event_obj).execute()

        print ('Event created: %s' % (cal_event.get('htmlLink')))

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User)
    summary = models.CharField(max_length=100)
    start  = models.DateTimeField()
    end = models.DateTimeField()
    timeZone = models.CharField(max_length=100, choices=TIMEZONES, default= "US/Pacific")
    location = models.CharField(max_length=100)
    description = models.TextField()
    approved = models.BooleanField(default=False)
    category = models.ForeignKey('Calendar', on_delete=models.CASCADE)
    price = models.FloatField(blank=True, null=True)
    url = models.URLField(blank=True)
    rcnotes = models.TextField(blank=True)
    recurrence = models.BooleanField(default=False)
    rrule = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['start']

    def get_absolute_url(self):
        return '/event/%s'% self.id

    def __str__(self):
        return self.summary

    def save(self, *args, **kwargs):
        super().save(self, *args, **kwargs)
        if self.approved == True:
            self.category.add_event(self)