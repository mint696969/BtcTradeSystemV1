# path: ./btcts_next/src/btcts/replay/replay_engine.py
# desc: Minimal replay engine that iterates through canonical records in time order.

from __future__ import annotations

import time
from typing import Dict, List, Optional

from .replay_clock import ReplayClock


def _parse_event_ts(record: Dict) -> str:
    return str(record.get("event_ts") or "")


class ReplayEngine:
    def __init__(self, records: List[Dict], clock: Optional[ReplayClock] = None):
        self.records = records
        self.clock = clock or ReplayClock()
        self.index = 0

    def has_next(self) -> bool:
        return self.index < len(self.records)

    def reset(self) -> None:
        self.index = 0

    def seek(self, index: int) -> None:
        if index < 0:
            index = 0
        if index > len(self.records):
            index = len(self.records)
        self.index = index

    def current(self) -> Optional[Dict]:
        if not self.has_next():
            return None
        return self.records[self.index]

    def next_event(self) -> Optional[Dict]:
        if not self.has_next():
            return None

        if self.clock.paused:
            return None

        record = self.records[self.index]
        self.index += 1
        return record

    def play_step(self) -> Optional[Dict]:
        if not self.has_next():
            return None

        if self.clock.paused:
            return None

        current = self.records[self.index]

        if self.index > 0:
            prev = self.records[self.index - 1]
            prev_ts = _parse_event_ts(prev)
            curr_ts = _parse_event_ts(current)

            if prev_ts and curr_ts and curr_ts > prev_ts:
                sleep_sec = 1.0 / self.clock.speed
                time.sleep(min(sleep_sec, 0.25))

        self.index += 1
        return current