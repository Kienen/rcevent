from django.core.urlresolvers import resolve, reverse
from django.test import TestCase
from django.http import HttpRequest
from event import views, models
from django.contrib.auth.models import User
from unittest import skip


class CreateEventTest(TestCase):

    def test_url_resolves_to_event_create_view(self):
        found = resolve('/event/create/') 
        self.assertEqual(found.func, views.create_event)

    def test_create_view_requires_login(self):
        response = self.client.get('/event/create/')
        self.assertRedirects(response, expected_url='/account/login/?next=/event/create/', fetch_redirect_response=False)

    @skip
    def test_event_create_view_saves_owner(self):
        request = HttpRequest()
        request.user, created = User.objects.get_or_create(email='burner@burner.me',
                                                           defaults={'username': 'burner@burner.me',
                                                                     'password': 'burnerpass'})
        
        request.POST['summary']="Big Party"
        request.POST['start']= '2016-10-25 14:30:59'
        request.POST['end']= '2016-10-25 14:30:59'
        request.POST['location']= 'My House'
        request.POST['description']= "Party Party"
        request.POST['category']= '2hbus9o0mmnt8rhodedbhiq5n8@group.calendar.google.com'
        request.method = "POST"
        views.create_event(request)
        event_ = models.Event.objects.get(summary= "Big Party")
        self.assertEqual(event_.owner, request.user)

      