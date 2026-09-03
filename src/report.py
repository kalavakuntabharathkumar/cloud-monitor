import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "monitoring.db"

with sqlite3.connect(DB) as c:
    print("\nRecent incidents:")
    for row in c.execute("""SELECT ts, instance, category, detail, severity
                            FROM incidents ORDER BY id DESC LIMIT 20"""):
        print(" | ".join(map(str, row)))
