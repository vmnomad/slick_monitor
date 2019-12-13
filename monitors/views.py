from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import redirect,reverse
from .forms import PingMonitorForm, HttpMonitorForm, SshMonitorForm, TcpMonitorForm, Form_Factory
from django.contrib.auth.decorators import login_required
from monitors.models import Monitors, States
import json



# temp view
def test(request):
    form = PingMonitorForm()
    return render(request, 'monitor_form.html', {'url_name': 'dashboard', 'form': form})

@login_required
def get_form(request, type):

    formFactory = Form_Factory()
    form = formFactory.create_form(type)
    return render(request, 'monitor_form.html', {'url_name': 'add_monitor', 'form': form})

# Create your views here.
@login_required
def dashboard(request):


    query_results = Monitors.objects.all()

    display_results = []

    for result in query_results:
        
        if result.states.state == 2:
            display_state = 'circle-gray'
        if result.states.state == 1:
            display_state = 'circle-green'
        if result.states.state == 0:
            display_state = 'circle-red'

        display_result = {
                          'hostname' : result.hostname, 
                          'type' : result.type, 
                          'display_state': display_state
                          }
        display_results.append(display_result)

    return render(request, 'monitors_dashboard.html', {'query_results': display_results})

@login_required
def add_form(request):
    return render(request, 'add_monitor.html', {'url_name': 'get_monitor_form'})

@login_required
def edit_monitor(request, id):
    return HttpResponse('Landing page of Edit Monitor')

@login_required
def delete_monitor(request, id):
    return HttpResponse('Landing page of Delete Monitor')

@login_required
def add_monitor(request):
    type = request.POST.get('type')
    formFactory = Form_Factory()
    form = formFactory.create_form(type, request.POST)
    
    if form.is_valid():
        form = form.cleaned_data.copy()
        print(form['type'])
        type = form['type']


        params = {}

        if type == 'ping':
            params['count'] = form['count']
            
        elif type == 'http':
            if 'allowed_codes' in form:
                params['allowed_codes'] = form['allowed_codes']
            if 'regexp' in form:
                params['regexp'] = form['regexp']
        elif type == 'tcp':
            params['port'] = form['port']
            params['timeout'] = form['timeout']
        elif type == 'ssh':
            params['u'] = form['port']
            params['timeout'] = form['timeout']


        # stringify params 
        params = json.dumps(params)

        # write monitor to DB
        monitor =  Monitors(
                        hostname=form['hostname'], 
                        type = form['type'],
                        interval = form['interval'],
                        ftt = form['ftt'],
                        alert_type = form['alert_type'],
                        alert_enabled = form['alert_enabled'],
                        params = params)
        

        try:
            monitor.save()
            print('successfully saved monitor', monitor)
        except Exception as err:
            return render(request, 'error.html', {'error': err})


        # TODO delete Monitor
        try:
            state = States(monitor=monitor, state=2)
            state.save()    
            print('successfully saved state', type)
        except Exception as err:
            return render(request, 'error.html', {'error': err})
    else:
        print(form.errors)
        return render(request, 'error.html', {'error': 'wrong type of monitor'})

    return redirect(reverse('dashboard'))
