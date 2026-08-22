# Automated Cloud Infrastructure Monitoring & Incident Alert Tool

A local simulation of cloud infrastructure monitoring and incident alerting using Python, Bash, Azure CLI-style resource modeling, SQLite/PostgreSQL/MySQL-compatible SQL concepts, cron scheduling, and logging.

## What it demonstrates
- Monitoring 5 simulated VM/database instances every 60 seconds
- CPU, memory, disk, connectivity, and service-health checks
- Persistent state-change logging in a local SQLite database
- Classification of disk, connectivity, and service-down incidents
- Email/webhook-style alert delivery
- Four reproducible outage scenarios
- CLI reports for health and incidents

## Run
```bash
python src/monitor.py --once
python src/monitor.py --scenario disk
python src/monitor.py --scenario connectivity
python src/monitor.py --scenario service_down
python src/monitor.py --scenario cpu
python src/report.py
```

For repeated polling, use the included cron example in `cron/monitor.cron`.

> This repository intentionally uses simulated infrastructure so it can run without an Azure subscription.
