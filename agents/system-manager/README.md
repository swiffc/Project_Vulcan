# System Manager - David's Worker

Background daemon for job scheduling, backups, health monitoring, and metrics collection.

## Features

- **Scheduler**: Cron-like job scheduling
- **Backup Service**: Automated backups to Google Drive
- **Health Monitor**: Service health checks
- **Metrics Collector**: System and agent metrics

## Usage

```bash
# From project root
cd agents/system-manager
pip install -r requirements.txt
python -m src.main
```

## Scheduled Jobs

| Job | Schedule | Description |
|-----|----------|-------------|
| Daily Backup | 02:00 UTC | Backup storage to Google Drive |
| Health Check | Hourly | Check all service health |
| Metrics | Every 5 min | Collect system metrics |
| Weekly Report | Friday 17:00 | Generate performance report |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `WEB_URL` | Vulcan web interface URL |
| `DESKTOP_SERVER_URL` | Desktop MCP server URL |
| `MEMORY_SERVER_URL` | Memory Brain server URL |
| `GOOGLE_DRIVE_CREDENTIALS` | Path to Drive credentials |

## Architecture

```
system-manager/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── scheduler.py         # Job scheduling
│   ├── backup.py            # Drive backups
│   ├── health_monitor.py    # Service health
│   └── metrics_collector.py # System metrics
├── config/
│   └── jobs.json            # Job configurations
├── requirements.txt
└── README.md
```
