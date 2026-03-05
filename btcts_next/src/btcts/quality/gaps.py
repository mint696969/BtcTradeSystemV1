# path: ./btcts_next/src/btcts/quality/gaps.py
# desc: derived/hourly の topics.max_age_sec を閾値判定し、欠損候補を gaps_YYYYMMDD_HH.jsonl に列挙する。

from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone
from btcts.core import paths, io


THRESHOLD_SEC = 10


def run_gaps():

    logs_dir = paths.logs_dir()

    derived = logs_dir / "derived"
    quality = logs_dir / "quality"

    quality.mkdir(parents=True, exist_ok=True)

    hourly_files = sorted(derived.glob("hourly_*.json"))

    if not hourly_files:
        return None

    latest = hourly_files[-1]

    row = io.read_json(latest)

    topics = row.get("collector", {}).get("topics", {})

    hour = latest.name.replace("hourly_", "").replace(".json", "")

    out = quality / f"gaps_{hour}.jsonl"

    with open(out, "w", encoding="utf-8") as f:

        for topic, v in topics.items():

            age = v.get("max_age_sec")

            if age and age > THRESHOLD_SEC:

                gap = {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "topic": topic,
                    "gap_sec": age
                }

                f.write(json.dumps(gap) + "\n")

    return out


if __name__ == "__main__":
    p = run_gaps()
    print(f"OK quality_gaps: {p}")