import datetime


class NextbikeLogCollector:
    def __init__(self, config):
        self.config = config

        # Extract parameters from config
        self.name = config.get("name", "NextbikeLogCollector")
        self.log_file_path = config.get("log_file_path", None)

        if not self.log_file_path:
            raise ValueError(
                "log_file_path must be provided in the config for NextbikeLogCollector"
            )

    def get_errors(self) -> list[str]:
        current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
        date = datetime.datetime.now().strftime("%Y-%m-%d")

        with open(self.log_file_path + "/" + date + ".txt", "r") as log_file:
            errors = []
            for line in log_file:
                if current_time in line and "ERROR" in line:
                    errors.append(line.strip())
        return errors

    def generate_daily_message(self, site_name: str) -> str:
        """
        Generate daily report message with table format. Message looks like:
        Report for Nextbike-Collector on 2025-10-30
        Data Provider      | Fetch | Save | Error
        -------------------|-------|------|-------
        Germany            | 1     | 1    | 0
        Global             | 0     | 0    | 0
        """
        title = f"[{site_name} - Daily Summary {self.name} - {(datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')}]"

        # Fixed column widths for perfect alignment
        target_width = 18
        fetch_width = 5
        save_width = 4
        error_width = 5

        header = (
            f"{'Data Provider':<{target_width}} | {'Fetch':>{fetch_width}} | {'Save':>{save_width}} | {'Error':>{error_width}}\n"
            f"{'-' * target_width} | {'-' * fetch_width} | {'-' * save_width} | {'-' * error_width}"
        )

        message = ""
        daily_metrics = self._get_daily_metrics()
        for operator, metrics in daily_metrics.items():
            fetches = metrics.get("Fetch", 0)
            saves = metrics.get("Save", 0)
            errors = metrics.get("Error", 0)
            message += (
                f"{operator:<{target_width}} | "
                f"{fetches:>{fetch_width}} | "
                f"{saves:>{save_width}} | "
                f"{errors:>{error_width}}\n"
            )

        final_message = f"```\n{header}\n{message}```"

        return final_message, title

    def _get_daily_metrics(self):
        """
        Metrics are structured like:
        {
            "Global": {
                "Fetch": 10,
                "Save": 10,
                "Error": 0
            },
            "Germany": {
                "Fetch": 20,
                "Save": 18,
                "Error": 0
            }
        }
        """
        date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )
        with open(self.log_file_path + "/" + date + ".txt", "r") as log_file:
            metrics = {}
            for line in log_file:
                if date in line:
                    # 2025-10-31T10:15:00.11534971Z INFO msg=Starting scraping job
                    # target=Germany url=https://maps.nextbike.net/maps/nextbike-live.json?countries=DE
                    try:
                        operator_name = line.split("[")[1].split("]")[0]
                        # Skip non-operator lines
                        if operator_name in [
                            "Scraper",
                            "Compactor",
                            "Samba Move",
                            "Scraping Cron",
                        ]:
                            continue
                    except IndexError:
                        continue
                    if operator_name not in metrics:
                        metrics[operator_name] = {}
                    # fetching a feed case
                    if "Starting scraping job" in line:
                        metrics[operator_name]["Fetch"] = (
                            metrics[operator_name].get("Fetch", 0) + 1
                        )
                    # Successfully saved scraped data path=/app/output-json/Germany/2025-10-31/1761905701.json
                    elif "Successfully saved scraped data" in line:
                        metrics[operator_name]["Save"] = (
                            metrics[operator_name].get("Save", 0) + 1
                        )
                    elif "ERROR" in line:
                        metrics[operator_name]["Error"] = (
                            metrics[operator_name].get("Error", 0) + 1
                        )

        return metrics

    def get_name(self):
        return self.name
