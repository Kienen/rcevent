from django.conf.urls import url
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import TemplateView
from event import views

urlpatterns = [
    url(r"^create/$", views.CreateEvent.as_view(), name="create_event"),
    url(r"^update/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$", views.UpdateEvent.as_view(), name="update_event"),
    url(r"^admin/create/$", views.CreateEvent.as_view(auto_approve= True), name="admin_create_event"),
    url(r"^admin/update/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$", views.UpdateEvent.as_view(auto_approve= True), name="admin_update_event"),
    url(r"^create/reccurring/(?P<event_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$", views.edit_reccurence, name="recurrence"),
    url(r"^deleterecurrence/(?P<event_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<rrule_id>\d+)$", views.delete_recurrence, name='delete_recurrence'),
    url(r'^(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.EventDetailView.as_view(template_name="event_detail.html"), name="show_event"),
    url(r"^approve/$", views.UnapprovedEvents.as_view(template_name="unapproved_events.html"), name="unapproved"),
    url(r"^calendar/(?P<order>\d+)$", views.calendar_detail_view, name="calendar"),
    url(r'^profile/(?P<profile_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$', views.profile_view, name="profile_without_login"),
    url(r"^profile/", views.profile_view, name="profile"),
    url(r"^newsletter/", views.newsletter_view, name="newsletter"),
]