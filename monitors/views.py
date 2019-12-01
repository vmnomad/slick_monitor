from django.shortcuts import render
from django.shortcuts import HttpResponse
from .forms import SlackAlertForm


# temp view
def test(request):
    form = SlackAlertForm()
    return render(request, 'monitor_form.html', {'url_name': 'dashboard', 'form': form})


# Create your views here.
def dashboard(request):

    return HttpResponse('Landing page of Monitors')

def add_monitor(request):

    return render(request, 'add_monitor.html', {'url_name': 'test'})
    #return HttpResponse('Landing page of Add Monitor')

def edit_monitor(request):
    return HttpResponse('Landing page of Edit Monitor')

def delete_monitor(request):
    return HttpResponse('Landing page of Delete Monitor')

