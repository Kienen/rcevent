from django.conf.urls import url
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
    
    #Event Details()
    url(r'^(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.EventDetailView.as_view(template_name="event_detail.html"), name="show_event"),
    url(r'^(?P<gcal_id>\w+)/$', views.gcal_id_redirect, name="gcal_show_event"),
    url(r'^(?P<calendar_id>[^@]+@group.calendar.google.com+)/(?P<gcal_id>\w+)/$', views.gcal_id_redirect, name="calendar_gcal_show_event"),

    #Event Deletion
    url(r"^delete/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$", views.EventDeleteView.as_view(), name="delete_event"),
    url(r"^unapprove/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$", views.calendar_remove_event, name="remove_event"),

    #Staff views
    url(r"^approve/$", views.UnapprovedEventsView.as_view(), name="unapproved"),
    url(r"^all/$", views.AllEventListView.as_view(), name="all_events"),
]