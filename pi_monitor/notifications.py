from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging
from .configuration import NotificationSettings

logger = logging.getLogger(__name__)


class Notifier:
    """Notifier Class

    The Notifier class encapsulates the functionality to send email notifications.

    Attributes:
        config: An instance of [NotificationSettings][NotificationSettings]
    """

    config: NotificationSettings

    def __init__(self, notify_config: NotificationSettings) -> None:
        """Constructor

        Initialize the instance using the provided
        [NotificationSettings][NotificationSettings].

        """
        self.config = notify_config

    def notify(self, subject: str, content: str):
        """Send notification

        Build and send an email notificaiton using the provided parameters.

        Args:
            subject: The email subject.
            content: the email content.

        """
        if self.config.sms_email != "":
            logger.debug("Sending Notification to %s", self.config.sms_email)

            message = Mail(
                from_email=self.config.smtp_sender_id,
                to_emails=self.config.sms_email,
                subject=subject,
                plain_text_content=content,
                html_content=content,
            )
            try:
                sg = SendGridAPIClient(self.config.smtp_sender_apikey)
                sg.send(message)
            except Exception as e:
                print(e.message)
