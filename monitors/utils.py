

def get_form_data(form):
        if form.is_valid():
        slack_settings = form.cleaned_data.copy()

        # stringify DICT to JSON
        slack_settings = json.dumps(slack_settings)