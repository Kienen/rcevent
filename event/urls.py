from django.conf.urls import url
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import TemplateView
from event import views

urlpatterns = [
    #Event creation
    url(r"^create/$", views.EventCreateView.as_view(), name="create_event"),
    url(r"^admin/create/$", views.EventCreateView.as_view(auto_approve= True), name="admin_add_event"),
    
    #Event Updates    
    url(r"^update/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$", views.EventUpdateView.as_view(), name="update_event"),
    url(r"^admin/update/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$", views.EventUpdateView.as_view(auto_approve= True), name="admin_update_event"),
    
    #RRULES
    url(r"^create/reccurring/(?P<event_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$", views.edit_reccurence, name="recurrence"),
    url(r"^deleterecurrence/(?P<event_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<rrule_id>\d+)$", views.delete_recurrence, name='delete_recurrence'),
    
    #Event Details
    url(r'^(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.EventDetailView.as_view(template_name="event_detail.html"), name="show_event"),

    #Event Deletion
    url(r"^delete/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$", views.EventDeleteView.as_view(), name="delete_event"),
    url(r"^unapprove/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$", views.calendar_remove_event, name="remove_event"),

    #Approval
    url(r"^approve/$", views.UnapprovedEventsView.as_view(), name="unapproved"),
    url(r"^newsletter/", views.newsletter_view, name="newsletter"),
]