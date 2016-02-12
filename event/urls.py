from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from event import views

urlpatterns = [
    url(r"^create/", views.create_event(), name="create_event"),
]