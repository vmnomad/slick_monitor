from django.shortcuts import render, redirect,reverse
from django.shortcuts import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# Create your views here.
def default(request):
    if(authenticate(username='admin', password='VMware1!')):
        return render(request, 'change_password.html')
    else:
        if request.user.is_authenticated:
            return render (request, 'monitors.html')
        else:
            return redirect(reverse('login'))

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
        print(username)
        print(password)
        user = authenticate(username=username, password=password)
        print('User', user)
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
    return render(request, 'settings.html')
    #return HttpResponse('Placeholder for settings')

@login_required
def settings_email(request):
    return render(request, 'settings_email.html')

@login_required
def settings_slack(request):
    return render(request, 'settings_slack.html')