# path: ./btcts_next/src/btcts/apps/sr_fx_ws_canonical_refresh_once.py
# desc: Refresh SR-FX WS canonical board/executions, then attempt stale-safe L3 market_state bridge. No broker calls.

from __future__ import annotations

import json
from typing import Any, Callable, Iterable

from btcts.apps.operator_ui.components.live_bridge import latest_live_board_metrics, recent_live_tradeflow_metrics
from btcts.autotrade.read_model.fx_market_state_ws_live import write_fx_market_state_from_ws_live_canonical
from btcts.collector_vnext.fx_public_ws_refresh import (
    refresh_fx_ws_board_snapshot_until_seen,
    refresh_fx_ws_executions_until_seen,
)
from btcts.collector_vnext.ids import SequenceManager, make_session_id
from btcts.collector_vnext.config import load_config
from btcts.collector_vnext.providers.bitflyer_ws import WSMessage, connect_and_stream_executions
from btcts.collector_vnext.providers.bitflyer_ws_board import BoardMessage, connect_and_stream_board

STAGE = "sr_fx_ws_canonical_refresh_once"


def build_sr_fx_ws_canonical_refresh_payload(
    *,
    board_stream_factory: Callable[..., Iterable[BoardMessage]] = connect_and_stream_board,
    executions_stream_factory: Callable[..., Iterable[WSMessage]] = connect_and_stream_executions,
    max_board_messages: int = 20,
    max_execution_messages: int = 20,
) -> dict[str, Any]:
    cfg = load_config()
    seq = SequenceManager.start()
    session_id = make_session_id(cfg.collector_id)

    board = refresh_fx_ws_board_snapshot_until_seen(
        seq,
        session_id,
        max_messages=max_board_messages,
        stream_factory=board_stream_factory,
    )
    executions = refresh_fx_ws_executions_until_seen(
        seq,
        session_id,
        max_messages=max_execution_messages,
        stream_factory=executions_stream_factory,
    )
    l3 = write_fx_market_state_from_ws_live_canonical(
        latest_board_func=latest_live_board_metrics,
        recent_tradeflow_func=recent_live_tradeflow_metrics,
    )

    blocked_by: list[str] = []
    if not board.get("ok"):
        blocked_by.extend(str(item) for item in board.get("blocked_by", []))
    if not executions.get("ok"):
        blocked_by.extend(str(item) for item in executions.get("blocked_by", []))
    if not l3.ok:
        blocked_by.extend(str(item) for item in l3.blocked_by)

    blocked_by = list(dict.fromkeys(blocked_by))
    return {
        "stage": STAGE,
        "ok": not blocked_by,
        "session_id": session_id,
        "board_refresh": board,
        "executions_refresh": executions,
        "l3_market_state": l3.to_dict(),
        "blocked_by": blocked_by,
        "read_only": True,
        "would_send_to_broker": False,
    }


def main() -> int:
    try:
        payload = build_sr_fx_ws_canonical_refresh_payload()
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
