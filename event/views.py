import datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse, reverse_lazy

from django.db.models import Max
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from account import forms as auth_forms, views as auth_views
from event import forms, models
from .mixins import StaffViewMixin


#Account views
class LoginView(auth_views.LoginView):
    form_class = auth_forms.LoginEmailForm

class SignupView(auth_views.SignupView):
    form_class = forms.SignupForm

    def generate_username(self, form):
        username = form['email'].value()[0:29].lower()
        username = ''.join([x for x in username if x not in "!#$%&'*+-/=?^_`{|}~}"])
        i=0
        while models.User.objects.filter(username=username):
            if i < 10:
                username=str(i) + username[1:]
            else:
                username=str(i) + username[2:]
            i+=1
        return username   

def profile_view(request, profile_id= None):
    if profile_id:
        profile= models.Profile.objects.get(pk= profile_id)
    else:
        if request.user.is_authenticated():
            profile, created = models.Profile.objects.get_or_create(user=request.user)
        else:
            return redirect ("login")

    calendars= models.Calendar.objects.all()
    if not profile.subscribed_calendars:
        profile.subscribed_calendars= {calendar.summary: False
                                       for calendar in calendars}
        profile.save()

    if request.method == 'POST':
        form = forms.ProfileForm(request.POST, calendars=calendars, subscribed_calendars=profile.subscribed_calendars)
        if form.is_valid():
            profile.subscribed_calendars = form.cleaned_data
            profile.save()
            messages.add_message(request, messages.SUCCESS, "Profile updated")
            return redirect('home')

    else:
        form = forms.ProfileForm(calendars=calendars, subscribed_calendars=profile.subscribed_calendars)
    
    return render(request, 'account/profile.html', {'form': form,
                                                    'events': models.Event.objects.filter(creator= request.user)})

class MyEventsView(LoginRequiredMixin, ListView):
    template_name= 'account/my_events.html'
    context_object_name= 'events'

    def get_queryset(self):
        queryset= models.Event.objects.filter(creator= self.request.user)
        return queryset

#Public Views
class HomepageView(TemplateView):
    template_name = "homepage.html"  

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            try: 
                profile_exists= request.user.profile.subscribed_calendars
            except AttributeError:
                return redirect('profile')

        return super().get(request, *args, **kwargs) 

    def get_context_data(self, *args, **kwargs):
        context= super().get_context_data(*args, **kwargs)
        context['blog']= models.Blog.objects.last()
        return context


def calendar_detail_view(request, order):
    calendar= models.Calendar.objects.get(order=order)
    events= calendar.list_events()
    return render(request, 'calendar.html', {'calendar': calendar,
                                             'events': events})

class SearchEventsView(TemplateView):
    calendars= models.Calendar.objects.all()
    template_name= "event_search.html"
    time_min= datetime.date.today().strftime('%m-%d-%Y')
    time_max= (datetime.date.today() + datetime.timedelta(days=30)).strftime('%m-%d-%Y')

    def get_context_data(self, *args, **kwargs):
        self.time_min= datetime.datetime.strptime(self.request.GET.get('time_min', self.time_min), '%m-%d-%Y')
        self.time_max= datetime.datetime.strptime(self.request.GET.get('time_max', self.time_max), '%m-%d-%Y')
        context = super().get_context_data(*args, **kwargs)
        context['search_results']= {}
        for calendar in self.calendars:
            context['search_results'][calendar.summary]= calendar.list_events(time_min=self.time_min, time_max=self.time_max)
        return context   


#Event Management Views
class EventCreateView(CreateView):
    model = models.Event
    form_class= forms.EventForm
    auto_approve= False

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object= form.save(commit= False)
        self.object.creator= self.request.user
        if self.auto_approve and self.request.user.is_staff:
            gcal= self.object.calendar.add_event(self.object)
            if gcal:
                messages.add_message(self.request, messages.ERROR, str(gcal))
            else: 
                messages.add_message(self.request, messages.SUCCESS, "Event saved and added to calendar.")
        else:
            messages.add_message(self.request, messages.SUCCESS, 
                                 "Event created! It will be added to the calendar after approval by site moderators.")
        self.object.save() 
        return redirect(self.get_success_url())  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['admin_url']= "admin_add_event"
        return context  

    def get_success_url(self):
        if self.object.recurring:
            url= reverse('recurrence', args=[self.object.id])
        else:
            url = self.object.get_absolute_url()
        return url

class EventDetailView(DetailView):
    model= models.Event
    context_object_name = 'event'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rrules']= models.Rrule.objects.filter(event= context['event'])   
        if self.object.gcal_id: 
            context['approved']= True
        else: 
            context['approved']= False
        return context 

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.gcal_id:
            gcal= self.object.calendar.update_event(self.object)
        else:
            gcal= self.object.calendar.add_event(self.object)

        if gcal:
            messages.add_message(self.request, messages.ERROR, str(gcal))
        else: 
            messages.add_message(self.request, messages.SUCCESS, "Event added to calendar.")

        return redirect(self.object)

def gcal_id_redirect(request, gcal_id, calendar_id=None):
    try:
        event= models.Event.objects.get(gcal_id= gcal_id)
    except models.Event.DoesNotExist:
        if calendar_id:
            calendar= models.Calendar.objects.get(id=calendar_id)
            event= calendar.single_refresh(gcal_id)
        else:
            event= None
    if event:
        return redirect(event)

    messages.add_message(request, messages.ERROR, "Event not in Database. It may be imported from the Calendar page.")
    return redirect(request.META.get('HTTP_REFERER','/'))

class EventDeleteView(DeleteView):
    model= models.Event
    template_name= "event_delete.html"
    success_url= reverse_lazy('home')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        gcal= self.object.full_delete()
        if gcal:
            messages.add_message(self.request, messages.ERROR, str(gcal))
        else:
            messages.add_message(self.request, messages.SUCCESS, "%s deleted." % self.object.summary)
        return redirect(success_url)    

class EventUpdateView(UpdateView):
    model = models.Event
    form_class= forms.EventForm
    auto_approve= False

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form): 
        self.object= form.save(commit= False)
        self.object.rcnotes= "Updated on %s by %s\n" % (datetime.date.today(),self.request.user.email) + self.object.rcnotes
        self.object.save()
        if self.auto_approve and self.request.user.is_staff:
            if self.object.gcal_id:
                gcal= self.object.calendar.update_event(self.object)
            else:
                gcal= self.object.calendar.add_event(self.object)

            if gcal:
                messages.add_message(self.request, messages.ERROR, str(gcal))
            else: 
                messages.add_message(self.request, messages.SUCCESS, "Event updated and added to calendar.")
        else:
            if self.object.gcal_id:
                self.object.calendar.remove_event(self.object)

            messages.add_message(self.request, messages.SUCCESS, 
                                 "Event updated! It will be added to the calendar after approval by site moderators.")   
        return redirect(self.get_success_url())   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['admin_url']= "admin_update_event"
        return context          

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

class UnapprovedEventsView(StaffViewMixin, TemplateView):
    template_name="unapproved_events.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events']= models.Event.objects.filter(gcal_id= '')
        return context

class AllEventListView(StaffViewMixin, ListView):
    model= models.Event
    queryset= models.Event.objects.all()
    context_object_name = 'events'

#Calendar Management Views
class CalendarCreateView(StaffViewMixin, CreateView):
    model= models.Calendar
    fields = ['summary', 'timeZone', 'order', 'description']
    template_name= 'calendar_form.html'
    success_url = reverse_lazy('calendar_list')

    def form_valid(self, form):
        self.object = form.save()
        self.object.refresh()
        return redirect(self.get_success_url())

    def get_initial(self):
        if 'order' not in self.initial:
            try:
                self.initial['order']= models.Calendar.objects.all().aggregate(Max('order'))['order__max'] + 1
            except:
                self.initial['order']= 1
        if 'pk' in self.kwargs:
            self.initial['pk']= self.kwargs['pk']
            CalendarList = models.CalendarList()
            if type (CalendarList) is not  models.CalendarList:
                messages.add_message(self.request, messages.ERROR, str(CalendarList))
                return self.initial.copy()
            details= CalendarList.get_details(self.kwargs['pk'])
            self.initial['summary']= details['summary']
            if 'description' in details:
                self.initial['description']= details['description']
        return self.initial.copy()

class CalendarEventListView(StaffViewMixin, ListView):
    model= models.Event
    context_object_name = 'events'
    calendar= None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calendar']= self.calendar
        return context 

    def get_queryset(self):
        calendar_id= self.kwargs['pk']
        self.calendar= models.Calendar.objects.get(pk=calendar_id)
        return models.Event.objects.filter(calendar= self.calendar)      

class CalendarListView(StaffViewMixin, ListView):
    model= models.Calendar
    queryset= models.Calendar.objects.all()
    context_object_name= 'calendars'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        CalendarList= models.CalendarList()
        if type (CalendarList) is not  models.CalendarList:
            messages.add_message(self.request, messages.ERROR, str(CalendarList))
            return context
        context['private_calendars']= CalendarList.get_private_calendars()
        return context 

class CalendarUpdateView(StaffViewMixin, UpdateView):
    model= models.Calendar
    fields = ['summary', 'timeZone', 'order', 'description']
    template_name= 'calendar_form.html'
    success_url = reverse_lazy('calendar_list')

@login_required(login_url='/account/login/')
def calendar_remove_event(request, pk):
    event= models.Event.objects.get(pk=pk)
    gcal= event.calendar.remove_event(event)
    if gcal:
        messages.add_message(request, messages.ERROR, str(gcal))
    else:
        messages.add_message(request, messages.SUCCESS, "%s removed." % event.summary)
        event.rcnotes += "Removed on %s by %s" % (datetime.date.today(), request.user.email)
        event.save()
    return redirect(event)


@user_passes_test(lambda u: u.is_staff, login_url='/account/login/')
def delete_calendar(request, pk):
    models.Calendar.objects.get(id=pk).delete()
    return redirect('calendar_list')  

@user_passes_test(lambda u: u.is_staff, login_url='/account/login/')
def calendar_refresh(self):
    for calendar in models.Calendar.objects.all():
        calendar.refresh()
    return redirect ("all_events")

#Site/Newsletter Management
class SiteManagementView(StaffViewMixin, UpdateView):
    #template_name="site_management.html"
    model= models.Newsletter
    form_class= forms.SiteForm
    template_name= "newsletter_form.html"
    success_url= reverse_lazy("lounge")

    def form_valid(self, form):
        site= models.Site.objects.get_current()
        if 'domain' in form.cleaned_data:
            site.domain= form.cleaned_data.pop('domain')
        if 'name' in form.cleaned_data:
            site.name= form.cleaned_data.pop('name')
        site.save()    

        return super().form_valid(form)

    def get_object(self):
        newsletter= models.Newsletter.objects.first()
        if not newsletter:
            newsletter= models.Newsletter.objects.create()
        return newsletter

    def get_initial(self):
        site= models.Site.objects.get_current()
        self.initial['domain']= site.domain
        self.initial['name']= site.name
        return self.initial.copy()   

class BlogCreateView(StaffViewMixin, CreateView):
    model= models.Blog
    fields= '__all__'
    success_url= reverse_lazy("home")

    def get_initial(self):
        self.initial['date']= datetime.date.today()
        return self.initial.copy()

class BlogListView(ListView):
    model= models.Blog
    context_object_name = 'entries'

class BlogDeleteView(StaffViewMixin, DeleteView):
    model= models.Blog
    success_url= reverse_lazy("blog")
    context_object_name =  'entry'

class AdminLoungeView(StaffViewMixin, TemplateView):
    template_name= 'rc_lounge.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['staff']= models.User.objects.filter(is_staff= True)
        return context

class ManageAdminView(StaffViewMixin, UpdateView):
    model= models.User
    template_name= 'rc_manage.html'
    success_url= reverse_lazy('lounge')
    fields = ['is_staff']

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object:
            return super().get(request, *args, **kwargs)
        messages.add_message(self.request, messages.WARNING, "You cannot change your own status.")
        return redirect ('lounge')

    def get_object(self, queryset=None):
        obj= super().get_object(queryset= queryset)
        if obj == self.request.user:
            obj= None
        return obj

class UserListView(StaffViewMixin, ListView):
    model= models.User
    context_object_name = 'users'
    ordering= 'email'
    template_name= 'user_list.html'

@user_passes_test(lambda u: u.is_staff, login_url='/account/login/')
def send_newsletter(request):
    newsletter= models.Newsletter.objects.first()
    if newsletter:
        newsletter.send_newsletter()
        messages.add_message(request, messages.SUCCESS, "Newsletter Sent.")
        return redirect ('lounge')

    messages.add_message(request, messages.WARNING, "Set up newsletter and domain settings.")
    return redirect ('site')

@user_passes_test(lambda u: u.is_staff, login_url='/account/login/')
def event_cleanup(request, delete_recurring= False):
    events= models.Event.objects.filter(start__lt= datetime.date.today())
    
    if not delete_recurring:
        events= events.filter(rrule__isnull= True)

    for event in events:
        messages.add_message(request, messages.SUCCESS, "Deleted %s %s" % (event.start.strftime("%m/%d/%Y"), event.summary))
        event.delete()
    return redirect('lounge')