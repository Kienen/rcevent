from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Event(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length=100)
    date  = models.DateTimeField()
    location = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        ordering = ['date']

    def get_absolute_url(self):
        return '/event/%s'% self.id