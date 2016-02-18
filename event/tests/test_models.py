from django.test import TestCase
from django.contrib.auth.models import User
from event.models import *

class EventModelTest(TestCase):

    def test_event_is_related_to_promoter(self):
        promoter = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        event_ = Event(
            owner=promoter, 
            title= 'Test Event Please Ignore', 
            date= '2006-10-25 14:30:59', 
            location = "My House", 
            description = "Big Shindig",
            )

        event_.save()
        self.assertEqual(event_.owner, promoter)
   


