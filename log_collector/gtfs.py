import datetime


class GTFSLogCollector:
    def __init__(self, config):
        self.config = config

        # Extract parameters from config
        self.name = config.get("name", "GTFSLogCollector")
        self.log_file_path = config.get("log_file_path", None)

        if not self.log_file_path:
            raise ValueError(
                "log_file_path must be provided in the config for GTFSLogCollector"
            )

    def get_errors(self) -> list[str]:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        with open(self.log_file_path, "r") as log_file:
            errors = []
            for line in log_file:
                if current_time in line and "ERROR" in line:
                    errors.append(line.strip())
        return errors

    def generate_daily_message(self, site_name) -> str:
        """
        Generate daily report message with table format. Message looks like:
        Report for GTFS-Collector on 2025-10-30
        Data Provider      | Fetch | Upload
        -------------------|-------|-------
        gtfs-germany       | 1     | 1
        another-operator   | 0     | 0
        """
        title = f"[{site_name} - Daily Summary {self.name} - {(datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')}]"

        # Fixed column widths for perfect alignment
        target_width = 18
        fetch_width = 5
        upload_width = 6

        header = (
            f"{'Data Provider':<{target_width}} | {'Fetch':>{fetch_width}} | {'Upload':>{upload_width}}\n"
            f"{'-' * target_width} | {'-' * fetch_width} | {'-' * upload_width}"
        )

        message = ""
        daily_metrics = self._get_daily_metrics()
        for operator, metrics in daily_metrics.items():
            fetches = metrics.get("Fetch", 0)
            uploads = metrics.get("Upload", 0)
            message += (
                f"{operator:<{target_width}} | "
                f"{fetches:>{fetch_width}} | "
                f"{uploads:>{upload_width}}\n"
            )

        final_message = f"```\n{header}\n{message}```"

        return final_message, title

    def _get_daily_metrics(self):
        """
        Metrics are structured like:
        {
            "gtfs-germany": {
                "Fetches": 10,
                "Uploads": 10
            },
            "another-operator": {
                "Fetches": 20,
                "Uploads": 18
            }
        }
        """
        # 2025-10-30 13:39:25,083 - GTFS-Collector - INFO - Starting download for target: gtfs-germany
        date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )
        with open(self.log_file_path, "r") as log_file:
            metrics = {}
            for line in log_file:
                if date in line:
                    # fetching data case
                    if "Starting download" in line:
                        try:
                            operator_name = line.split("target: ")[1]
                        except IndexError:
                            continue
                        if operator_name not in metrics:
                            metrics[operator_name] = {}
                        metrics[operator_name]["Fetch"] = (
                            metrics[operator_name].get("Fetch", 0) + 1
                        )
                    # upload successfull: 2025-10-30 17:00:46,303 - GTFS-Collector - INFO -
                    # Successfully uploaded /app/gtfs_output/gtfs-germany/1761831583.zip to SMB share in gtfs-germany folder
                    elif "Successfully uploaded" in line:
                        operator_name = line.split("share in ")[1].split(" folder")[0]
                        if operator_name not in metrics:
                            metrics[operator_name] = {}
                        metrics[operator_name]["Upload"] = (
                            metrics[operator_name].get("Upload", 0) + 1
                        )

        return metrics

    def get_name(self):
        return self.name
