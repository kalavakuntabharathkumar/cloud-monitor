# Architecture

Scheduler/cron -> Python monitor -> simulated VM/database inventory -> metric checks -> SQLite event store -> incident classifier -> email/webhook alert adapter -> reporting.

The core monitor is independent of Azure credentials. Azure CLI can be used in a real deployment to replace the simulated inventory with Azure resource discovery and metric collection.
