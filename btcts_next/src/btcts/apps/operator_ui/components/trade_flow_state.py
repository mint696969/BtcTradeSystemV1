# path: ./btcts_next/src/btcts/apps/operator_ui/components/trade_flow_state.py
# desc: Trade flow monitor panel 用の live-first / replay-fallback state adapter.

from __future__ import annotations

from btcts.apps.operator_ui.components.live_bridge import (
    recent_live_tradeflow_metrics,
)
from btcts.apps.operator_ui.components.research_bridge import (
    latest_trade_row,
    load_latest_replay_payload,
    tradeflow_metrics,
)


def build_trade_flow_state() -> dict | None:
    live_flow = recent_live_tradeflow_metrics(lines=80)
    if live_flow:
        return {
            "buy_volume": live_flow.get("buy_size"),
            "sell_volume": live_flow.get("sell_size"),
            "trade_delta": live_flow.get("delta"),
            "trade_count": live_flow.get("trade_count"),
            "event_ts": live_flow.get("event_ts"),
            "micro_event_names": [],
            "source_label": "live_canonical",
            "data_source": "live_canonical",
        }

    replay_payload = load_latest_replay_payload()
    flow = tradeflow_metrics(latest_trade_row(replay_payload))
    if not flow:
        return None

    return {
        **flow,
        "source_label": "replay_tradeflow",
        "data_source": "replay_tradeflow",
    }