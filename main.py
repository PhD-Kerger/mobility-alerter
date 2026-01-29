import yaml

from alerter import Alerter
from log_collector import (
    GBFSLogCollector,
    GTFSLogCollector,
    NextbikeLogCollector,
)

from utils import DataPipelineLogger
import time
import schedule
import apprise


class LogManager:
    """Main class for managing log operations."""

    def __init__(self):
        """Initialize the LogManager with configuration and logger."""
        self.config_path = "config.yaml"
        self.config = self.load_config()

        # Extract configuration sections
        alerting = self.config.get("alerting", {})

        self.alerting_config = (
            alerting.get("alerters", {}) if alerting.get("alerters") else {}
        )
        self.log_collector_config = (
            alerting.get("log_collector", {}) if alerting.get("log_collector") else {}
        )

        self.site_name = alerting.get("site_name", "DefaultSite")
        self.daily_summary_time = alerting.get("daily_summary_time", "19:09")

        # Setup logger as class attribute
        self.logger = DataPipelineLogger.get_logger(
            name=self.__class__.__name__,
            log_file_path="log",
        )

        # Class mappings for processors and extensions
        self.log_collector_class_mapping = {
            "GBFS": GBFSLogCollector,
            "GTFS": GTFSLogCollector,
            "Nextbike": NextbikeLogCollector,
        }

    def load_config(self) -> dict:
        """Load configuration from YAML file."""
        with open(self.config_path, "r") as file:
            return yaml.safe_load(file)

    def create_log_collector(self, log_collector_config):
        """Create a log collector instance based on configuration."""
        log_collector_class = log_collector_config.get("class")

        if log_collector_class not in self.log_collector_class_mapping:
            raise ValueError(f"Unknown log collector class: {log_collector_class}")

        # Get the log collector class constructor
        LogCollectorClass = self.log_collector_class_mapping[log_collector_class]

        # Create log collector instance dynamically
        return LogCollectorClass(
            {
                "name": log_collector_config.get("name", "UnnamedLogCollector"),
                "log_file_path": log_collector_config.get("log_file", None),
            }
        )

    def create_alerter(self, alerter_config, log_collectors):
        """Create an alerter instance based on configuration."""
        alerter_name = alerter_config.get("name")
        self.alerter = Alerter(
            name=alerter_config.get("name", "UnnamedAlerter"),
            config_str=alerter_config.get("config_str", ""),
            apprise_obj=apprise.Apprise(),
            log_collectors=log_collectors,
            site_name=self.site_name,
        )
        schedule.every().day.at(self.daily_summary_time).do(
            self.alerter.send_daily_summary
        )
        self.logger.info(
            f"Scheduled {alerter_name} Daily summary at {self.daily_summary_time}"
        )

        schedule.every(1).minutes.do(self.alerter.check_errors)
        self.logger.info(f"Scheduled {alerter_name} error check every minute")

    def run(self):
        """Main method to process all configured operators and extensions."""
        log_collectors = []

        # Handle log_collector_config as a list of dictionaries
        for collector_item in self.log_collector_config:
            for _, config in collector_item.items():
                log_collectors.append(self.create_log_collector(config))

        if len(log_collectors) == 0:
            self.logger.error("No log collectors configured. Exiting.")
            return

        for alerter_item in self.alerting_config:
            for _, config in alerter_item.items():
                self.logger.info(f"Creating alerter with config: {config}")
                self.create_alerter(config, log_collectors)

        while True:
            try:
                schedule.run_pending()
                time.sleep(10)  # Check every 10 seconds
            except KeyboardInterrupt:
                self.logger.info("Shutting down LogManager.")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in scheduler: {e}")
                time.sleep(60)  # Wait a minute before retrying


def main():
    """Main function to create and run the LogManager."""
    log_manager = LogManager()
    log_manager.run()


if __name__ == "__main__":
    main()
