import datetime
from event.models import Calendar


def sidebar(request):
    ctx = {
        "today": datetime.date.today().strftime('%m-%d-%Y'),
        "calendars": Calendar.objects.all()
        
    }
    return ctx