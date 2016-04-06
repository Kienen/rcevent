import re
import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _
import account.forms
from account.models import EmailAddress
from datetimewidget.widgets import DateTimeWidget, DateWidget
from event import models, mixins

DAYS = [
    ('SU', 'Every Sunday'),
    ('MO', 'Every Monday'),
    ('TU', 'Every Tuesday'),
    ('WE', 'Every Wednesday'),
    ('TH', 'Every Thursday'),
    ('FR', 'Every Friday'),
    ('SA', 'Every Saturday'),
    ('1SU', 'The First Sunday of the month'),
    ('1MO', 'The First Monday of the month'),
    ('1TU', 'The First Tuesday of the month'),
    ('1WE', 'The First Wednesday of the month'),
    ('1TH', 'The First Thursday of the month'),
    ('1FR', 'The First Friday of the month'),
    ('1SA', 'The First Saturday of the month'),
    ('2SU', 'The Second Sunday of the month'),
    ('2MO', 'The Second Monday of the month'),
    ('2TU', 'The Second Tuesday of the month'),
    ('2WE', 'The Second Wednesday of the month'),
    ('2TH', 'The Second Thursday of the month'),
    ('2FR', 'The Second Friday of the month'),
    ('2SA', 'The Second Saturday of the month'),
    ('3SU', 'The Third Sunday of the month'),
    ('3MO', 'The Third Monday of the month'),
    ('3TU', 'The Third Tuesday of the month'),
    ('3WE', 'The Third Wednesday of the month'),
    ('3TH', 'The Third Thursday of the month'),
    ('3FR', 'The Third Friday of the month'),
    ('3SA', 'The Third Saturday of the month'),
    ('4SU', 'The Fourth Sunday of the month'),
    ('4MO', 'The Fourth Monday of the month'),
    ('4TU', 'The Fourth Tuesday of the month'),
    ('4WE', 'The Fourth Wednesday of the month'),
    ('4TH', 'The Fourth Thursday of the month'),
    ('4FR', 'The Fourth Friday of the month'),
    ('4SA', 'The Fourth Saturday of the month'),
    ('5SU', 'The Fifth Sunday of the month'),
    ('5MO', 'The Fifth Monday of the month'),
    ('5TU', 'The Fifth Tuesday of the month'),
    ('5WE', 'The Fifth Wednesday of the month'),
    ('5TH', 'The Fifth Thursday of the month'),
    ('5FR', 'The Fifth Friday of the month'),
    ('5SA', 'The Fifth Saturday of the month'),
]

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
        exclude = ['owner','approved']
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
                                   ),
            'rrule_until': DateWidget(usel10n = True, 
                                   bootstrap_version=3, 
                                   options = {'format': 'dd/mm/yyyy',
                                              'pickerPosition': 'bottom-left'
                                             }
                                   ),
            'rrule_byday': forms.CheckboxSelectMultiple(choices=DAYS)
        }

    def clean(self):
        cleaned_data = super().clean()
        if 'end' in cleaned_data and 'start' in cleaned_data and \
            cleaned_data['end'] < cleaned_data['start']:
                raise forms.ValidationError("Events must end after they begin.")
        return cleaned_data

    def clean_rrule_freq(self):
        if self.cleaned_data['recurrence']:
            if self.cleaned_data['rrule_freq'] == '':
                raise forms.ValidationError("How often is this recurring event?")

        if 'rrule_freq' not in self.cleaned_data:
          data = ''
        else:
          data = self.cleaned_data['rrule_freq']

        return data


    def clean_rrule_until(self):
        data = self.cleaned_data['rrule_until']
        if self.cleaned_data['recurrence']:
            if data == None:
              data = datetime.date.today()+datetime.timedelta(days=365)
        return data

    def clean_rrule_byday(self):
        data = self.cleaned_data['rrule_byday']
        check_data = data.replace('[','').replace(']','').replace(' ','').replace("'","")
        data_list= check_data.split(',')
        
        if self.cleaned_data['recurrence'] and self.cleaned_data['rrule_freq']=='MONTHLY':
            for value in data_list:
              if len(value) == 2:
                raise forms.ValidationError("If the event is monthly, it cannot be every week.")

        return data

class ProfileForm(forms.Form):
    def __init__(self, *args, **kwargs):
        calendars = kwargs.pop('calendars')
        subscribed_calendars = kwargs.pop('subscribed_calendars')
        super().__init__(*args, **kwargs)

        for calendar in calendars:
            if calendar.summary in subscribed_calendars and subscribed_calendars[calendar.summary]:
                self.fields[calendar.summary] = forms.BooleanField(label=calendar.summary, required=False, initial=True)
            else:
                self.fields[calendar.summary] = forms.BooleanField(label=calendar.summary, required=False)
                        


# class RecurrenceForm:
#   class Meta:
#         model= models.Event
#         fields= ['rrule_freq', 'rrule_until', 'rrule_byday']
#         widgets = {
#             'rrule_until': DateTime(usel10n = True, 
#                                    bootstrap_version=3, 
#                                    options = {'format': 'dd/mm/yyyy',
#                                               'pickerPosition': 'bottom-left'
#                                              }
#                                    ),}

RCEventFormSet = forms.modelformset_factory(models.Event, 
                                            fields=('__all__'), 
                                            extra=0,
                                            can_delete=True)

