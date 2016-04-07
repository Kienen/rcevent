import uuid
import datetime
import httplib2

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.template.loader import render_to_string

from account.timezones import TIMEZONES
from apiclient import discovery
import oauth2client
from oauth2client.service_account import ServiceAccountCredentials

from .colors import GOOGLE_CALENDAR_COLORS as COLORS

credentials = ServiceAccountCredentials.from_json_keyfile_name(
                settings.CLIENT_SECRET_FILE, scopes='https://www.googleapis.com/auth/calendar')
http = credentials.authorize(httplib2.Http())
service = discovery.build('calendar', 'v3', http=http)

class Calendar(models.Model):
    order = models.PositiveIntegerField(unique=True)
    summary = models.CharField(max_length=100, unique=True)
    timeZone = models.CharField(max_length=100, choices=TIMEZONES, default= settings.TIME_ZONE)
    color = models.CharField(max_length=12, choices=COLORS, default= '%23CC3333')
    id = models.CharField(max_length=100, primary_key= True, editable=False)

    class Meta:
        ordering = ['order']
        
    def get_or_create_id(self):
        page_token = None
        while True:
          calendar_list = service.calendarList().list(pageToken=page_token).execute()
          for calendar_list_entry in calendar_list['items']:
            if calendar_list_entry['summary'] == self.summary:
                return calendar_list_entry['id']
          page_token = calendar_list.get('nextPageToken')
          if not page_token:
            break

        cal_dict= model_to_dict(calendar, fields=['summary', 'timeZone'])

        created_calendar = service.calendars().insert(body=cal_dict, colorRgbFormat=true, foregroundColor=self.color, backgroundColor='%23FFFFFF').execute()
        rule = {
                'scope': {
                    'type': 'default'
                },
                'role': 'reader'
            }
        created_rule = service.acl().insert(calendarId=created_calendar['id'], body=rule).execute()

        if settings.DEFAULT_FROM_EMAIL:
            rule = {
                    'scope': {
                        'type': 'user',
                        'value': settings.DEFAULT_FROM_EMAIL
                    },
                    'role': 'owner'
                }
            created_rule = service.acl().insert(calendarId=self.id, body=rule).execute()
        return created_calendar['id']

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self.get_or_create_id()

        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.summary

    def get_absolute_url(self):
        return '/event/calendar/%s'% self.order

    def add_event(self, event):
        event_dict= model_to_dict(event, 
                                  exclude=['owner', 'approved', 'rcnotes', 'timezone'
                                           'category', 'url', 'recurrence', 
                                           'rrule_freq', 'rrule_until', 'rrule_byday'])
        if event_dict['price']:
            event_dict['description']= \
                "(TICKET PRICE %s) %s" % (event_dict.pop('price') , 
                                          event_dict['description'])
        #"RRULE:FREQ=WEEKLY;COUNT=5;BYDAY=TU,FR"   

        if event.recurrence:
            rrule= 'RRULE:FREQ=' + event.rrule_freq + ';UNTIL=' + event.rrule_until.strftime('%Y%m%d') + ';'
            if event.rrule_byday:
                byday= event.rrule_byday.replace('[','').replace(']','').replace(' ','').replace("'","")
                rrule +=  'BYDAY=' + byday + ';'
            event_dict['recurrence']= [rrule]
            
        event_dict['anyoneCanAddSelf'] = True
        event_dict['guestsCanInviteOthers'] = True
        event_dict['start']= {'dateTime': event.start.isoformat(), 'timeZone': event.timeZone}
        event_dict['end']= {'dateTime': event.end.isoformat(), 'timeZone': event.timeZone}
        if settings.DEBUG:
            print (event_dict)
        cal_event = service.events().insert(calendarId=self.id, 
                                                 body=event_dict).execute()
        if settings.DEBUG:
            print ('Event created: %s' % (cal_event.get('htmlLink')))

    def list_events(self, time_delta=365):
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        time_max = (datetime.datetime.utcnow() 
                    +datetime.timedelta(days=time_delta)).isoformat() + 'Z'
        events = service.events().list(calendarId=self.id, timeMin=now, timeMax=time_max,
                                       singleEvents=True, orderBy='startTime').execute()
        for event in events['items']:
            event['start']['dateTime']= \
                datetime.datetime.strptime(event['start']['dateTime'][:19], '%Y-%m-%dT%H:%M:%S')
        return events['items']

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User)
    summary = models.CharField(max_length=100)
    start  = models.DateTimeField()
    end = models.DateTimeField()
    timeZone = models.CharField(max_length=100, choices=TIMEZONES, default= settings.TIME_ZONE)
    location = models.CharField(max_length=100)
    description = models.TextField()
    approved = models.BooleanField(default=False)
    category = models.ForeignKey('Calendar', on_delete=models.CASCADE)
    price = models.FloatField(blank=True, null=True)
    url = models.URLField(blank=True)
    rcnotes = models.TextField(blank=True)
    recurrence = models.BooleanField(default=False)
    rrule_freq = models.CharField(max_length=100, blank=True, choices = [('WEEKLY','Every Week'),
                                                                         ('MONTHLY','Every Month')])
    rrule_until = models.DateField(blank= True, null=True)
    rrule_byday = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['start']

    def get_absolute_url(self):
        return '/event/%s'% self.id

    def __str__(self):
        return self.summary

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.approved == True:
            self.category.add_event(self)

class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscribed_calendars= JSONField(null=True) 

    def get_absolute_url(self):
        return '/event/profile/%s'% self.id          

class Newsletter(models.Model):
    last= models.DateField(blank= True, null=True)
    next= models.DateField(blank= True, null=True)
    intro= models.TextField(blank=True)

    def send_newsletter(self):
        current_site = Site.objects.get_current()
        calendars_events = {calendar.summary:calendar.list_events(time_delta=30)
                            for calendar in Calendar.objects.all()}

        for profile in Profile.objects.all().iterator():
            subscribed_calendars= {calendar:subscribed 
                                   for calendar, subscribed in profile.subscribed_calendars.items() 
                                   if subscribed == True}

            if not subscribed_calendars:
                continue
            
            message_events = {calendar_summary:calendars_events[calendar_summary]
                              for calendar_summary in subscribed_calendars
                              if calendar_summary in calendars_events}

            message = render_to_string('newsletter.txt', {'intro': self.intro,
                                                          'events_dict': message_events,
                                                          'id': profile.id,
                                                          'domain': current_site.domain,
                                                          })
            
            send_mail(current_site.name + " " + datetime.date.today().isoformat() + " Newsletter",
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [profile.user.email]
                      )

        self.last= datetime.date.today()
        self.next= datetime.date.today() + (datetime.timedelta(days=30))


        