from django.conf.urls import url
from event import views

urlpatterns = [
    url(r"^create/", views.create_event, name="create_event"),

]