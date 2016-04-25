import datetime
from django.core.management.base import BaseCommand
from event.models import Event

class Command(BaseCommand):
    help = "Checks to see if it is time to send the newsletter and sends it if so."

    def handle(self, *args, **options):
        events= Event.objects.filter(start__lt= datetime.date.today(), rrule__isnull= True)
        
        for event in events:
            print ("Deleted %s %s" % (event.start.strftime("%m/%d/%Y"), event.summary))
            event.delete()

