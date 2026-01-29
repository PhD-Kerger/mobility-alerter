from utils import DataPipelineLogger
from log_collector import GBFSLogCollector, GTFSLogCollector, NextbikeLogCollector


class Alerter:
    """Alerter for sending messages"""

    def __init__(
        self,
        name,
        config_str: str,
        apprise_obj,
        log_collectors: list[
            GBFSLogCollector | GTFSLogCollector | NextbikeLogCollector
        ],
        site_name: str,
    ):
        """e
        Initialize Alerter instance

        Args:
            config_str: Configuration string for the alerter
            log_collectors: List of log collectors to monitor
        """
        self.name = name
        self.logger = DataPipelineLogger(name)
        self.log_collectors = log_collectors
        self.site_name = site_name
        self.apprise_obj = apprise_obj

        self.apprise_obj.add(config_str)

        self.send_initial_message()

    def check_errors(self):
        for log_collector in self.log_collectors:
            errors = log_collector.get_errors()
            if errors:
                message = (
                    f"[\n".join(errors)
                )
                self.apprise_obj.notify(
                    body=message,
                    title=f"[{self.site_name} - {log_collector.get_name()}]",
                )

    def send_message(self, message, title=None):
        """
        Send a message

        Args:
            message: Text message to send

        Raises:
            ValueError: If no channel is specified
            Exception: If Slack API call fails
        """
        try:
            self.apprise_obj.notify(
                body=message,
                title=title or f"[{self.site_name}] Mobility Alerter Notification",
            )

            self.logger.info("Message sent successfully")

        except Exception as e:
            error_msg = f"Failed to send message: {str(e)}"
            self.logger.error(error_msg)

    def send_daily_summary(self):
        """
        Generate and send daily tracking message to the daily channel
        """
        for log_collector in self.log_collectors:
            daily_summary, title = log_collector.generate_daily_message(self.site_name)
            if daily_summary:
                self.send_message(daily_summary, title=title)

    def send_initial_message(self):
        """
        Send an initial message indicating that the alerter is active
        """
        initial_message = f"Mobility Alerter is now active."
        self.send_message(initial_message)
