import sys
import smtplib
import logging
import configuration

from email.message import EmailMessage

logger = logging.getLogger(__name__)


class Notifier:
    """Notifier Class

    The Notifier class encapsulates the functionality to send email notifications.

    Attributes:
        config: An instance of [NotificationSettings][configuration.NotificationSettings]
    """
    config: configuration.NotificationSettings

    def __init__(self, notifyConfig: configuration.NotificationSettings) -> None:
        """ Constructor

        Initialize the instance using the provided [NotificationSettings][configuration.NotificationSettings].

        """
        self.config = notifyConfig

    def notify(self, subject: str, content: str):
        """ Send notification

        Build and send an email notificaiton using the provided parameters.

        Args:
            subject: The email subject.
            content: the email content.

        """
        if (self.config.smsEmail != ""):
            logger.debug("Sending Notification to %s", self.config.smsEmail)
            msg = EmailMessage()
            msg.set_content(content)
            msg['Subject'] = subject
            msg['From'] = self.config.smtp_sender_id
            msg['To'] = self.config.smsEmail
            try:
                server = smtplib.SMTP(
                    self.config.smtp_url, self.config.smtp_port)
                server.starttls()
                server.login(self.config.smtp_sender_id,
                             self.config.smtp_sender_pass)
                server.send_message(
                    msg, self.config.smtp_sender_id, self.config.smsEmail)
                server.quit()
            except:
                logger.error("Error sending notification: %s",
                             sys.exc_info()[0])
