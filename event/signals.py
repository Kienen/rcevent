import json
from django.core import serializers
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from event.models import Event
from event import calendar



@receiver(post_save, sender=Event)
def saved_event(sender, **kwargs):
    cal = calendar.GoogleCalendar()

    event= kwargs['instance']
    if event.approved:
        cal.add_event(event)

