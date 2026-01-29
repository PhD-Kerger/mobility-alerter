# Mobility Alerter

A monitoring and alerting system for mobility data collection pipelines. This tool automatically monitors log files from various mobility data collectors (GBFS, GTFS, Nextbike) and provides real-time error alerts and daily summary reports through Slack and email notifications.

## Features

- **Multi-Collector Support**: Monitors GBFS, GTFS, and Nextbike data collection pipelines
- **Real-time Error Monitoring**: Instant alerts when errors are detected in log files
- **Daily Summary Reports**: Automated daily reports with collection statistics and metrics
- **Multiple Alert Channels**: Support for both Slack and SMTP email notifications
- **Flexible Configuration**: YAML-based configuration with hot-reload capabilities
- **Production Ready**: Dockerized with comprehensive logging and error handling
- **Scheduled Operations**: Configurable timing for daily summaries and error checks

## Supported Data Collectors

The alerter can monitor any mobility data collection system that produces structured log files. Currently supported collectors include:

### GBFS Collector

- Monitors General Bikeshare Feed Specification data collection
- Tracks feed fetch/skip statistics per operator and feed type
- Supports both v2.3 and v3.0 GBFS specifications

### GTFS Collector

- Monitors General Transit Feed Specification data collection
- Tracks transit data collection metrics and status

### Nextbike Collector

- Monitors Nextbike-specific data collection pipelines
- Provides specialized metrics for bike-sharing operations

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for development)
- Access to log files from your data collection pipelines

### Configuration

1. Copy the example configuration:

   ```bash
   cp config.example.yaml config.yaml
   ```

2. Edit `config.yaml` with your alerting preferences:

   ```yaml
   alerting:
     slack:
       enabled: true
       token: "xoxb-your-slack-bot-token"
       daily_summary_time: "12:00"
       channels:
         daily: "#daily-tracker"     # Channel for daily summaries
         alerts: "#alerts"           # Channel for error alerts
     
     smtp:
       enabled: false
       daily_summary_time: "12:00"
       server: "smtp.gmail.com"
       port: 587
       username: "your-email@gmail.com"
       password: "your-app-password"
       from_email: "your-email@gmail.com"
       to_email: "admin@yourcompany.com"
     
     log_collector:
       - GBFS:
           name: "GBFS Collector"
           class: "GBFS"
           log_file: "logs/gbfs_collector/log"
       - GTFS:
           name: "GTFS Collector"  
           class: "GTFS"
           log_file: "logs/gtfs_collector/log"
       - Nextbike:
           name: "Nextbike Collector"
           class: "Nextbike"
           log_file: "logs/nextbike_collector/log"
   ```

### Running with Docker

1. Build the image:

   ```bash
   docker build -t mobility-alerter:latest .
   ```

2. Run with Docker Compose:

   ```bash
   docker-compose up -d
   ```

### Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/PhD-Kerger/mobility-alerter.git
   cd mobility-alerter
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure your settings:

   ```bash
   cp config.example.yaml config.yaml
   # Edit config.yaml with your settings
   ```

4. Run the application:

   ```bash
   python main.py
   ```

## Architecture

### Alert Flow

```text
Log Files → Log Collectors → Error Detection → Alert Channels (Slack/Email)
         → Daily Metrics → Summary Reports → Alert Channels (Slack/Email)
```

1. **Log Monitoring**: Continuous monitoring of configured log files
2. **Error Detection**: Real-time scanning for ERROR level messages
3. **Metric Collection**: Aggregation of daily statistics and performance metrics
4. **Alert Dispatch**: Immediate error notifications and scheduled summaries

### Slack Configuration

To set up Slack notifications:

1. Create a Slack app in your workspace
2. Add a bot token with `chat:write` permissions
3. Invite the bot to your notification channels
4. Add the token to your configuration

### SMTP Configuration

For email notifications, configure your SMTP settings.

### Log Collector Configuration

Each log collector monitors specific log file patterns:

- **Path**: Absolute path to the log file
- **Class**: Collector type (GBFS, GTFS, Nextbike)
- **Name**: Human-readable identifier for reports

#### Error Alerts

- **Frequency**: Every minute scan for ERROR level messages
- **Content**: Full error message with timestamp and context
- **Channels**: Sent to configured alert channels

#### Daily Summaries

- **Timing**: Configurable daily summary time (default: 12:00)
- **Content**: Collection statistics, success/failure rates, operator metrics
- **Format**: Structured reports with feed-specific breakdowns

Example daily summary:

```text
Report for GBFS Collector on 2024-11-01

Lime Stuttgart:
• vehicle_status: Fetch: 1440 | Skip: 0
• station_information: Fetch: 24 | Skip: 0

Dott Mannheim:  
• free_bike_status: Fetch: 1435 | Skip: 5
• system_information: Fetch: 24 | Skip: 0
```