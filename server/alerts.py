import smtplib
import shelve
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import pprint
import logging
#logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')



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
        self.password = config['password']
        self.alert_interval = config['alert_interval']
    

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

                # update last alert time
                monitor.alert_time = datetime.datetime.now()

            except Exception as er:
                print('Failed to send email:', monitor.hostname, monitor.type, ', Error:', er)
            
        else:
            logging.debug('Skipping email alert, alert interval has not expired yet')

class Syslog_alert(Alert):
    # TODO
    pass

class Alert_Factory():
   def create_alert(self, typ, global_config):
        alert_config = global_config[typ]
        target_class = typ.capitalize() + "_alert"
        return globals()[target_class](alert_config)
