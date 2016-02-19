from django.conf.urls import url
from event.views import *

urlpatterns = [
    url(r'^$', EventListView.as_view(template_name="event_list.html"), name='event_list'),
    url(r"^create/", create_event, name="create_event"),
    url(r'^(?P<pk>\d+)/$', EventDetailView.as_view(template_name="event_detail.html"), name="show_event"),
    url(r"^approve/", rc_approve_view, name="RCapprove"),
]