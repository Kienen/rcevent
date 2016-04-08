import datetime
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from account import forms as auth_forms, views as auth_views
from event import forms, models
from .mixins import StaffViewMixin


# Create your views here.
class LoginView(auth_views.LoginView):
    form_class = auth_forms.LoginEmailForm


class SignupView(auth_views.SignupView):
    form_class = forms.SignupForm

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

class HomepageView(TemplateView):
    template_name = "homepage.html"  

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            try: 
                profile_exists= request.user.profile.subscribed_calendars
            except:
                return redirect('profile')

        return super().get(request, *args, **kwargs)     

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calendars']= models.Calendar.objects.all()
        return context

class UnapprovedEvents(StaffViewMixin, TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events']= models.Event.objects.filter(approved=False)
        return context

class CreateEvent(CreateView):
    model = models.Event
    form_class= forms.EventForm
    auto_approve= False
    admin_url= "admin_create_event"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form): 
        form.cleaned_data['rcnotes']= "Created by %s\n" % self.request.user.email + form.cleaned_data['rcnotes']
        
        if self.auto_approve and self.request.user.is_staff:
            self.object = form.save()
            self.object.approved = True
            messages.add_message(self.request, messages.SUCCESS, "Event saved and added to calendar.")
            return redirect(self.get_success_url())
        else:
            messages.add_message(self.request, messages.SUCCESS, 
                                 "Event created! It will be added to the calendar after approval by site moderators.")   
        return super().form_valid(form)  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['admin_url']= self.admin_url
        return context              

class UpdateEvent(UpdateView):
    model = models.Event
    form_class= forms.EventForm
    auto_approve= False
    admin_url= "admin_update_event"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form): 
        form.cleaned_data['rcnotes']= "Updated by %s\n" % self.request.user.email + form.cleaned_data['rcnotes']
        if self.auto_approve and self.request.user.is_staff:
            self.object = form.save()
            self.object.approved = True
            messages.add_message(self.request, messages.SUCCESS, "Event updated and added to calendar.")
            return redirect(self.get_success_url())
        else:
            messages.add_message(self.request, messages.SUCCESS, 
                                 "Event updated! It will be added to the calendar after approval by site moderators.")   
        return super().form_valid(form)     

# @login_required(login_url='/account/login/')
# def create_event(request, event_id=None, auto_approve= False):
#     if event_id:
#         event= models.Event.objects.get(id= event_id)
#         form= forms.EventForm(instance= event)
#     else:
#         form = forms.EventForm()

#     if request.method == 'POST':
#         if event:
#             form= forms.EventForm(data=request.POST, instance= event)
#         else:
#             form = forms.EventForm(data=request.POST)
#         if form.is_valid():
#             event = form.save(commit=False)
#             if event.recurring:
#                 event.save()
#                 return redirect ("recurrence", event=event.id)
#             if auto_approve:
#                 event.approved = True
#                 messages.add_message(request, messages.SUCCESS, "Event saved and added to calendar.")
#             else:
#                 messages.add_message(request, messages.SUCCESS, "Event created! It will be added to the calendar after approval by site moderators.")
#             event.save()
#             return redirect(event)
#     return render(request, 'event_create.html', {'form': form})

# @user_passes_test(lambda u: u.is_staff, login_url='/account/login/')
# def admin_update(request, event_id= None):


@login_required(login_url='/account/login/')
def edit_reccurence(request, event_id):
    if request.method == 'POST':
        form = forms.RecurrenceForm(data=request.POST)
    else:
        form = forms.RecurrenceForm()
    if form.is_valid():
        event= models.Event.objects.get(pk=event_id)
        rrule= models.Rrule.objects.create(event= event,
                                           freq= form.cleaned_data['freq'],
                                           until= form.cleaned_data['until'],
                                           byday= form.cleaned_data['byday'],
                                           count= form.cleaned_data['count'],
                                           rdate= form.cleaned_data['rdate'],
                                           exdate= form.cleaned_data['exdate'])
        return redirect(event)
    return render(request, 'recurrence.html', {'form': form})

@login_required(login_url='/account/login/')
def delete_recurrence(request, event_id, rrule_id): 
    event= models.Event.objects.get(pk=event_id)
    rrule= models.Rrule.objects.get(id=rrule_id).delete()
    return redirect(event)

class EventDetailView(DetailView):
    model= models.Event
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rrules']= models.Rrule.objects.filter(event= context['event'])
        return context    

# class EventListView(ListView):
#     model= models.Event
#     context_object_name = 'event_list'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return context 

#     def get_queryset(self):
#         return models.Event.objects.filter(approved= True)
     

# @user_passes_test(lambda u: u.is_staff, login_url='/account/login/')
# def rc_approve_view(request):

    # q=models.Event.objects.filter(approved=False)
    # if request.method == "POST":
    #     formset= forms.RCEventFormSet(request.POST, instance=q)
    #     if formset.is_valid():
    #         formset.save()
    #     return redirect('event_list')
    # else:
    #    formset= forms.RCEventFormSet(queryset=q)
    # return render(request, 'RCevent_approve.html', {'formset': formset})

def calendar_detail_view(request, order):
    calendar= models.Calendar.objects.get(order=order)
    
    events= calendar.list_events()
    return render(request, 'calendar.html', {'calendar': calendar,
                                             'events': events})

def profile_view(request, profile_id= None):
    if profile_id:
        profile= models.Profile.objects.get(pk= profile_id)
    else:
        if request.user.is_authenticated():
            profile, created = models.Profile.objects.get_or_create(user=request.user)
        else:
            return redirect ("home")

    calendars= models.Calendar.objects.all()
    if profile.subscribed_calendars == None:
        subscribed_calendars = {calendar.summary: False
                                for calendar in calendars}
    else:
        subscribed_calendars=profile.subscribed_calendars

    if request.method == 'POST':
        form = forms.ProfileForm(request.POST, calendars=calendars, subscribed_calendars=subscribed_calendars)
        if form.is_valid():
            for calendar in calendars:
                if calendar.summary in request.POST:
                    subscribed_calendars[calendar.summary]= True
                else:
                    subscribed_calendars[calendar.summary]= False
            profile.subscribed_calendars = subscribed_calendars
            profile.save()
            messages.add_message(request, messages.SUCCESS, "Profile updated")
            return redirect('home')

    else:
        form = forms.ProfileForm(calendars=calendars, subscribed_calendars=subscribed_calendars)
    return render(request, 'profile_view.html', {'form': form})


def newsletter_view(request):
    models.Newsletter.objects.first().send_newsletter()
    return HttpResponse("Sent")






