import re
from django import forms
from django.utils.translation import ugettext_lazy as _
import account.forms
from account.models import EmailAddress
from datetimewidget.widgets import DateTimeWidget
from event import models, mixins


alnum_re = re.compile(r"^\w+$")

class SignupForm(forms.Form):

    email = forms.EmailField(
        label=_("Email"),
        widget=forms.TextInput(), required=True)
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(render_value=False)
    )
    password_confirm = forms.CharField(
        label=_("Password (again)"),
        widget=forms.PasswordInput(render_value=False)
    )
    code = forms.CharField(
        max_length=64,
        required=False,
        widget=forms.HiddenInput()
    )

    def clean_email(self):
        value = self.cleaned_data["email"]
        qs = EmailAddress.objects.filter(email__iexact=value)
        if not qs.exists():
            return value
        raise forms.ValidationError(_("A user is registered with this email address."))

    def clean(self):
        if "password" in self.cleaned_data and "password_confirm" in self.cleaned_data:
            if self.cleaned_data["password"] != self.cleaned_data["password_confirm"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data

class EventForm(forms.ModelForm):
    class Meta:
        model= models.Event
        exclude = ['owner','approved', 'recurrence', 'rrule']
        widgets = {
            'start': DateTimeWidget(usel10n = True, 
                                   bootstrap_version=3, 
                                   options = {'format': 'dd/mm/yyyy HH:ii P',
                                              'showMeridian': True,
                                              'minuteStep': 15,
                                              'pickerPosition': 'bottom-left'
                                             }
                                   ),
            'end': DateTimeWidget(usel10n = True, 
                                   bootstrap_version=3, 
                                   options = {'format': 'dd/mm/yyyy HH:ii P',
                                              'showMeridian': True,
                                              'minuteStep': 15,
                                              'pickerPosition': 'bottom-left'
                                             }
                                   )
        }

    def clean(self):
        cleaned_data = super().clean()
        if 'end' in cleaned_data and 'start' in cleaned_data and \
          cleaned_data['end'] < cleaned_data['start']:
            raise forms.ValidationError("Events must end after they begin.")
        return cleaned_data

RCEventFormSet = forms.modelformset_factory(models.Event, 
                                            fields=('__all__'), 
                                            extra=0,
                                            can_delete=True)

