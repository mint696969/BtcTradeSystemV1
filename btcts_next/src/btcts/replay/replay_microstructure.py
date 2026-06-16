# path: ./btcts_next/src/btcts/replay/replay_microstructure.py
# desc: Replay-side microstructure fusion using rebuilt orderbook signals and replay trade metrics.

from __future__ import annotations

from typing import Dict, List

from btcts.processing.l3_market_semantics.microstructure import (
    detect_absorption,
    detect_sweep,
)


def detect_microstructure(signal_payload: Dict, trade_metrics_payload: Dict) -> List[Dict]:
    events: List[Dict] = []

    absorption = detect_absorption(signal_payload, trade_metrics_payload)
    if absorption is not None:
        events.append(absorption)

    sweep = detect_sweep(signal_payload, trade_metrics_payload)
    if sweep is not None:
        events.append(sweep)

    return events