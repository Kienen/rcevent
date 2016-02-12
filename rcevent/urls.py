from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rcevent.views import *

from django.contrib import admin


urlpatterns = [
    url(r"^$", TemplateView.as_view(template_name="homepage.html"), name="home"),
    url(r"^admin/", include(admin.site.urls)),

    #Email Account Views
    url(r"^account/login/", LoginView.as_view(template_name='account/login.html'), name="login"),
    url(r"^account/signup/", SignupView.as_view(template_name='account/signup.html'), name="signup"),
    url(r"^account/", include("account.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
