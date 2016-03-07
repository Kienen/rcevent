from django.db.models.signals import post_save 
from django.dispatch import receiver
from event.models import Event
#from event import calendar

# @receiver(post_save, sender=Event)
# def saved_event(sender, **kwargs):
#     event= kwargs['instance']
#     cal = event.category

#     if event.approved:
#         cal.add_event(event)

