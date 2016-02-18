from django.core.urlresolvers import resolve, reverse
from django.test import TestCase
from event.views import *
from django.http import HttpRequest
import datetime


class HomePageTest(TestCase):

    def test_url_resolves_to_event_create_view(self):
        found = resolve('/event/create/') 
        self.assertEqual(found.func, create_event)

    # def test_create_view_returns_correct_template(self):
    #     response = self.client.get('/event/create/')
    #     self.assertTemplateUsed(response, 'event_create.html')

    def test_create_view_requires_login(self):
        response = self.client.get('/event/create/')
        self.assertRedirects(response, expected_url='/account/login/?next=/event/create/', fetch_redirect_response=False)

    def test_event_create_view_saves_owner(self):
        request = HttpRequest()
        request.user, created = User.objects.get_or_create(email='burner@burner.me',
                                                           defaults={'username': 'burner@burner.me',
                                                                     'password': 'burnerpass'})
        
        request.POST['title']="Big Party"
        request.POST['date']= '2006-10-25 14:30:59'
        request.POST['location']= 'My House'
        request.POST['description']= "Big Party"
        create_event(request)
        event_ = Event.objects.get(title= "Big Party")
        self.assertEqual(event_.owner, request.user)

      