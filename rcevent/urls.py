from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from event import views
from event import urls as event_urls
from django.conf.urls.static import static

urlpatterns = [
    #Public Views
    url(r"^$", views.HomepageView.as_view(), name="home"),
    url(r"^calendar/(?P<order>\d+)$", views.calendar_detail_view, name="calendar"),
    url(r"^search/$", views.SearchEventsView.as_view(), name="search"),

    #Account Views
    url(r"^account/login/", views.LoginView.as_view(template_name='account/login.html'), name="login"),
    url(r"^account/signup/", views.SignupView.as_view(template_name='account/signup.html'), name="signup"),
    url(r'^account/profile/(?P<profile_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$', views.profile_view, name="profile_without_login"),
    url(r"^account/profile/", views.profile_view, name="profile"),
    url(r"^account/events/", views.MyEventsView.as_view(), name="my_events"),
    url(r"^account/", include("account.urls")),

    #Event URLS
    url(r"^event/", include(event_urls)),

    #Calendar Management
    url(r"^calendar/$", views.CalendarListView.as_view(), name="calendar_list"),
    url(r"^calendar/create/$", views.CalendarCreateView.as_view(), name="calendar_create"),
    url(r"^calendar/create/(?P<pk>[^@]+@group.calendar.google.com+)$", views.CalendarCreateView.as_view(), name="calendar_make_public"),
    url(r"^calendar/update/(?P<pk>[^@]+@group.calendar.google.com+)$", views.CalendarUpdateView.as_view(), name="calendar_update"),
    url(r"^calendar/delete/(?P<pk>[^@]+@group.calendar.google.com+)$", views.delete_calendar, name="calendar_delete"),
    url(r"^calendar/events/(?P<pk>[^@]+@group.calendar.google.com+)$", views.CalendarEventListView.as_view(), name="event_list"),
    url(r"^calendar/refresh/$", views.calendar_refresh, name="refresh"),

    #Admin
    url(r"^admin/", include(admin.site.urls)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
