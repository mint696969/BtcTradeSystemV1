# path: ./btcts_next/src/btcts/quality/anomaly.py
# desc: derived/daily の日次集計から、429/再起動/health等の異常サマリ anomaly_YYYYMMDD.json を生成する。

from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
from btcts.core import paths, io


def run_anomaly():

    logs_dir = paths.logs_dir()

    derived = logs_dir / "derived"
    quality = logs_dir / "quality"

    quality.mkdir(parents=True, exist_ok=True)

    daily_files = sorted(derived.glob("daily_*.json"))

    if not daily_files:
        return None

    latest = daily_files[-1]

    row = io.read_json(latest)

    http = row.get("collector", {}).get("http", {})

    anomaly = {

        "day": row.get("day"),

        "429_spike": http.get("status_429", 0) > 10,

        "restart_spike": row.get("collector", {}).get("proc_restart_count", 0) > 5,

        "health_crit": row.get("health", {}).get("crit_count", 0),

        "generated_utc": datetime.now(timezone.utc).isoformat()
    }

    out = quality / f"anomaly_{row.get('day')}.json"

    io.write_json(out, anomaly, indent=2, sort_keys=True)

    return out


if __name__ == "__main__":
    p = run_anomaly()
    print(f"OK quality_anomaly: {p}")