from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required


# Create your views here.
def default(request):
    if(authenticate(username='admin', password='VMware1!')):
        return render(request, 'welcome.html')
    else:
        if request.user.is_authenticated:
            render (request, 'monitors.html')
        else:
            return render(request, 'login.html')

def change_password(request):
    
    new_password = request.POST.get('inputPassword1')
    
    user = User.objects.get(username='admin')    
    user.set_password(new_password)
    user.save()
    return render(request, 'login.html')

def login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    print(username)
    print(password)
    user = authenticate(username=username, password=password)
    print('User', user)
    if user is not None:
        return redirect('/settings/')

@login_required
def settings(request):
    return HttpResponse('Placeholder for settings')