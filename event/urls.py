from django.conf.urls import url
from event import views

urlpatterns = [
    url(r'^$', views.EventListView.as_view(template_name="event_list.html"), name='event_list'),
    url(r"^create/$", views.create_event, name="create_event"),
    url(r'^(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.EventDetailView.as_view(template_name="event_detail.html"), name="show_event"),
    url(r"^approve/$", views.rc_approve_view, name="RCapprove"),
    url(r"^calendar/(?P<order>\d+)$", views.calendar_detail_view, name="calendar"),
    url(r'^profile/(?P<profile_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$', views.profile_view, name="profile_without_login"),
    url(r"^profile/", views.profile_view, name="profile"),
    url(r"^newsletter/", views.newsletter_view, name="newsletter"),
]