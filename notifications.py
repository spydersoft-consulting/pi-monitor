from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
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
            
            message = Mail(
            from_email=self.config.smtp_sender_id,
            to_emails=self.config.smsEmail,
            subject=subject,
            plain_text_content=content,
            html_content=content)
            try:
                sg = SendGridAPIClient(self.config.smtp_sender_apikey)
                response = sg.send(message)
            except Exception as e:
                print(e.message)
