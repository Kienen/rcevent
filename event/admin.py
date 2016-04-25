from django.contrib import admin
from event.models import *

# Register your models here.
class NewsletterAdmin(admin.ModelAdmin):
  def has_add_permission(self, request):
    num_objects = self.model.objects.count()
    if num_objects >= 1:
      return False
    else:
      return True

admin.site.register(Event)
admin.site.register(Calendar)
admin.site.register(Newsletter, NewsletterAdmin)
admin.site.register(Rrule)
admin.site.register(Profile)

