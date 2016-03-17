from django.test import TestCase
from django.contrib.auth.models import User
from event import models

class EventModelTest(TestCase):

    def test_event_is_related_to_promoter(self):
        promoter = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        event_ = models.Event(
            owner=promoter, 
            summary= 'Test Event Please Ignore', 
            start= '2006-10-25 14:30:59', 
            end= '2006-10-25 15:30:59',
            location = "My House", 
            description = "Big Shindig",
        )
        event_.category_id = "jieqlbpa8d8c06vlgo4iu0jpok@group.calendar.google.com"

        event_.save()
        self.assertEqual(event_.owner, promoter)
   


