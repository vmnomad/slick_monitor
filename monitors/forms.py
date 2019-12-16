from django import forms
from setup.models import Alerts





ALERT_TYPES= [
    ('Slack', 'slack'),
    ('Email', 'email'),
    ]

def get_alert_types():
    alerts = Alerts.objects.values('type')
    ALERT_TYPES = []
    for al in alerts:
        for k,v in al.items():
            alert_type = (v, v.capitalize())
            ALERT_TYPES.append(alert_type)
    if len(ALERT_TYPES) == 0:
        ALERT_TYPES.append(('n/a', 'n/a'))
    return ALERT_TYPES






class PingMonitorForm(forms.Form):

    type = forms.CharField(
        required = True,
        widget=forms.HiddenInput(
            attrs={
                'value':'ping'
            })
    )

    # Ping 
    hostname = forms.CharField(
        label='Hostname / IP Address',
        required = True,
        widget=forms.TextInput(
            attrs={
                'placeholder': '192.168.1.1',
                'class' : 'form-control'
            })
    )

    # Count
    count = forms.IntegerField(
        label='Ping Count',
        required = True,
        widget=forms.NumberInput(
            attrs={
                'placeholder': '2',
                'class' : 'form-control'
            }),
        max_value = 3,
        min_value= 1
    )

    # Monitor Interval
    interval = forms.IntegerField(
        label='Ping Interval',
        required = True,
        widget=forms.NumberInput(
            attrs={
                'placeholder': '60',
                'class' : 'form-control'
            }),
        max_value = 86400,
        min_value= 60
    )

     # FTT
    ftt = forms.IntegerField(
        label='Number of failures',
        required = True,
        widget=forms.NumberInput(
            attrs={
                'placeholder': '3',
                'class' : 'form-control'
            }),
        max_value = 100,
        min_value= 1
    )


    # Alet Type
    alert_type = forms.CharField(
        label='Alert Type',
        required = True,
        widget=forms.Select(
            attrs={
                'class' : 'form-control',
                #'readonly' :'readonly'
            },
            choices = get_alert_types())
    )

    # Alert Enabled
    alert_enabled = forms.BooleanField(
        label='Enable Alert',
        required = False,
        widget=forms.CheckboxInput(
            attrs={
                'class' : 'form-control'
            })
    )


class HttpMonitorForm(forms.Form):

    type = forms.CharField(
        required = True,
        widget=forms.HiddenInput(
            attrs={
                'value':'http'
            })
    )


    # Hostname 
    hostname = forms.CharField(
        label='Hostname / IP Address',
        required = True,
        widget=forms.TextInput(
            attrs={
                'placeholder': '192.168.1.1',
                'class' : 'form-control'
            })
    )

    # Allowed HTTP Code
    allowed_codes = forms.IntegerField(
        label='Allowed HTTP code',
        required = False,
        widget=forms.NumberInput(
            attrs={
                'placeholder': '200',
                'class' : 'form-control'
            })
    )

    # Regular expression 
    regexp = forms.CharField(
        label='Matching regexp',
        required = False,
        widget=forms.TextInput(
            attrs={
                'placeholder': '^Python$',
                'class' : 'form-control'
            })
    )

    # Monitor Interval
    interval = forms.IntegerField(
        label='Ping Interval',
        required = True,
        widget=forms.NumberInput(
            attrs={
                'placeholder': '60',
                'class' : 'form-control'
            }),
        max_value = 86400,
        min_value= 60
    )

     # FTT
    ftt = forms.IntegerField(
        label='Number of failures',
        required = True,
        widget=forms.NumberInput(
            attrs={
                'placeholder': '3',
                'class' : 'form-control'
            }),
        max_value = 100,
        min_value= 1
    )


    # Alet Type
    alert_type = forms.CharField(
        label='Alert Type',
        required = True,
        widget=forms.Select(
            attrs={
                'class' : 'form-control',
                #'readonly' :'readonly'
            },
            choices = get_alert_types())
    )

    # Alert Enabled
    alert_enabled = forms.BooleanField(
        label='Enable Alert',
        required = False,
        widget=forms.CheckboxInput(
            attrs={
                'class' : 'form-control'
            })
    )



class SshMonitorForm(forms.Form):

    type = forms.CharField(
        required = True,
        widget=forms.HiddenInput(
            attrs={
                'value':'ssh'
            })
    )

    # Hostname 
    hostname = forms.CharField(
        label='Hostname / IP Address',
        required = True,
        widget=forms.TextInput(
            attrs={
                'placeholder': '192.168.1.1',
                'class' : 'form-control'
            })
    )

    # SSH Username
    username = forms.CharField(
        label='Username',
        required = False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'admin',
                'class' : 'form-control'
            })
    )

    # SSH Password
    password = forms.CharField(
        label='Password',
        required = True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': '********',
                'class' : 'form-control'
            })
    )

    # Monitor Interval
    interval = forms.IntegerField(
        label='Test Interval',
        required = True,
        widget=forms.NumberInput(
            attrs={
                'placeholder': '60',
                'class' : 'form-control'
            }),
        max_value = 86400,
        min_value= 60
    )

     # FTT
    ftt = forms.IntegerField(
        label='Number of failures',
        required = True,
        widget=forms.NumberInput(
            attrs={
                'placeholder': '3',
                'class' : 'form-control'
            }),
        max_value = 100,
        min_value= 1
    )


    # Alet Type
    alert_type = forms.CharField(
        label='Alert Type',
        required = True,
        widget=forms.Select(
            attrs={
                'class' : 'form-control',
                #'readonly' :'readonly'
            },
            choices = get_alert_types())
    )

    # Alert Enabled
    alert_enabled = forms.BooleanField(
        label='Enable Alert',
        required = False,
        widget=forms.CheckboxInput(
            attrs={
                'class' : 'form-control'
            })
    )



class TcpMonitorForm(forms.Form):

    type = forms.CharField(
        required = True,
        widget=forms.HiddenInput(
            attrs={
                'value':'tcp'
            })
    )

    # Hostname 
    hostname = forms.CharField(
        label='Hostname / IP Address',
        required = True,
        widget=forms.TextInput(
            attrs={
                'placeholder': '192.168.1.1',
                'class' : 'form-control'
            })
    )

    # Port
    port = forms.IntegerField(
        label='Port',
        required = False,
        widget=forms.NumberInput(
            attrs={
                'placeholder': '443',
                'class' : 'form-control'
            })
    )

    # Timeout
    timeout = forms.IntegerField(
        label='Timeout',
        required = False,
        widget=forms.NumberInput(
            attrs={
                'placeholder': '2',
                'class' : 'form-control'
            }),
        min_value=1,
        max_value=10
    )

    # Monitor Interval
    interval = forms.IntegerField(
        label='Ping Interval',
        required = True,
        widget=forms.NumberInput(
            attrs={
                'placeholder': '60',
                'class' : 'form-control'
            }),
        max_value = 86400,
        min_value= 60
    )

     # FTT
    ftt = forms.IntegerField(
        label='Number of failures',
        required = True,
        widget=forms.NumberInput(
            attrs={
                'placeholder': '3',
                'class' : 'form-control'
            }),
        max_value = 100,
        min_value= 1
    )


    # Alet Type
    alert_type = forms.CharField(
        label='Alert Type',
        required = True,
        widget=forms.Select(
            attrs={
                'class' : 'form-control',
                #'readonly' :'readonly'
            },
            choices = get_alert_types())
    )

    # Alert Enabled
    alert_enabled = forms.BooleanField(
        label='Enable Alert',
        required = False,
        widget=forms.CheckboxInput(
            attrs={
                'class' : 'form-control'
            })
    )



class Form_Factory():
   def create_form(self, typ, request=False):

        target_class = typ.capitalize() + "MonitorForm"
        if request:
            return globals()[target_class](request)
        else: 
            print('returning form:', target_class)
            return globals()[target_class]()