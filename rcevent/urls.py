from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView
from event import views

from django.contrib import admin


urlpatterns = [
    url(r"^$", TemplateView.as_view(template_name="homepage.html"), name="home"),
    url(r"^admin/", include(admin.site.urls)),

    #Email Account Views
    url(r"^account/login/", views.LoginView.as_view(template_name='account/login.html'), name="login"),
    url(r"^account/signup/", views.SignupView.as_view(template_name='account/signup.html'), name="signup"),
    url(r"^account/", include("account.urls")),

    url(r"^event/create/", views.create_event, name="create_event"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
