# path: ./btcts_next/src/btcts/replay/replay_session.py
# desc: Replay session object that stores replay outputs and summary stats.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ReplaySession:
    name: str
    source_paths: List[str]
    processed_count: int = 0
    output: List[Dict] = field(default_factory=list)

    def add(self, item: Dict) -> None:
        self.output.append(item)
        self.processed_count += 1

    def summary(self) -> Dict:
        event_count = 0
        signal_count = 0

        for row in self.output:
            signal = row.get("signal")
            events = row.get("events", [])

            if signal is not None:
                signal_count += 1
            if isinstance(events, list):
                event_count += len(events)

        return {
            "name": self.name,
            "source_paths": self.source_paths,
            "processed_count": self.processed_count,
            "signal_count": signal_count,
            "event_count": event_count,
        }