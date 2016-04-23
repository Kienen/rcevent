import re
import datetime
from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.forms.utils import flatatt, to_current_timezone
from django.utils.translation import ugettext_lazy as _
import account.forms
from account.models import EmailAddress
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

class SplitDateTimeWidget(forms.widgets.MultiWidget):
    def __init__(self, attrs={'class': 'time'}, date_format=None, time_format='%I:%M%p'):
        widgets = (forms.widgets.DateInput(attrs={'class': 'date'}, format=date_format),
                   forms.widgets.TimeInput(attrs={'class': 'time'}, format=time_format))
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            value = to_current_timezone(value)
            return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]  

    def format_output(self, rendered_widgets):
        rendered_widgets[0]= str.replace(rendered_widgets[0],'time', 'date')
        output= "<div class='form-inline'>\n" + ' '.join(rendered_widgets) + "</div>"
        return output

class EventForm(forms.ModelForm):
    class Meta:
        model= models.Event
        exclude = ['creator']
    start= forms.SplitDateTimeField(widget=SplitDateTimeWidget() )
    end= forms.SplitDateTimeField(widget=SplitDateTimeWidget())
    url= forms.URLField(required= False,
                        label="Website", 
                        help_text= "Input a website to buy tickets or find more information, or just leave blank.<b>i.e. http://www.burningman.org") 
    price= forms.CharField(required= False,
                           help_text="i.e. '$5', 'Suggested Donation $5', 'Bring a canned item to donate', etc")                                       
    rcnotes= forms.CharField(required= False,
                             widget=forms.widgets.Textarea(), 
                             label="Admin Notes", 
                             help_text= "This information will not show on the website and is intended to help site admins understand why this event is relevant to the community.")

    def clean(self):
        cleaned_data = super().clean()
        if 'end' in cleaned_data and 'start' in cleaned_data and \
            cleaned_data['end'] < cleaned_data['start']:
                raise forms.ValidationError("Events must end after they begin.")
        return cleaned_data

    def clean_start(self):
        data = self.cleaned_data['start']
        print (data)
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
                        
class RecurrenceForm(forms.Form):
    freq= forms.ChoiceField(label= "Frequency",
                            choices= [(None, '-------'),
                                      ('WEEKLY','Every Week'),
                                      ('MONTHLY','Every Month')],
                            required= False)
    until= forms.DateField(required= False, 
                           label="This event will continue until this date", 
                           help_text="Please choose either an end date or a number of times to repeat")
    count= forms.IntegerField(min_value= 2, 
                              required= False,
                              label="This event will occur this number of times", 
                              help_text="Please choose either an end date or a number of times to repeat")
    byday= forms.MultipleChoiceField(choices= DAYS, 
                                     widget= forms.CheckboxSelectMultiple(),
                                     required= False,
                                     label= "Recur on certain day(s) of the week")
    rdate= forms.DateField(required= False,
                           label= "Additional Recurrence",
                           help_text= "Please submit the base recurrence rule first. Add additional days in another rule.")
    exdate= forms.DateField(required= False,
                            label= "Exception (The event will not occur on this day)",
                            help_text= "Please submit the base recurrence rule first. Add exceptions in another rule.")                               

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data)
        if cleaned_data['freq']:
            if cleaned_data['rdate']:
                msg= "Please create the base recurrence rule first. Add additional days in another rule."
                self.add_error('freq', msg)
                self.add_error('rdate', msg)
                raise forms.ValidationError(msg)

            if cleaned_data['exdate']:
                msg= "Please create the base recurrence rule first. Add exceptions in another rule."
                self.add_error('freq', msg)
                self.add_error('exdate', msg)
                raise forms.ValidationError("Please create the base recurrence rule first. Add exceptions in another rule.")                    

            if (cleaned_data['until'] and cleaned_data['count']) or \
               (not cleaned_data['until'] and not cleaned_data['count']):
                    msg= ("Please choose either an end date or a number of times to repeat")
                    self.add_error('until', msg)
                    self.add_error('count', msg)
                    return cleaned_data

        return cleaned_data


class SiteForm(forms.ModelForm):
    class Meta:
        model= models.Newsletter
        fields= '__all__'

    last= forms.DateField(required= False, 
                          disabled= True, 
                          help_text= "The last day the newsletter was sent.")
    next= forms.DateField(required= False, 
                          help_text= "The next day to send the newsletter.")
    email_header= forms.CharField(required= False,
                                  widget=forms.widgets.Textarea(), 
                                  label="Email Intro", 
                                  help_text= "This will be included in each email.")
    domain= forms.CharField(required= False, help_text= "i.e. example.mysite.com")
    name= forms.CharField(required= False)

