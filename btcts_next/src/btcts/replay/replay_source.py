# path: ./btcts_next/src/btcts/replay/replay_source.py
# desc: JSONL replay source loader for canonical collector outputs.

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List


def _event_sort_key(record: Dict):
    event_ts = str(record.get("event_ts") or "")
    sequence_id = int(record.get("sequence_id") or 0)
    record_id = str(record.get("record_id") or "")
    return (event_ts, sequence_id, record_id)


class JsonlReplaySource:
    def __init__(self, paths: Iterable[Path]):
        self.paths = [Path(p) for p in paths]

    def load(self) -> List[Dict]:
        records: List[Dict] = []

        for path in self.paths:
            if not path.exists() or not path.is_file():
                continue

            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        record = json.loads(line)
                    except Exception:
                        continue

                    if isinstance(record, dict):
                        records.append(record)

        records.sort(key=_event_sort_key)
        return records