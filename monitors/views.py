from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import redirect,reverse
from .forms import PingMonitorForm, HttpMonitorForm, SshMonitorForm, TcpMonitorForm, Form_Factory
from django.contrib.auth.decorators import login_required
from monitors.models import Monitors, States
import json
from setup.utils import encrypt, decrypt


MUTABLE_PARAMS = ['interval', 'ftt', 'alert_type', 'alert_enabled']


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
    print(query_results)
    if len(query_results) > 0:

        display_results = []
        
        for result in query_results:
            
            if result.states.state == 2:
                display_state = 'circle-gray'
            if result.states.state == 1:
                display_state = 'circle-green'
            if result.states.state == 0:
                display_state = 'circle-red'

            display_result = {
                            'id' : result.id,
                            'hostname' : result.hostname, 
                            'type' : result.type, 
                            'display_state': display_state
                            }
            display_results.append(display_result)

        return render(request, 'monitors_dashboard.html', {'query_results': display_results})
    else:
        display_results = 'No configured monitors'
        return render(request, 'monitors_dashboard.html', {'message': display_results})



@login_required
def add_form(request):
    return render(request, 'add_monitor.html', {'url_name': 'get_monitor_form'})

@login_required
def edit_monitor(request, id):

    # if a GET (or any other method) we'll create a blank form
    if request.method == 'GET':
        if Monitors.objects.filter(id=id).exists():

            # get Monitor settings as DICT
            m = Monitors.objects.filter(id=id).values()[0]
            type = m['type']
            
            
            params = json.loads(m['params'])

            if type == 'ping':    
                m['count'] = params['count']
            elif type == 'http':
                m['allowed_codes'] =  ','.join([str(char) for char in params['allowed_codes']]) #params['allowed_codes']
                m['regexp'] = params['regexp']
            elif type == 'tcp':
                m['port'] = params['port']
                m['timeout'] = params['timeout']
            elif type == 'ssh':
                m['username'] = params['username']
                m['password'] = params['password']
                
            # create and populate form    
            formFactory = Form_Factory()
            form = formFactory.create_form(type, m)

            # lock down Hostname attribute of the form
            form.fields['hostname'].widget.attrs['readonly']= 'readonly'

            # renders a form using form. Passing ID
            return render(request, 'edit_monitor.html', {'url_name': 'edit_monitor', 'form': form, 'id': m['id']})

    else:
        # get monitor params from DB
        m = Monitors.objects.get(id=id)

        # get monitor type
        type = request.POST.get('type')

        # generate form using form type and form payload
        formFactory = Form_Factory()
        form = formFactory.create_form(type, request.POST)

        # use form data to update and save monitor
        if form.is_valid():
            form = form.cleaned_data.copy()
            
            # Update Params
            params = {}
            if type == 'ping':
                params['count'] = form['count']
            
            elif type == 'http':
                if 'allowed_codes' in form:
                    params['allowed_codes'] = [int(x) for x in form['allowed_codes'].split(',')]  #form['allowed_codes']
                if 'regexp' in form:
                    params['regexp'] = form['regexp']
            elif type == 'tcp':
                params['port'] = form['port']
                params['timeout'] = form['timeout']
            elif type == 'ssh':
                params['username'] = form['username']
                params['password'] = encrypt(form['password'])
            # stringify params 
            params = json.dumps(params)
            m.params = params
            
            # update MUTABLE parameters
            for p in MUTABLE_PARAMS:
                setattr(m, p, form[p])

            m.save()
            return redirect(reverse('dashboard'))
        else:
            print(form.errors)



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
                if form['allowed_codes'] != '':
                    params['allowed_codes'] = [int(x) for x in form['allowed_codes'].split(',')]  #form['allowed_codes']
                else:
                    params['allowed_codes'] = []
            if 'regexp' in form:
                params['regexp'] = form['regexp']
        elif type == 'tcp':
            params['port'] = form['port']
            params['timeout'] = form['timeout']
        elif type == 'ssh':
            params['username'] = form['username']
            params['password'] = encrypt(form['password'])

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


        # TODO delete Monitor if adding State fails
        try:
            state = States(monitor=monitor, state=2)
            state.save()    
            print('successfully saved state', type)
        except Exception as err:
            monitor.delete()
            return render(request, 'error.html', {'error': err})
    else:
        print(form.errors)
        return render(request, 'error.html', {'error': 'wrong type of monitor'})

    return redirect(reverse('dashboard'))


@login_required
def delete_monitor(request, id):
    monitor = Monitors.objects.get(id=id)
    monitor.delete()
    return redirect(reverse('dashboard'))