import smtplib
import shelve
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import pprint
import logging
import requests
import json
import sqlite3
import Loggers

from Utils import decrypt, load_alerts


alerts_logger = Loggers.get_queue_logger(logging.DEBUG, __name__)


class Alert:
    def fail(self):
        return 'function is not defined'

    

class Email_alert(Alert):

    def __init__(self, config):
        self.smtp_host = config['smtp_host']
        self.smtp_port = config['smtp_port']
        self.from_addr = config['from_addr']
        self.to_addr = config['to_addr']
        self.ssl = config['ssl']
        self.username = config['username']
        self.password = decrypt(config['password'])
        self.alert_interval = config['alert_interval']
    
    def __str__(self):
        return 'Email Alert to: {}'.format(self.to_addr)

    def fail(self, monitor):

        # check if the alert interval elapsed
        if (datetime.datetime.now() - monitor.alert_time).total_seconds() > self.alert_interval:
            
            # build email body
            message = MIMEMultipart()
            message['From'] = self.from_addr
            message['To'] = self.to_addr
            message['Subject'] = "[%s] Monitor %s Failed!" % (monitor.hostname, monitor.type)
            
            body = """Monitor %s%s has failed.
Failed at: %s
Error Info: %s """ % (
                monitor.hostname,
                monitor.type,
                monitor.last_fail.isoformat(' '),
                monitor.result_info)

            message.attach(MIMEText(body, 'plain'))
            
            #send email
            try:
                smtpObj = smtplib.SMTP(self.smtp_host, self.smtp_port)
                smtpObj.ehlo()
                if self.ssl:
                    smtpObj.starttls()
                smtpObj.login(self.username, self.password)

                smtpObj.sendmail(self.from_addr, self.to_addr, message.as_string())
                smtpObj.quit()

                alerts_logger.debug('Email alert sent for: {} / {}'.format(monitor.hostname, monitor.type))
                # update last alert time
                monitor.alert_time = datetime.datetime.now()

            except Exception as er:
                alerts_logger.exception('Failed to send email: {}, {}. Error: {}'.format(monitor.hostname, monitor.type, er))
            
        else:
            alerts_logger.debug('Skipping email alert, alert interval has not expired yet')


class Slack_alert(Alert):

    def __init__(self, config):
        self.webhook = decrypt(config['webhook'])
        self.headers = {"Content-type": "application/json"}
        self.alert_interval = config['alert_interval']

    def fail(self, monitor):

        # check if the alert interval elapsed
        if (datetime.datetime.now() - monitor.alert_time).total_seconds() > self.alert_interval:
            try:
                data = {"text": monitor.result_info}
                request = requests.post(self.webhook, json=data, headers=self.headers)
                request.raise_for_status()
                monitor.alert_time = datetime.datetime.now()
            except Exception as er:
                alerts_logger.error('Failed to send slack alert. Error: {}'.format(er))
        else:
            alerts_logger.debug('Skipping Slack alert, alert interval has not expired yet')
        

class Alert_Factory():
   def create_alert(self, typ):
        global_config = load_alerts()
        alert_config = global_config[typ]
        target_class = typ.capitalize() + "_alert"
        return globals()[target_class](alert_config)