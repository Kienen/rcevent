from django.conf.urls import url
from event import views
urlpatterns = [
    url(r'^$', views.EventListView.as_view(template_name="event_list.html"), name='event_list'),
    url(r"^create/", views.create_event, name="create_event"),
    url(r'^(?P<pk>\d+)/$', views.EventDetailView.as_view(template_name="event_detail.html"), name="show_event"),
    url(r"^approve/", views.rc_approve_view, name="RCapprove"),
    url(r"^calendar/", views.calendar_view, name="calendar"),
]