from django.shortcuts import render, redirect,reverse
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
from .forms import EmailAlertForm, SlackAlertForm, ConsoleLoggingForm, FileLoggingForm, NetcatLoggingForm

from setup.models import Alerts, Loggers

# Create your views here.
def default(request):
    if(authenticate(username='admin', password='VMware1!')):
        return render(request, 'change_password.html')
    else:
        if request.user.is_authenticated:
            return render (request, 'monitors.html')
        else:
            return redirect(reverse('login'))

@login_required
def change_password(request):
    if request.method == 'GET':
        return render(request, 'change_password.html')
    else:
        current_password = request.POST.get('currentPassword')
        new_password = request.POST.get('inputPassword1')
        if authenticate(username='admin', password=current_password) is not None:
            user = User.objects.get(username='admin')    
            user.set_password(new_password)
            user.save()
            return render(request, 'login.html')
        else:
            # TODO generate warning message
            return render(request, 'change_password.html')
        
def my_login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')        
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(reverse('default'))
        else:
            context = {"message": 'wrong password'}
            return render(request, 'login.html', context=context)

@login_required
def my_logout(request):
    logout(request)
    return render(request, 'login.html')

@login_required
def alerts(request):
    return redirect(reverse('email'))

@login_required
def loggers(request):
    return redirect(reverse('console'))

@login_required
def alerts_email(request):
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        form = EmailAlertForm(request.POST)

        # check whether it's valid:
        if form.is_valid():

            # get data from the form
            email_settings = form.cleaned_data.copy()

            # stringify DICT to JSON
            print(json.dumps(email_settings))
            email_settings = json.dumps(email_settings)

            # if email settings exist:
            if len(Alerts.objects.filter(type="email")) == 1:
                email_alert = Alerts.objects.get(type="email")
                email_alert.settings = email_settings
                email_alert.save()

            # create new settings
            else:
                email_alert = Alerts(type="email", settings=email_settings)
                email_alert.save()
            # 
            # redirect to a new URL:
            return redirect(reverse('email'))

    # if a GET (or any other method) we'll create a blank form
    else:
        if len(Alerts.objects.filter(type="email")) == 1:
                email_alert = Alerts.objects.get(type="email")  
                email_settings = json.loads(email_alert.settings)
        else:
            form = EmailAlertForm()
            return render(request, 'alerts_email.html', {'form': form})

        form = EmailAlertForm(email_settings)

    return render(request, 'alerts_email.html', {'form': form})


@login_required
def alerts_slack(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SlackAlertForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            slack_settings = form.cleaned_data.copy()

            # stringify DICT to JSON
            slack_settings = json.dumps(slack_settings)

            # if slack settings exist:
            if len(Alerts.objects.filter(type="slack")) == 1:
                slack_alert = Alerts.objects.get(type="slack")
                slack_alert.settings = slack_settings
                slack_alert.save()

            # create new settings
            else:
                slack_alert = Alerts(type="slack", settings=slack_settings)
                slack_alert.save()
            # 
            # redirect to a new URL:
            return redirect(reverse('slack'))

    # if a GET (or any other method) we'll create a blank form
    else:
        # return prepopulated form
        if len(Alerts.objects.filter(type="slack")) == 1:
                slack_alert = Alerts.objects.get(type="slack")  
                slack_settings = json.loads(slack_alert.settings)
                form = SlackAlertForm(slack_settings)
                return render(request, 'alerts_slack.html', {'form': form})
        # return empty form
        else:
            form = SlackAlertForm()
            return render(request, 'alerts_slack.html', {'form': form})

@login_required
def loggers_console(request):
    logger_type = 'console'
    template_data = {'url_name' : logger_type}
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ConsoleLoggingForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            logger_settings = form.cleaned_data.copy()

            # stringify DICT to JSON
            logger_settings = json.dumps(logger_settings)

            # if slack settings exist:
            if len(Loggers.objects.filter(type=logger_type)) == 1:
                logger = Loggers.objects.get(type=logger_type)
                logger.settings = logger_settings
                logger.save()

            # create new settings
            else:
                logger = Loggers(type=logger_type, settings=logger_settings)
                logger.save()

            # redirect to a current form:
            return redirect(reverse(logger_type))

    # if a GET (or any other method) we'll create a blank form
    else:
        # return prepopulated form
        if len(Loggers.objects.filter(type=logger_type)) == 1:
                
                # get current config
                logger = Loggers.objects.get(type=logger_type)  
                logger_settings = json.loads(logger.settings)
                
                # pre-populate the form  
                template_data['form'] = ConsoleLoggingForm(logger_settings)
                return render(request, 'loggers_form.html', template_data)
        # return empty form
        else:
            template_data['form']  = ConsoleLoggingForm()
            return render(request, 'loggers_form.html', template_data)

def loggers_netcat(request):
    logger_type = 'netcat'
    template_data = {'url_name' : logger_type}
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NetcatLoggingForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            logger_settings = form.cleaned_data.copy()

            # stringify DICT to JSON
            logger_settings = json.dumps(logger_settings)

            # if slack settings exist:
            if len(Loggers.objects.filter(type=logger_type)) == 1:
                logger = Loggers.objects.get(type=logger_type)
                logger.settings = logger_settings
                logger.save()

            # create new settings
            else:
                logger = Loggers(type=logger_type, settings=logger_settings)
                logger.save()

            # redirect to a current form:
            return redirect(reverse(logger_type))

    # if a GET (or any other method) we'll create a blank form
    else:
        # return prepopulated form
        if len(Loggers.objects.filter(type=logger_type)) == 1:
                
                # get current config
                logger = Loggers.objects.get(type=logger_type)  
                logger_settings = json.loads(logger.settings)
                
                # pre-populate the form  
                template_data['form'] = NetcatLoggingForm(logger_settings)
                return render(request, 'loggers_form.html', template_data)
        # return empty form
        else:
            template_data['form']  = NetcatLoggingForm()
            return render(request, 'loggers_form.html', template_data)

def loggers_file(request):
    logger_type = 'file'
    template_data = {'url_name' : logger_type}
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = FileLoggingForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            logger_settings = form.cleaned_data.copy()

            # stringify DICT to JSON
            logger_settings = json.dumps(logger_settings)

            # if slack settings exist:
            if len(Loggers.objects.filter(type=logger_type)) == 1:
                logger = Loggers.objects.get(type=logger_type)
                logger.settings = logger_settings
                logger.save()

            # create new settings
            else:
                logger = Loggers(type=logger_type, settings=logger_settings)
                logger.save()

            # redirect to a current form:
            return redirect(reverse(logger_type))

    # if a GET (or any other method) we'll create a blank form
    else:
        # return prepopulated form
        if len(Loggers.objects.filter(type=logger_type)) == 1:
                
                # get current config
                logger = Loggers.objects.get(type=logger_type)  
                logger_settings = json.loads(logger.settings)
                
                # pre-populate the form  
                template_data['form'] = FileLoggingForm(logger_settings)
                return render(request, 'loggers_form.html', template_data)
        # return empty form
        else:
            template_data['form']  = FileLoggingForm()
            return render(request, 'loggers_form.html', template_data)