import uuid
import datetime
import httplib2
import re
import json
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.forms.models import model_to_dict
from django.template.loader import render_to_string
from account.timezones import TIMEZONES
from apiclient import discovery
from apiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
from .colors import GOOGLE_CALENDAR_COLORS_LIST as COLORS

credentials = ServiceAccountCredentials.from_json_keyfile_name(
                settings.CLIENT_SECRET_FILE, scopes='https://www.googleapis.com/auth/calendar')
http = credentials.authorize(httplib2.Http())
service = discovery.build('calendar', 'v3', http=http)

class Event(models.Model):
    id= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gcal_id= models.CharField(max_length=100, blank=True, editable= False)
    creator= models.ForeignKey(User, null= True)
    summary= models.CharField(max_length=100)
    start= models.DateTimeField()
    end= models.DateTimeField()
    timeZone= models.CharField(max_length=100, choices=TIMEZONES, default= settings.TIME_ZONE)
    location= models.CharField(max_length=100)
    description= models.TextField()
    calendar= models.ForeignKey('Calendar', on_delete=models.CASCADE)
    price= models.CharField(max_length=100, blank=True)
    url= models.URLField(blank=True)
    rcnotes= models.TextField(blank=True)
    recurring= models.BooleanField(default=False)
    htmlLink= models.TextField(blank=True, editable= False)

    class Meta:
        ordering = ['start']

    def get_absolute_url(self):
        return '/event/%s'% self.id

    def full_delete(self, *args, **kwargs):
        gcal_error= self.calendar.remove_event(self)
        super().delete(*args, **kwargs)
        return gcal_error

    def __str__(self):
        return self.summary

class Rrule(models.Model):
    event= models.ForeignKey(Event, on_delete=models.CASCADE)
    freq= models.CharField(max_length=10, blank=True, choices = [('WEEKLY','Every Week'),
                                                                  ('MONTHLY','Every Month')])
    until= models.DateField(blank= True, null= True)
    count= models.PositiveIntegerField(null= True)
    byday= ArrayField(models.CharField(max_length=3, blank=True)) 
    rdate= models.DateField(blank= True, null= True)
    exdate= models.DateField(blank= True, null= True)

    def __str__(self):
        rrule= ''
        if self.freq: 
            rrule= self.get_freq_display() + '; '
            if self.until:
                rrule+= 'Until: ' + self.until.strftime('%Y%m%d') + '; '
            if self.count:
                rrule+= str(self.count) + ' times; '
            if self.byday:
                rrule +=  'Every '
                for day in self.byday:
                    rrule += day + ','
                rrule = rrule[:-1]
        elif self.rdate:
            rrule='Also on '+ self.rdate.strftime('%b %d, %Y') 
        elif self.exdate:
            rrule= 'But not on '+ self.exdate.strftime('%b %d, %Y') 
        return rrule 

    def formatted(self):
        #"RRULE:FREQ=WEEKLY;COUNT=5;BYDAY=TU,FR"
        if self.freq: 
            rrule= 'RRULE:FREQ=' + self.freq + ';'
            if self.until:
                rrule+= 'UNTIL=' + self.until.strftime('%Y%m%d') + ';'
            if self.count:
                rrule+= 'COUNT=' + str(self.count) + ';'
            if self.byday:
                rrule +=  'BYDAY='
                for day in self.byday:
                    rrule += day + ','
                rrule = rrule[:-1]
        elif self.rdate:
            #"RDATE;VALUE=DATE:20150609,20150611",
            rrule='RDATE;VALUE=DATE:'+ self.rdate.strftime('%Y%m%d') + ';'
        elif self.exdate:
            #"EXDATE;VALUE=DATE:20150610",
            rrule= 'EXDATE;VALUE=DATE:'+ self.exdate.strftime('%Y%m%d') + ';'
        return rrule 

class CalendarList:
    def __init__(self):
        page_token = None
        self.calendars= []
        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            self.calendars+= calendar_list['items']
            page_token= calendar_list.get('nextPageToken')
            if not page_token:
                break
        for calendar in self.calendars:
            calendar_object= Calendar.objects.filter(id= calendar['id'])
            if calendar_object:
                calendar['public']= True
            else:
                calendar['public']= False

    def get_all_calendars(self):
        return self.calendars

    def get_private_calendars(self):
        return [calendar for calendar in self.calendars
                if not calendar['public']]

    def get_details(self, calendar_id):
        calendar= [calendar for calendar in self.calendars
                    if calendar['id'] == calendar_id]
        print (calendar[0])
        return calendar[0]

def valid_uuid(uuid):
    regex = re.compile('[0-9a-f]{12}4[0-9a-f]{3}[89ab][0-9a-f]{15}\Z', re.I)
    match = regex.match(uuid)
    return bool(match)

class Calendar(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description= models.TextField(blank=True)
    summary = models.CharField(max_length=100, unique=True)
    timeZone = models.CharField(max_length=100, choices=TIMEZONES, default= settings.TIME_ZONE)
    color = models.CharField(max_length=12, default= 'CC3333', editable= False)
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

        cal_dict= model_to_dict(self, fields=['summary', 'timeZone'])

        created_calendar = service.calendars().insert(body=cal_dict).execute()
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
            created_rule = service.acl().insert(calendarId=created_calendar['id'], body=rule).execute()
        return created_calendar['id']

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self.get_or_create_id()

        self.color= COLORS[self.order%42-1]
        gcal = service.calendars().get(calendarId=self.id).execute()
        gcal['summary']= self.summary
        gcal['description']= self.description
        gcal['timeZone']= self.timeZone
        updated_calendar = service.calendars().update(calendarId=self.id, body=gcal).execute()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.summary

    def get_absolute_url(self):
        return '/event/calendar/%s'% self.order

    def add_event(self, event):
        event_dict= model_to_dict(event, 
                                  exclude=['creator', 'rcnotes', 'timezone', 'price', 'htemlLink'
                                           'calendar', 'recurrence', 'start', 'end' , 'url'])
        event_dict['id']= event.id.hex
        if event.price:
            event_dict['description']= \
                "(TICKET PRICE: %s) %s" % (event.price, 
                                           event_dict['description'])
        if event.url:
            event_dict['description']= event_dict['description'] + " For more information visit: %s" % event.url

        event_dict['recurrence']= []
        for rrule in Rrule.objects.filter(event=event):
            event_dict['recurrence'].append(rrule.formatted())
            
        event_dict['anyoneCanAddSelf'] = True
        event_dict['guestsCanInviteOthers'] = True
        event_dict['start']= {'dateTime': event.start.isoformat(), 'timeZone': event.timeZone}
        event_dict['end']= {'dateTime': event.end.isoformat(), 'timeZone': event.timeZone}
        try:
            cal_event = service.events().insert(calendarId=self.id, body=event_dict).execute()
            event.gcal_id= cal_event['id']
            event.htmlLink= cal_event['htmlLink']
            event.save()

            message = render_to_string('event_approved.txt', {'event': event,
                                                              'htmlLink': cal_event['htmlLink'],
                                                              'domain': Site.objects.get_current().domain,
                                                              'rrules': Rrule.objects.filter(event= event)
                                                              })
            send_mail("Event Approved!",
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [event.creator.email]
                      )
            return False
        except HttpError as err:
            err_json= json.loads(err.content.decode("utf-8"))
            if err_json['error']['code'] == 409:
                event.gcal_id= event.id.hex
                event.save()
                return self.update_event(event)
            print (err)
            return err_json['error']['message']
        
      
    def remove_event(self, event):
        try:
            deleted= service.events().delete(calendarId=self.id, eventId=event.gcal_id).execute()
            event.gcal_id= ""
            event.htmlLink= ""
            event.save()            
            return False
        except HttpError as err:
            return json.loads(err.content.decode("utf-8"))['error']['message']
 
    def update_event(self, event):
        event_dict= model_to_dict(event, 
                                  exclude=['creator',  'rcnotes', 'timezone', 'price', 'htmlLink',
                                           'calendar',  'recurrence', 'id', 'gcal_id' ])
        if event.price:
            event_dict['description']= \
                "(TICKET PRICE %s) %s" % (event.price,
                                          event_dict['description'])
        if event.url:
            event_dict['description']= event_dict['description'] + " For more information visit: %s" % event.url

        event_dict['recurrence']= []
        for rrule in Rrule.objects.filter(event=event):
            event_dict['recurrence'].append(rrule.formatted())

        event_dict['start']= {'dateTime': event.start.isoformat(), 'timeZone': event.timeZone}
        event_dict['end']= {'dateTime': event.end.isoformat(), 'timeZone': event.timeZone}

        if 'url' in event_dict:
            event_dict['description']= event_dict['description'] + " For more information visit: %s" % event_dict['url']
        try:
            old_event = service.events().get(calendarId=self.id, eventId=event.gcal_id).execute()
            for key in event_dict:
                old_event[key]= event_dict[key]
            updated_event = service.events().update(calendarId=self.id, eventId=event.gcal_id, body=old_event).execute()
            event.htmlLink= updated_event['htmlLink']
            event.save()
            
            message = render_to_string('event_approved.txt', {'event': event,
                                                              'htmlLink': updated_event['htmlLink'],
                                                              'domain': Site.objects.get_current().domain,
                                                              'rrules': Rrule.objects.filter(event= event)
                                                               })
            send_mail("Event Updated",
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [event.creator.email]
                      )
            return False
        except HttpError as err:
            print (err)
            return json.loads(err.content.decode("utf-8"))['error']['message']
         
    def list_events(self, time_min=datetime.datetime.utcnow(), time_max=None, time_delta=365):
        if not time_max:
            time_max = (datetime.datetime.utcnow() 
                        +datetime.timedelta(days=time_delta))
        try:
            event_json = service.events().list(calendarId=self.id, timeMin=time_min.isoformat() + 'Z', timeMax=time_max.isoformat() + 'Z',
                                           singleEvents=True, orderBy='startTime').execute()
            for event in event_json['items']:
                event['start']['dateTime']= \
                    datetime.datetime.strptime(event['start']['dateTime'][:19], '%Y-%m-%dT%H:%M:%S')
                event['end']['dateTime']= \
                    datetime.datetime.strptime(event['end']['dateTime'][:19], '%Y-%m-%dT%H:%M:%S')
            return event_json['items']
        except HttpError as err:
            print(err)
            return json.loads(err.content.decode("utf-8"))['error']['message']
            
    def refresh(self, time_delta=365):
        now = datetime.datetime.utcnow()
        time_max = datetime.datetime.utcnow()+datetime.timedelta(days=time_delta)
        event_json = service.events().list(calendarId=self.id, timeMin=now.isoformat() + 'Z', timeMax=time_max.isoformat() + 'Z',
                                       singleEvents=False).execute()
        events= event_json['items']
        for event_dict in events:
            if not Event.objects.filter(id= event_dict['id']):
                event_dict['gcal_id']= event_dict['id']
                if not valid_uuid(event_dict['id']):
                    event_dict['id']= uuid.uuid4()

                event_dict['rcnotes']= ''
                if 'recurrence' in event_dict:
                    event_dict['rcnotes']= "The following recurrence rules are in this Google Calendar event. Any changes will overwrite them.\n"
                    for rrule in event_dict['recurrence']:
                        event_dict['rcnotes']+= str(rrule) + '\n'

                event= Event.objects.create(id= event_dict['id'],
                                            gcal_id= event_dict['gcal_id'],
                                            summary= event_dict['summary'],
                                            start= datetime.datetime.strptime(event_dict['start']['dateTime'][:19], '%Y-%m-%dT%H:%M:%S'),
                                            end= datetime.datetime.strptime(event_dict['end']['dateTime'][:19], '%Y-%m-%dT%H:%M:%S'),
                                            timeZone= event_dict['start']['timeZone'],
                                            location= event_dict['location'],
                                            description= event_dict['description'],
                                            rcnotes= event_dict['rcnotes'],
                                            calendar= self
                                            )
                event.save()

    def single_refresh(self, gcal_id):
        event_dict = service.events().get(calendarId=self.id, eventId=gcal_id).execute()
        event_dict['gcal_id']= event_dict['id']
        if not valid_uuid(event_dict['id']):
            event_dict['id']= uuid.uuid4()
        
        event_dict['rcnotes']= ''
        if 'recurrence' in event_dict:
            event_dict['rcnotes']= "The following recurrence rules are in this Google Calendar event. Any changes will overwrite them.\n"
            for rrule in event_dict['recurrence']:
                event_dict['rcnotes']+= str(rrule) + '\n'
        try:
            event = Event.objects.get(id= event_dict['id'])
            event.gcal_id= event_dict['gcal_id']
            event.summary= event_dict['summary']
            event.start= datetime.datetime.strptime(event_dict['start']['dateTime'][:19], '%Y-%m-%dT%H:%M:%S')
            event.end= datetime.datetime.strptime(event_dict['end']['dateTime'][:19], '%Y-%m-%dT%H:%M:%S')
            event.timeZone= event_dict['start']['timeZone']
            event.location= event_dict['location']
            event.description= event_dict['description']
            event.rcnotes= event_dict['rcnotes']
            event.htmlLink= event_dict['htmlLink']
            event.calendar= self
            event.save()
        except ObjectDoesNotExist:
            event= Event.objects.create(id= event_dict['id'],
                                        gcal_id= event_dict['gcal_id'],
                                        summary= event_dict['summary'],
                                        start= datetime.datetime.strptime(event_dict['start']['dateTime'][:19], '%Y-%m-%dT%H:%M:%S'),
                                        end= datetime.datetime.strptime(event_dict['end']['dateTime'][:19], '%Y-%m-%dT%H:%M:%S'),
                                        timeZone= event_dict['start']['timeZone'],
                                        location= event_dict['location'],
                                        description= event_dict['description'],
                                        rcnotes= event_dict['rcnotes'],
                                        htmlLink= event_dict['htmlLink'],
                                        calendar= self
                                        )
        return event

class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscribed_calendars= JSONField(null=True) 

    def get_absolute_url(self):
        return '/event/profile/%s'% self.id          

class Newsletter(models.Model):
    last= models.DateField(blank= True, null=True)
    next= models.DateField(blank= True, null=True)
    email_header= models.TextField(blank=True)

    def send_newsletter(self):
        calendars_events = {calendar.summary:calendar.list_events(time_delta=45)
                            for calendar in Calendar.objects.all()}

        for profile in Profile.objects.all().iterator():
            try:
                subscribed_calendars= {calendar:subscribed 
                                       for calendar, subscribed in profile.subscribed_calendars.items() 
                                       if subscribed}
            except AttributeError:
                print("Profile for %s is not set up correctly." % profile.user.email)
                continue

            if not subscribed_calendars:
                continue
            
            message_events = {calendar_summary:calendars_events[calendar_summary]
                              for calendar_summary in subscribed_calendars
                              if calendar_summary in calendars_events}

            message = render_to_string('newsletter.txt', {'intro': self.email_header,
                                                          'events_dict': message_events,
                                                          'id': profile.id,
                                                          'domain': Site.objects.get_current().domain,
                                                          })
            
            send_mail(Site.objects.get_current().name + " " + datetime.date.today().isoformat() + " Newsletter",
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [profile.user.email]
                      )

        self.last= datetime.date.today()
        self.next= datetime.date.today() + (datetime.timedelta(days=30))
        self.save()

class Blog(models.Model):
    class Meta:
        ordering = ['-date']
    date= models.DateField()
    entry= models.TextField()

