from django import forms


from django import forms

LOGGING_LEVELS= [
    ('INFO', 'INFO'),
    ('DEBUG', 'DEBUG'),
    ('ERROR', 'ERROR'),
    ('WARNING', 'WARNING'),
    ]

class EmailAlertForm(forms.Form):
    # SMTP Host
    smtp_host = forms.CharField(
        label='SMTP host',
        required = True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'smtp.gmail.com',
                'class' : 'form-control'
            })
    )

    # SMTP Port
    smtp_port = forms.IntegerField(
        label='SMTP port',
        required = True,
        widget=forms.NumberInput(
            attrs={
                'placeholder': '587',
                'class' : 'form-control'
            })
    )

    # Sender Email
    from_addr = forms.EmailField(
        label='Sender Address',
        required = True,
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'slick.monitor@lab.local',
                'class' : 'form-control'
            })
    )

    # Receiever Email
    to_addr = forms.EmailField(
        label='Receiver Address',
        required = True,
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'lab_owner@lab.local',
                'class' : 'form-control'
            })
    )

    # Username
    username = forms.CharField(
        label='Username',
        required = True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'login.name',
                'class' : 'form-control'
            })
    )

    # Password
    password = forms.CharField(
        label='Password',
        required = True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': '********',
                'class' : 'form-control'
            })
    )

    # Alert Interval
    alert_interval = forms.IntegerField(
        label='Alert Interval',
        required = True,
        widget=forms.NumberInput(
            attrs={
                'placeholder': '60',
                'class' : 'form-control'
            }),
        max_value = 86400,
        min_value= 60
    )

    # SSL
    ssl = forms.BooleanField(
        label='Enable SSL',
        required = False,
        widget=forms.CheckboxInput(
            attrs={
                'class' : 'form-control'
            })
    )


class SlackAlertForm(forms.Form):
    # Slack Webhook
    webhook = forms.CharField(
        label='Slack Webhook',
        required = True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'https://hooks.slack.com/services/XXXX/XXXX',
                'class' : 'form-control'
            })
    )

    # Alert Interval
    alert_interval = forms.IntegerField(
        label='Alert Interval',
        required = True,
        widget=forms.NumberInput(
            attrs={
                'placeholder': '60',
                'class' : 'form-control'
            }),
        max_value = 86400,
        min_value= 60
    )



class ConsoleLoggingForm(forms.Form):
    # Enable Logger
    enabled = forms.BooleanField(
        label='Enable Console Logging',
        required = False,
        widget=forms.CheckboxInput(
            attrs={
                'class' : 'form-control'
            })
    )

    # Set Logging level
    logging_level = forms.CharField(
        label='Logging Level',
        required = True,
        widget=forms.Select(
            attrs={
                'class' : 'form-control',
                #'readonly' :'readonly'
            },
            choices = LOGGING_LEVELS)
    )


class FileLoggingForm(forms.Form):
    # Enable Logger
    enabled = forms.BooleanField(
        label='Enable File Logging',
        required = False,
        widget=forms.CheckboxInput(
            attrs={
                'class' : 'form-control'
            })
    )

    # Set Logging level
    logging_level = forms.CharField(
        label='Logging Level',
        required = True,
        widget=forms.Select(
            attrs={
                'class' : 'form-control',
                #'readonly' :'readonly'
            },
            choices = LOGGING_LEVELS)
    )

    # Set Logging File Size
    file_size = forms.IntegerField(
        label='Log File Size (MB)',
        required = True,
        widget=forms.NumberInput(
            attrs={
                'placeholder': '1',
                'class' : 'form-control',
                #'readonly' :'readonly'
            }),
        max_value = 10,
        min_value= 1
    )

    # Set Max Number of Log Files
    file_number = forms.IntegerField(
        label='Number of Log Files',
        required = True,
        widget=forms.NumberInput(
            attrs={
                'placeholder': '1',
                'class' : 'form-control',
                #'readonly' :'readonly'
            }),
        max_value = 10,
        min_value= 1
    )


class NetcatLoggingForm(forms.Form):
    # Enable Logger
    enabled = forms.BooleanField(
        label='Enable Netcat Logging',
        required = False,
        widget=forms.CheckboxInput(
            attrs={
                'class' : 'form-control'
            })
    )

    # Set Logging level
    logging_level = forms.CharField(
        label='Console Logging Level',
        required = True,
        widget=forms.Select(
            attrs={
                'class' : 'form-control',
                #'readonly' :'readonly'
            },
            choices = LOGGING_LEVELS)
    )

    # Netcat Host
    hostname = forms.CharField(
        label='Netcat hostname',
        required = True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'ubuntu-1.lab.local',
                'class' : 'form-control'
            })
    )

    # SMTP Port
    port = forms.IntegerField(
        label='Netcat port',
        required = True,
        widget=forms.NumberInput(
            attrs={
                'placeholder': '1234',
                'class' : 'form-control'
            })
    )