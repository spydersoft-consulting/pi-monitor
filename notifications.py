import sys
import smtplib
import logging
import configuration

from email.message import EmailMessage

logger = logging.getLogger(__name__)

class Notifier:
    config: configuration.NotificationSettings

    def __init__(self, notifyConfig: configuration.NotificationSettings ) -> None:
        self.config = notifyConfig

    def notify(self, subject, content):

        if (self.config.smsEmail != ""):
            logger.debug("Sending Notification to %s", self.config.smsEmail)
            msg = EmailMessage()
            msg.set_content(content)
            msg['Subject'] = subject
            msg['From'] = self.config.smtp_sender_id
            msg['To'] = self.config.smsEmail
            try:
                server = smtplib.SMTP(self.config.smtp_url, self.config.smtp_port)
                server.starttls()
                server.login(self.config.smtp_sender_id, self.config.smtp_sender_pass)
                server.send_message(msg, self.config.smtp_sender_id, self.config.smsEmail)
                server.quit()
            except:
                logger.error("Error sending notification: %s", sys.exc_info()[0])