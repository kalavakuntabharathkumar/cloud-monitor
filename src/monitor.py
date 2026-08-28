import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "monitoring.db"
LOG = Path(__file__).resolve().parents[1] / "logs" / "monitor.log"

BASE = [
    {"name": "vm-web-01", "type": "vm", "cpu": 34, "memory": 48, "disk": 51, "connectivity": True, "service": True},
    {"name": "vm-api-01", "type": "vm", "cpu": 42, "memory": 57, "disk": 46, "connectivity": True, "service": True},
    {"name": "db-primary", "type": "database", "cpu": 61, "memory": 64, "disk": 68, "connectivity": True, "service": True},
    {"name": "db-reporting", "type": "database", "cpu": 38, "memory": 52, "disk": 73, "connectivity": True, "service": True},
    {"name": "vm-worker-01", "type": "vm", "cpu": 47, "memory": 59, "disk": 43, "connectivity": True, "service": True},
]

THRESHOLDS = {"cpu": 85, "memory": 85, "disk": 90}

def init():
    DB.parent.mkdir(exist_ok=True)
    LOG.parent.mkdir(exist_ok=True)
    with sqlite3.connect(DB) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS health_events(
            id INTEGER PRIMARY KEY, ts TEXT, instance TEXT, metric TEXT,
            value TEXT, status TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS incidents(
            id INTEGER PRIMARY KEY, ts TEXT, instance TEXT, category TEXT,
            detail TEXT, severity TEXT)""")

def apply_scenario(rows, scenario):
    rows = [dict(x) for x in rows]
    if scenario == "disk":
        rows[2]["disk"] = 97
    elif scenario == "connectivity":
        rows[1]["connectivity"] = False
    elif scenario == "service_down":
        rows[3]["service"] = False
    elif scenario == "cpu":
        rows[4]["cpu"] = 96
    elif scenario == "memory":
        rows[0]["memory"] = 94
    return rows

def classify(row):
    incidents = []
    if not row["connectivity"]:
        incidents.append(("connectivity", "Connectivity check failed", "high"))
    if not row["service"]:
        incidents.append(("service_down", "Service health check failed", "high"))
    for metric, limit in THRESHOLDS.items():
        if row[metric] >= limit:
            incidents.append((metric, f"{metric} threshold breached: {row[metric]}%", "medium"))
    return incidents

def alert(instance, category, detail):
    payload = {"instance": instance, "category": category, "detail": detail}
    print("ALERT:", json.dumps(payload))

def run(scenario="none"):
    init()
    rows = apply_scenario(BASE, scenario)
    ts = datetime.now().isoformat(timespec="seconds")
    with sqlite3.connect(DB) as c:
        for row in rows:
            metrics = ["cpu", "memory", "disk"]
            for metric in metrics:
                status = "BREACH" if row[metric] >= THRESHOLDS[metric] else "OK"
                c.execute("INSERT INTO health_events(ts,instance,metric,value,status) VALUES(?,?,?,?,?)",
                          (ts, row["name"], metric, str(row[metric]), status))
            for metric, value in [("connectivity", row["connectivity"]), ("service", row["service"])]:
                c.execute("INSERT INTO health_events(ts,instance,metric,value,status) VALUES(?,?,?,?,?)",
                          (ts, row["name"], metric, str(value), "OK" if value else "DOWN"))
            for category, detail, severity in classify(row):
                c.execute("INSERT INTO incidents(ts,instance,category,detail,severity) VALUES(?,?,?,?,?)",
                          (ts, row["name"], category, detail, severity))
                alert(row["name"], category, detail)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{ts} scenario={scenario} monitored={len(rows)}\n")
    print(f"Monitored {len(rows)} instances; scenario={scenario}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--scenario", choices=["none", "disk", "connectivity", "service_down", "cpu", "memory"], default="none")
    p.add_argument("--once", action="store_true")
    args = p.parse_args()
    run(args.scenario)
