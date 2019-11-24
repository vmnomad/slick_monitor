from django.shortcuts import render, redirect,reverse
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
from .forms import NameForm, EmailSettingsForm

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
            return redirect(reverse('settings'))
        else:
            context = {"message": 'wrong password'}
            print('Context:', context)
            return render(request, 'login.html', context=context)

@login_required
def my_logout(request):
    logout(request)
    return render(request, 'login.html')

@login_required
def settings(request):
    form = EmailSettingsForm()
    return render(request, 'settings_email.html', {'form': form})


@login_required
def settings_email(request):
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        form = EmailSettingsForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            my_keys = form.cleaned_data.copy()
            print(json.dumps(my_keys))

            # place data into database
            # ...
            # redirect to a new URL:
            return HttpResponse("Placeholder to update email settings")

    # if a GET (or any other method) we'll create a blank form
    else:
        # read data from the database

        # data = {'smtp': 'host'}
        #form = EmailSettingsForm(data=data)

        form = EmailSettingsForm()

    return render(request, 'settings_email.html', {'form': form})

@login_required
def settings_email_old(request):
    if request.method == 'GET':
        return render(request, 'settings_email.html')
    elif request.method == 'POST':
        my_keys = request.POST.copy()
        my_keys.pop('csrfmiddlewaretoken', None)
        print(json.dumps(my_keys))
        for key, val in my_keys.items():
            print(key, val)
        return HttpResponse("Placeholder to update email settings")
        
@login_required
def settings_slack(request):
    if request.method == 'GET':
        return render(request, 'settings_slack.html')
    elif request.method == 'POST':
        return HttpResponse("Placeholder to update slack settings")