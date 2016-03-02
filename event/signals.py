from django.db.models.signals import post_save
#from django.core.signals import request_finished
from django.dispatch import receiver
from django.core import serializers
from django.forms.models import model_to_dict
import json
from event.models import Event
from event import calendar



@receiver(post_save, sender=Event)
def saved_event(sender, **kwargs):
    for key, value in kwargs.items():
        print( "%s = %s" % (key, value))
    print (kwargs['instance'].title)

    event= kwargs['instance']
    if True: #event.approved:
        calendar.add_event(event)

