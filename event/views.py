from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from account import forms, views
from event.forms import *


# Create your views here.
class LoginView(views.LoginView):
    form_class = account.forms.LoginEmailForm


class SignupView(views.SignupView):
    form_class = SignupForm

    def generate_username(self, form):
        username = form['email'].value()[0:29].lower()
        username = ''.join([x for x in username if x not in "!#$%&'*+-/=?^_`{|}~}"])
        i=0
        while User.objects.filter(username=username):
            if i < 10:
                username=str(i) + username[1:]
            else:
                username=str(i) + username[2:]
            i+=1
        return username   

@login_required(login_url='/account/login/')
def create_event(request):
    if request.method == 'POST':
        form = EventForm(data=request.POST)
    else:
        form = EventForm()
    if form.is_valid():
        event_ = form.save(commit=False)
        event_.owner = request.user
        event_.save()
        return redirect(event_)
    return render(request, 'event_create.html', {'form': form})

class EventDetailView(DetailView):
    model= Event
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        return context    

class EventListView(ListView):
    model= Event
    context_object_name = 'event_list'

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        return context 

