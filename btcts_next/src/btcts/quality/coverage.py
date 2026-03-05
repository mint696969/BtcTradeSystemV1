# path: ./btcts_next/src/btcts/quality/coverage.py
# desc: derived/hourly の最新1時間サマリから、GPT判定用の coverage_YYYYMMDD_HH.json を生成する。

from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone
from btcts.core import paths, io


def run_coverage() -> Path:

    logs_dir = paths.logs_dir()
    derived = logs_dir / "derived"
    quality = logs_dir / "quality"

    quality.mkdir(parents=True, exist_ok=True)

    hourly_files = sorted(derived.glob("hourly_*.json"))
    if not hourly_files:
        raise RuntimeError("no hourly summaries found")

    latest = hourly_files[-1]

    row = io.read_json(latest)

    http = row.get("collector", {}).get("http", {})
    watchdog = row.get("watchdog", {})
    health = row.get("health", {})

    total = int(http.get("total", 0))
    ok = int(http.get("status_2xx", 0))

    ok_rate = ok / total if total > 0 else 0

    status = "OK"

    if http.get("status_429", 0) > 0:
        status = "WARN"

    if health.get("crit_count", 0) > 0:
        status = "CRIT"

    out = {

        "ts_start": row.get("ts_start"),
        "ts_end": row.get("ts_end"),

        "collector": {
            "ok_rate": ok_rate,
            "http_429": http.get("status_429", 0),
            "restarts": row.get("collector", {}).get("proc_restart_count", 0)
        },

        "watchdog": {
            "restarts": watchdog.get("restart_count", 0),
            "hang_detected": watchdog.get("hang_detected_count", 0)
        },

        "health": {
            "warn": health.get("warn_count", 0),
            "crit": health.get("crit_count", 0)
        },

        "status": status,

        "generated_utc": datetime.now(timezone.utc).isoformat()
    }

    hour = latest.name.replace("hourly_", "").replace(".json", "")

    out_file = quality / f"coverage_{hour}.json"

    io.write_json(out_file, out, indent=2, sort_keys=True)

    return out_file


if __name__ == "__main__":
    p = run_coverage()
    print(f"OK quality_coverage: {p}")