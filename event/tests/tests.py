from django.core.urlresolvers import resolve
from django.test import TestCase
from event.views import create_event

class HomePageTest(TestCase):

    def test_url_resolves_to_event_create_view(self):
        found = resolve('/event/create/') 
        self.assertEqual(found.func, create_event)