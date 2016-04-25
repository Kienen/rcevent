import datetime
from django.core.management.base import BaseCommand, CommandError
from event.models import Newsletter


class Command(BaseCommand):
    help = "Checks to see if it is time to send the newsletter and sends it if so."

    def handle(self, *args, **options):
        newsletter = Newsletter.objects.first()
        
        if not newsletter:
            raise CommandError("Newsletter object not found.")
        elif newsletter.last and newsletter.last + datetime.timedelta(days=7) > datetime.date.today():
            self.stdout.write('Not sending the newsletter because it was sent %s days ago' %
                              (datetime.date.today() - newsletter.last).days)
        elif datetime.date.today() < newsletter.next:
            self.stdout.write('The next newsletter is scheduled on %s' % newsletter.next)
        else:
            newsletter.send_newsletter()
            self.stdout.write('Sent the newsletter on %s' % datetime.date.today())
