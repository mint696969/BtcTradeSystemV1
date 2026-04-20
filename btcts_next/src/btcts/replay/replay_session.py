# path: ./btcts_next/src/btcts/replay/replay_session.py
# desc: Replay session object that stores replay outputs and additive prediction evaluation artifacts.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ReplaySession:
    name: str
    source_paths: List[str]
    processed_count: int = 0
    output: List[Dict] = field(default_factory=list)
    prediction_evaluation_entries: List[Dict] = field(default_factory=list)
    prediction_calibration_reviews: List[Dict] = field(default_factory=list)
    tactic_proposal_outputs: List[Dict] = field(default_factory=list)
    tactic_review_records: List[Dict] = field(default_factory=list)
    tactic_operation_records: List[Dict] = field(default_factory=list)

    def add(self, item: Dict) -> None:
        self.output.append(item)
        self.processed_count += 1

    def add_prediction_evaluation_entry(self, item: Dict) -> None:
        self.prediction_evaluation_entries.append(item)

    def add_prediction_calibration_review(self, item: Dict) -> None:
        self.prediction_calibration_reviews.append(item)

    def add_tactic_proposal_output(self, item: Dict) -> None:
        self.tactic_proposal_outputs.append(item)

    def add_tactic_review_record(self, item: Dict) -> None:
        self.tactic_review_records.append(item)

    def add_tactic_operation_record(self, item: Dict) -> None:
        self.tactic_operation_records.append(item)

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
            "prediction_evaluation_entry_count": len(
                self.prediction_evaluation_entries
            ),
            "prediction_calibration_review_count": len(
                self.prediction_calibration_reviews
            ),
            "tactic_proposal_output_count": len(self.tactic_proposal_outputs),
            "tactic_review_record_count": len(self.tactic_review_records),
            "tactic_operation_record_count": len(self.tactic_operation_records),
        }