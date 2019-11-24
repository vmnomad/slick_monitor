from django import forms
class NameForm(forms.Form):
    your_name = forms.CharField(
        label='Your name', 
        max_length=100, 
        widget=forms.TextInput(
            attrs={'placeholder': '1234 Main St',
                    'class' : 'form-control'
            })
    )

class EmailSettingsForm(forms.Form):
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
        required = True,
        widget=forms.CheckboxInput(
            attrs={
                'class' : 'form-control'
            })
    )




class SlackSettingsForm(forms.Form):
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
