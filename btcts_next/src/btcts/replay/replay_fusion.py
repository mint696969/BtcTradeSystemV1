# path: ./btcts_next/src/btcts/replay/replay_fusion.py
# desc: Replay fusion pipeline joining board-derived signals with replay tradeflow for microstructure detection.

from __future__ import annotations

from typing import Dict, List, Optional

from btcts.ingestion.event_types import EventType
from btcts.market_engine.profiles import create_exchange_profile
from .replay_microstructure import detect_microstructure
from .replay_pipeline import ReplayPipeline
from .replay_tradeflow import ReplayTradeFlow


class ReplayFusion:
    def __init__(self, *, profile_name: str = "bitflyer"):
        self.board_pipeline = ReplayPipeline(
            exchange_profile=create_exchange_profile(profile_name),
        )
        self.tradeflow = ReplayTradeFlow()
        self.last_board_result: Optional[Dict] = None

    def process_record(self, record: Dict) -> Optional[Dict]:
        record_type = str(record.get("record_type") or "")

        if record_type in {
            EventType.MARKET_ORDERBOOK_SNAPSHOT,
            EventType.MARKET_ORDERBOOK_DIFF,
        }:
            board_result = self.board_pipeline.process_record(record)
            if board_result is not None:
                self.last_board_result = board_result
            return {
                "kind": "board",
                "record_type": record_type,
                "event_ts": record.get("event_ts"),
                "result": board_result,
            }

        if record_type == EventType.MARKET_TRADE:
            self.tradeflow.add_record(record)

            if self.last_board_result is None:
                return {
                    "kind": "trade",
                    "record_type": record_type,
                    "event_ts": record.get("event_ts"),
                    "tradeflow": None,
                    "microstructure": [],
                }

            tradeflow_payload = self.tradeflow.flush()
            if tradeflow_payload is None:
                return {
                    "kind": "trade",
                    "record_type": record_type,
                    "event_ts": record.get("event_ts"),
                    "tradeflow": None,
                    "microstructure": [],
                }

            signal_payload = self.last_board_result.get("signal")
            micro_events: List[Dict] = []

            if isinstance(signal_payload, dict):
                micro_events = detect_microstructure(signal_payload, tradeflow_payload)

            return {
                "kind": "trade",
                "record_type": record_type,
                "event_ts": record.get("event_ts"),
                "tradeflow": tradeflow_payload,
                "microstructure": micro_events,
            }

        return None

    def process_records(self, records: List[Dict]) -> List[Dict]:
        out: List[Dict] = []

        for record in records:
            result = self.process_record(record)
            if result is not None:
                out.append(result)

        return out