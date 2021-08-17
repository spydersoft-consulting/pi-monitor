import sys
import smtplib
import json
import logging

from email.message import EmailMessage

def notify(email, subject, content):

    f = open('notifications.config.json')
    configData = json.load(f)
    f.close()
    logging.debug(str.format("Sending Notifcation to ", email))
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = configData['smtp_sender_id']
    msg['To'] = email
    try:
        server = smtplib.SMTP(configData['smtp_url'], configData['smtp_port'])
        server.starttls()
        server.login(configData['smtp_sender_id'], configData['smtp_sender_pass'])
        server.send_message(msg, configData['smtp_sender_id'], email)
        server.quit()
    except:
        logging.error("Error sending notification", sys.exc_info()[0])