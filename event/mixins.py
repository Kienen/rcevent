from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import auth, messages

class StaffViewMixin(UserPassesTestMixin):
    permission_denied_message= "This page is restricted to site moderators"

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        messages.add_message(self.request, messages.ERROR, self.permission_denied_message)
        if self.request.user.is_authenticated():
            auth.logout(self.request)
        return super().handle_no_permission()        

class ReadOnlyFieldsMixin(object):
    readonly_fields =()

    def __init__(self, *args, **kwargs):
        super(ReadOnlyFieldsMixin, self).__init__(*args, **kwargs)
        for field in (field for name, field in self.fields.iteritems() if name in self.readonly_fields):
            field.widget.attrs['disabled'] = 'true'
            field.required = False
            
        for field in (field for name, field in self.fields.iteritems()):
            field.required = False

    def clean(self):
        cleaned_data = super(ReadOnlyFieldsMixin,self).clean()
        for field in self.readonly_fields:
           cleaned_data[field] = getattr(self.instance, field)

        return cleaned_data        