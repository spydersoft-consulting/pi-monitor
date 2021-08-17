import sys
import smtplib
import json
import logging
from pathlib import Path

from email.message import EmailMessage

def notify(subject, content):

    config_file = Path('notifications.config.json')

    if (not config_file.exists()):
        return

    f = open('notifications.config.json')
    configData = json.load(f)
    f.close()

    if (configData['smsEmail']):
        logging.debug(str.format("Sending Notifcation to ", configData['smsEmail']))
        msg = EmailMessage()
        msg.set_content(content)
        msg['Subject'] = subject
        msg['From'] = configData['smtp_sender_id']
        msg['To'] = configData['smsEmail']
        try:
            server = smtplib.SMTP(configData['smtp_url'], configData['smtp_port'])
            server.starttls()
            server.login(configData['smtp_sender_id'], configData['smtp_sender_pass'])
            server.send_message(msg, configData['smtp_sender_id'], configData['smsEmail'])
            server.quit()
        except:
            logging.error("Error sending notification", sys.exc_info()[0])