from django.db.models.signals import post_save
from django.core.signals import request_finished
from django.dispatch import receiver
from event.models import Event

@receiver(post_save, sender=Event)
def saved_event(sender, **kwargs):
    for key, value in kwargs.items():
        print( "%s = %s" % (key, value))
    print (kwargs['instance'].approved)

# @receiver(request_finished)
# def my_callback(sender, **kwargs):
#     print("Request finished!")