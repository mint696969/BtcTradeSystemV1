# path: ./btcts_next/src/btcts/collector_vnext/telemetry_policy.py
# desc: Collector vNext telemetry routing policy. Keeps high-frequency success events out of primary audit while preserving WARN/ERROR and safety/state transitions in audit.

from __future__ import annotations

from typing import Any, Dict, Optional

from btcts.core import audit, telemetry

COLLECTOR_TELEMETRY_STREAM = "collector_vnext"

HIGH_FREQUENCY_SUCCESS_EVENTS = frozenset(
    {
        "collector_vnext.unified.board_snapshot.completed",
        "collector_vnext.unified.rest_trades.completed",
        "collector_vnext.unified.ws_board.message.received",
        "collector_vnext.unified.ws_executions.message.received",
        "collector_vnext.unified.ws_executions.trade.written",
    }
)


def should_route_to_telemetry(event: str, *, level: str = "INFO") -> bool:
    return (str(level or "INFO").upper() == "INFO") and (str(event or "") in HIGH_FREQUENCY_SUCCESS_EVENTS)


def emit_collector_event(
    event: str,
    *,
    level: str = "INFO",
    feature: str = "collector_vnext",
    payload: Optional[Dict[str, Any]] = None,
    actor: str = "",
    site: str = "",
    trace_id: Optional[str] = None,
) -> None:
    if should_route_to_telemetry(event, level=level):
        merged_payload: Dict[str, Any] = dict(payload or {})
        merged_payload.setdefault("audit_routed", False)
        merged_payload.setdefault("telemetry_routed", True)
        merged_payload.setdefault("ps_q19b_audit_telemetry_split", True)
        telemetry.emit(
            event,
            level=level,
            feature=feature,
            stream=COLLECTOR_TELEMETRY_STREAM,
            actor=actor,
            site=site,
            trace_id=trace_id,
            payload=merged_payload,
        )
        return

    audit.emit(
        event,
        level=level,
        feature=feature,
        actor=actor,
        site=site,
        trace_id=trace_id,
        payload=payload,
    )
