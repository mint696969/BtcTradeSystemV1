# path: ./btcts_next/src/btcts/collector_vnext/unified_market_state_lane.py
# desc: Optional Unified daemon L3 market_state lane. Feeds canonical board events into MarketEngineRuntime.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._env_utils import env_bool
from .config import load_config
from .events import now_iso_utc
from .unified_state import write_unified_market_state_status
from btcts.market_engine.runtime import MarketEngineRuntime


@dataclass
class UnifiedMarketStateLaneState:
    enabled: bool = False
    lane_state: str = "disabled"
    step_count: int = 0
    last_event_ts: str | None = None
    last_output_path: str | None = None
    last_error: str | None = None
    last_market_uid: str | None = None
    last_symbol_raw: str | None = None
    last_best_bid: float | None = None
    last_best_ask: float | None = None
    last_spread: float | None = None
    last_source_series_id: str | None = None


class UnifiedMarketStateLane:
    """Optional L3 writer owned by the Unified daemon, not by Operator UI.

    The lane is disabled unless BTCTS_UNIFIED_MARKET_STATE_ENABLED is true.
    It consumes already-canonical board events from the unified WS board lane and
    delegates market meaning/state writing to MarketEngineRuntime.
    """

    def __init__(self, *, enabled: bool | None = None) -> None:
        self.cfg = load_config()
        self.enabled = env_bool("BTCTS_UNIFIED_MARKET_STATE_ENABLED", False) if enabled is None else bool(enabled)
        self.state = UnifiedMarketStateLaneState(
            enabled=self.enabled,
            lane_state="ready" if self.enabled else "disabled",
        )
        self._runtime: MarketEngineRuntime | None = MarketEngineRuntime() if self.enabled else None
        self._write_status()

    def snapshot(self) -> dict[str, Any]:
        return {
            "enabled": self.state.enabled,
            "lane_state": self.state.lane_state,
            "step_count": self.state.step_count,
            "last_event_ts": self.state.last_event_ts,
            "last_output_path": self.state.last_output_path,
            "last_error": self.state.last_error,
            "last_market_uid": self.state.last_market_uid,
            "last_symbol_raw": self.state.last_symbol_raw,
            "last_best_bid": self.state.last_best_bid,
            "last_best_ask": self.state.last_best_ask,
            "last_spread": self.state.last_spread,
            "last_source_series_id": self.state.last_source_series_id,
        }

    def _write_status(self) -> None:
        payload = {
            "ts": now_iso_utc(),
            "runtime_kind": "unified",
            "lane": "market_state_l3",
            "read_only": True,
            "would_send_to_broker": False,
            **self.snapshot(),
        }
        write_unified_market_state_status(self.cfg, payload)

    def step(self, canonical_record: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled or self._runtime is None:
            return self.snapshot()
        try:
            result = self._runtime.step(canonical_record)
            row = result.market_state.to_dict()
            self.state.lane_state = "live"
            self.state.step_count += 1
            self.state.last_event_ts = row.get("collector_ts") or row.get("exchange_ts")
            self.state.last_output_path = result.output_path
            self.state.last_error = None
            self.state.last_market_uid = row.get("market_uid")
            self.state.last_symbol_raw = row.get("symbol_raw")
            self.state.last_best_bid = row.get("best_bid")
            self.state.last_best_ask = row.get("best_ask")
            self.state.last_spread = row.get("spread")
            self.state.last_source_series_id = row.get("source_series_id")
        except Exception as exc:
            self.state.lane_state = "degraded"
            self.state.last_error = str(exc)
        self._write_status()
        return self.snapshot()
