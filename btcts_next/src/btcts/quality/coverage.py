# path: ./btcts_next/src/btcts/quality/coverage.py
# desc: derived/hourly の最新1時間サマリから、GPT判定用の coverage_YYYYMMDD_HH.json を生成する。

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from btcts.core import io, paths


def _top_topics(row: Dict[str, Any], *, limit: int = 5) -> List[Dict[str, Any]]:
    col = row.get("collector") if isinstance(row.get("collector"), dict) else {}
    topics = col.get("topics") if isinstance(col.get("topics"), dict) else {}

    items: List[Dict[str, Any]] = []
    for name, v in topics.items():
        if not isinstance(v, dict):
            continue
        items.append(
            {
                "topic": str(name),
                "max_age_sec": v.get("max_age_sec"),
                "ok_count": v.get("ok_count"),
                "err_count": v.get("err_count"),
                "max_retries": v.get("max_retries"),
                "last_ok_ts": v.get("last_ok_ts"),
            }
        )

    def key(it: Dict[str, Any]) -> float:
        try:
            return float(it.get("max_age_sec") or 0.0)
        except Exception:
            return 0.0

    items.sort(key=key, reverse=True)
    return items[: int(limit)]


def run_coverage() -> Path:
    logs_dir = paths.logs_dir()
    derived_dir = logs_dir / "derived"
    quality_dir = logs_dir / "quality"
    quality_dir.mkdir(parents=True, exist_ok=True)

    hourly_files = sorted(derived_dir.glob("hourly_*.json"))
    if not hourly_files:
        raise RuntimeError("no derived/hourly_*.json found")

    latest = hourly_files[-1]
    row = io.read_json(latest)

    collector = row.get("collector") if isinstance(row.get("collector"), dict) else {}
    http = collector.get("http") if isinstance(collector.get("http"), dict) else {}
    watchdog = row.get("watchdog") if isinstance(row.get("watchdog"), dict) else {}
    health = row.get("health") if isinstance(row.get("health"), dict) else {}

    total = int(http.get("total") or 0)
    ok2xx = int(http.get("status_2xx") or 0)
    ok_rate = (ok2xx / total) if total > 0 else 0.0

    has_429 = int(http.get("status_429") or 0) > 0
    has_health_crit = int(health.get("crit_count") or 0) > 0

    status = "OK"
    if has_429:
        status = "WARN"
    if has_health_crit:
        status = "CRIT"

    hour_key = latest.name.removeprefix("hourly_").removesuffix(".json")
    out_file = quality_dir / f"coverage_{hour_key}.json"

    out: Dict[str, Any] = {
        "ts_start": row.get("ts_start"),
        "ts_end": row.get("ts_end"),
        "mode": row.get("mode"),
        "source_hourly": latest.name,
        "collector": {
            "ok_rate": ok_rate,
            "http": {
                "total": int(http.get("total") or 0),
                "status_2xx": int(http.get("status_2xx") or 0),
                "status_4xx": int(http.get("status_4xx") or 0),
                "status_5xx": int(http.get("status_5xx") or 0),
                "status_429": int(http.get("status_429") or 0),
                "retry_after_max_sec": http.get("retry_after_max_sec"),
            },
            "restarts": int(collector.get("proc_restart_count") or 0),
        },
        "topics_top": _top_topics(row, limit=5),
        "watchdog": {
            "restarts": int(watchdog.get("restart_count") or 0),
            "hang_detected": int(watchdog.get("hang_detected_count") or 0),
        },
        "health": {
            "warn": int(health.get("warn_count") or 0),
            "crit": int(health.get("crit_count") or 0),
        },
        "status": status,
        "status_reason": {
            "has_429": has_429,
            "has_health_crit": has_health_crit,
        },
        "generated_utc": datetime.now(timezone.utc).isoformat(),
    }

    io.write_json(out_file, out, indent=2, sort_keys=True)
    return out_file


if __name__ == "__main__":
    p = run_coverage()
    print(f"OK quality_coverage: {p}")
