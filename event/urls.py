from django.conf.urls import url
from event import views

urlpatterns = [
    url(r"^create/", views.create_event, name="create_event"),
    url(r'^(?P<pk>\d+)/$', views.EventDetailView.as_view(template_name="event_detail.html"), name="show_event"),
]