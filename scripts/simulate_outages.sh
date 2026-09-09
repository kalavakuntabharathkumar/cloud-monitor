#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
for scenario in disk connectivity service_down cpu; do
  echo "=== $scenario ==="
  python3 src/monitor.py --scenario "$scenario"
done
