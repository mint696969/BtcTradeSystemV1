# path: ./btcts_next/src/btcts/quality/anomaly.py
# desc: derived/daily の日次集計から、429/再起動/health等の異常サマリ anomaly_YYYYMMDD.json を生成する。

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from btcts.core import io, paths


def run_anomaly() -> Optional[Path]:
    logs_dir = paths.logs_dir()
    derived_dir = logs_dir / "derived"
    quality_dir = logs_dir / "quality"
    quality_dir.mkdir(parents=True, exist_ok=True)

    daily_files = sorted(derived_dir.glob("daily_*.json"))
    if not daily_files:
        return None

    latest = daily_files[-1]
    row = io.read_json(latest)

    day = row.get("day") or latest.name.removeprefix("daily_").removesuffix(".json")

    collector = row.get("collector") if isinstance(row.get("collector"), dict) else {}
    http = collector.get("http") if isinstance(collector.get("http"), dict) else {}
    health = row.get("health") if isinstance(row.get("health"), dict) else {}

    status_429 = int(http.get("status_429") or 0)
    restarts = int(collector.get("proc_restart_count") or 0)
    health_crit = int(health.get("crit_count") or 0)

    out: Dict[str, Any] = {
        "day": str(day),
        "source_daily": latest.name,
        "counts": {
            "status_429": status_429,
            "collector_restarts": restarts,
            "health_crit": health_crit,
        },
        "signals": {
            "http_429_spike": status_429 > 10,
            "restart_spike": restarts > 5,
            "health_crit": health_crit,
        },
        "generated_utc": datetime.now(timezone.utc).isoformat(),
    }

    out_file = quality_dir / f"anomaly_{day}.json"
    io.write_json(out_file, out, indent=2, sort_keys=True)
    return out_file


if __name__ == "__main__":
    p = run_anomaly()
    print(f"OK quality_anomaly: {p}")
