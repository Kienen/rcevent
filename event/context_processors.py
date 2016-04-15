import datetime
from event.models import Calendar

def sidebar(request):
    ctx = {
        "today": datetime.date.today(),
        "calendars": Calendar.objects.all()
    }
    return ctx