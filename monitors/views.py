from django.shortcuts import render
from django.shortcuts import HttpResponse
from .forms import SlackAlertForm, EmailAlertForm


# temp view
def test(request):
    form = SlackAlertForm()
    return render(request, 'monitor_form.html', {'url_name': 'dashboard', 'form': form})


def get_form(request, type):
    print('Type:', type)
    if type == 'ping':
        form = SlackAlertForm()
    elif type == 'http':
        form = EmailAlertForm()

    return render(request, 'monitor_form.html', {'url_name': 'test', 'form': form})

# Create your views here.
def dashboard(request):

    return HttpResponse('Landing page of Monitors')

def add_monitor(request):

    return render(request, 'add_monitor.html', {'url_name': 'get_monitor_form'})
    #return HttpResponse('Landing page of Add Monitor')

def edit_monitor(request):
    return HttpResponse('Landing page of Edit Monitor')

def delete_monitor(request):
    return HttpResponse('Landing page of Delete Monitor')

