# path: ./btcts_next/src/btcts/apps/sr_fx_ws_live_market_state_once.py
# desc: Write one SR-FX L3 market_state row from existing FX live canonical WS board/tradeflow. No broker calls.

from __future__ import annotations

import json
from typing import Any

from btcts.apps.operator_ui.components.live_bridge import latest_live_board_metrics, recent_live_tradeflow_metrics
from btcts.autotrade.read_model.fx_market_state_ws_live import (
    FxWsLiveMarketStateResult,
    write_fx_market_state_from_ws_live_canonical,
)

STAGE = "sr_fx_ws_live_market_state_once"


def build_sr_fx_ws_live_market_state_payload() -> dict[str, Any]:
    result = write_fx_market_state_from_ws_live_canonical(
        latest_board_func=latest_live_board_metrics,
        recent_tradeflow_func=recent_live_tradeflow_metrics,
    )
    return {
        "stage": STAGE,
        "ok": result.ok,
        "result": result.to_dict(),
        "read_only": True,
        "would_send_to_broker": False,
    }


def main() -> int:
    try:
        payload = build_sr_fx_ws_live_market_state_payload()
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))
        return 0
    except Exception as exc:
        payload = {
            "stage": STAGE,
            "ok": False,
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "read_only": True,
            "would_send_to_broker": False,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
