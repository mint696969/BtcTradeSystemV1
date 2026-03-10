# path: ./btcts_next/src/btcts/quality/gaps.py
# desc: derived/hourly の topics.max_age_sec を閾値判定し、欠損候補を gaps_YYYYMMDD_HH.jsonl に列挙する。

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from btcts.core import io, paths


THRESHOLD_SEC = 10


def run_gaps() -> Optional[Path]:
    logs_dir = paths.logs_dir()
    derived_dir = logs_dir / "derived"
    quality_dir = logs_dir / "quality"
    quality_dir.mkdir(parents=True, exist_ok=True)

    hourly_files = sorted(derived_dir.glob("hourly_*.json"))
    if not hourly_files:
        return None

    latest = hourly_files[-1]
    row = io.read_json(latest)

    collector = row.get("collector") if isinstance(row.get("collector"), dict) else {}
    topics = collector.get("topics") if isinstance(collector.get("topics"), dict) else {}

    hour_key = latest.name.removeprefix("hourly_").removesuffix(".json")
    out_file = quality_dir / f"gaps_{hour_key}.jsonl"

    with out_file.open("w", encoding="utf-8") as f:
        for topic, v in topics.items():
            if not isinstance(v, dict):
                continue
            age = v.get("max_age_sec")
            try:
                age_f = float(age) if age is not None else None
            except Exception:
                age_f = None

            if age_f is None or age_f <= THRESHOLD_SEC:
                continue

            gap: Dict[str, Any] = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "topic": str(topic),
                "gap_sec": age_f,
                "threshold_sec": THRESHOLD_SEC,
                "last_ok_ts": v.get("last_ok_ts"),
                "max_retries": v.get("max_retries"),
                "ok_count": v.get("ok_count"),
                "err_count": v.get("err_count"),
                "source_hourly": latest.name,
            }
            f.write(json.dumps(gap, ensure_ascii=False) + "\n")

    return out_file


if __name__ == "__main__":
    p = run_gaps()
    print(f"OK quality_gaps: {p}")
