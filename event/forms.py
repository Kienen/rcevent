from django import forms
import account.forms
import re
from account.models import EmailAddress
from django.utils.translation import ugettext_lazy as _
from event.models import *

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
        model= Event
        exclude = ['owner']