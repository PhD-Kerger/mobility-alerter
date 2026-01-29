import datetime


class GBFSLogCollector:
    def __init__(self, config):
        self.config = config

        # Extract parameters from config
        self.name = config.get("name", "GBFSLogCollector")
        self.log_file_path = config.get("log_file_path", None)

        if not self.log_file_path:
            raise ValueError(
                "log_file_path must be provided in the config for GBFSLogCollector"
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
        Generate daily report message with focus on "main". Message looks like:
        Report for GBFS-Collector on 2025-10-30
        Provider           | Saves  | Skips  | Errors | Others
        -------------------|--------|--------|--------|-------
        Dott_Muenster      | 725    | 722    | 0      | 0
        Dott_Leipzig       | 724    | 722    | 0      | 0
        Dott_Boeblingen    | 726    | 721    | 0      | 0
        Dott_Mannheim      | 726    | 721    | 0      | 0
        Dott_Stuttgart     | 724    | 723    | 0      | 0
        Dott_Karlsruhe     | 726    | 719    | 1      | 1
        Dott_Heidelberg    | 722    | 725    | 0      | 0
        Lime_Stuttgart     | 922    | 522    | 2      | 2
        Stella             | 877    | 567    | 2      | 2
        Bolt_Karlsruhe     | 263    | 1181   | 2      | 2
        Bolt_Stuttgart     | 263    | 1181   | 2      | 2
        Zeus_Heidelberg    | 1434   | 10     | 2      | 2
        Call_a_Bike        | 525    | 919    | 2      | 2
        RegioRadStuttgart  | 494    | 950    | 2      | 2
        Voi                | 1414   | 30     | 2      | 2

        """
        title = f"[{site_name} - Daily Summary {self.name} - {(datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')}]"
        
        # Fixed column widths for perfect alignment
        provider_width = 18
        saves_width = 4
        skips_width = 4
        errors_width = 5
        others_width = 5
        
        header = (
            f"{'Data Provider':<{provider_width}} | {'Save':>{saves_width}} | {'Skip':>{skips_width}} | {'Error':>{errors_width}} | {'Other':<{others_width}}\n"
            f"{'-' * provider_width} | {'-' * saves_width} | {'-' * skips_width} | {'-' * errors_width} | {'-' * others_width}"
        )

        message = ""
        daily_metrics = self._get_daily_metrics()
        for operator, feeds in daily_metrics.items():
            operator_name = operator.replace("_", " ")
            main_metrics = feeds.get("main", {})
            other_metrics = feeds.get("others", {})
            message += (
                f"{operator_name:<{provider_width}} | "
                f"{main_metrics.get('Saves', 0):>{saves_width}} | "
                f"{main_metrics.get('Skips', 0):>{skips_width}} | "
                f"{main_metrics.get('Errors', 0):>{errors_width}} | "
                f"{other_metrics.get('Saves', 0)}/{other_metrics.get('Skips', 0)}/{other_metrics.get('Errors', 0)}\n"
            )
            
        final_message = f"```\n{header}\n{message}```"

        return final_message, title

    def _get_daily_metrics(self):
        """
        Metrics are structured like:
        {
            "Lime Stuttgart": {
                "main": {
                    "Saves": 10,
                    "Skips": 2,
                    "Errors": 1
                },
                "others": {
                    "Saves": 8,
                    "Skips": 0,
                    "Errors": 0
                }
            },
            "Another Operator": {
                ...
            }
        }
        """
        # 2025-10-31T09:48:00.026899886Z INFO msg=[Lime Stuttgart] Fetching feed feed=
        # free_bike_status url=https://gbfs.api.ridedott.com/public/v2/karlsruhe/free_bike_status.json
        date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )
        with open(self.log_file_path + "/" + date + ".txt", "r") as log_file:
            metrics = {}
            for line in log_file:
                if date in line:
                    # get the operator name between []
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
                    feed_name = line.split('feed":"')[1].split('"')[0]
                    if feed_name in ["vehicle_status", "free_bike_status"]:
                        feed_name = "main"
                    else:
                        feed_name = "others"
                    if feed_name not in metrics[operator_name]:
                        metrics[operator_name][feed_name] = {}

                    if "Successfully scraped feed" in line:
                        metrics[operator_name][feed_name]["Saves"] = (
                            metrics[operator_name].get(feed_name, {}).get("Saves", 0)
                            + 1
                        )
                    elif "Skipping feed" in line:
                        metrics[operator_name][feed_name]["Skips"] = (
                            metrics[operator_name].get(feed_name, {}).get("Skips", 0)
                            + 1
                        )
                    elif "ERROR" in line:
                        metrics[operator_name][feed_name]["Errors"] = (
                            metrics[operator_name].get(feed_name, {}).get("Errors", 0)
                            + 1
                        )

        return metrics

    def get_name(self):
        return self.name
