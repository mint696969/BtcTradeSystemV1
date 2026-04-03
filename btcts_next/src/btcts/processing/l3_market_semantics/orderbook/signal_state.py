# path: ./btcts_next/src/btcts/processing/l3_market_semantics/orderbook/signal_state.py
# desc: Previous-signal state container for liquidity event detection.

from __future__ import annotations

from typing import Dict, Optional


class SignalState:
    def __init__(self):
        self.last_signal: Optional[Dict] = None

    def update(self, signal_payload: Dict) -> None:
        self.last_signal = signal_payload

    def get(self) -> Optional[Dict]:
        return self.last_signal