# path: ./btcts_next/src/btcts/collector_vnext/transforms/board_structural_hints.py
# desc: Board canonical payload に L2 structural metadata hints を付与する Collector runtime adapter helper。

from __future__ import annotations

from typing import Any, Dict, Optional


def _instrument_id(exchange: str, symbol: str) -> str:
    return f"{exchange}.spot.{symbol}"


def apply_board_structural_hints(
    payload: Dict[str, Any],
    *,
    exchange: str,
    symbol: str,
    channel: str,
    provider: str,
    transport: str,
    transport_role: str,
    origin_role: str,
    collector_id: str,
    stream_session_id: str,
    current_event_id: Optional[str],
    base_snapshot_id: Optional[str],
    continuity_state: str,
    is_resync: bool,
    description: str,
) -> Dict[str, Any]:
    """Attach structural integration/dedupe/completeness/origin hints.

    This helper belongs to the collector runtime adapter layer.
    It must not decide market meaning. L3 remains the semantic owner.
    """

    instrument_id = _instrument_id(exchange, symbol)
    series_prefix = "rest" if transport == "rest" else "ws"
    safe_base_snapshot_id = base_snapshot_id if base_snapshot_id is not None else "unknown_base"

    payload["integration_hint"] = {
        "integration_domain": "board_continuity_series",
        "transport_role": transport_role,
        "series_key_hint": f"{series_prefix}:{stream_session_id}:{safe_base_snapshot_id}",
        "unified_view_policy": "series_based_not_event_dedupe",
    }

    continuity_policy = {
        "mode": "conservative",
        "mix_unknown": False,
        "split_on_gap": True,
        "split_on_resync": True,
    }
    if transport_role != "baseline_snapshot":
        continuity_policy["continuous_only_when"] = continuity_state == "continuous"

    payload["dedupe_hint"] = {
        "entity_kind": "board",
        "event_dedupe_key": {
            "exchange": exchange,
            "instrument_id": instrument_id,
            "channel": channel,
            "source_event_id": current_event_id,
        },
        "series_key": {
            "exchange": exchange,
            "instrument_id": instrument_id,
            "channel": channel,
            "base_snapshot_id": base_snapshot_id,
            "stream_session_id": stream_session_id,
        },
        "continuity_policy": continuity_policy,
    }

    if transport_role == "baseline_snapshot":
        completeness = "partial"
        confidence_hint = "medium_or_low"
        completeness_basis = {
            "base_snapshot_id_present": base_snapshot_id is not None,
            "stream_session_id_present": bool(stream_session_id),
            "continuity_state": continuity_state,
            "gap_or_resync_observed": bool(is_resync or continuity_state in {"gap_detected", "resynced"}),
            "transport_role": transport_role,
        }
        policy_note = "rest snapshot is useful as baseline but not a continuous board series by itself"
    else:
        completeness = (
            "complete"
            if continuity_state == "continuous" and base_snapshot_id is not None and not is_resync
            else "mostly_complete"
            if continuity_state == "resynced" and base_snapshot_id is not None
            else "gap_detected"
            if continuity_state == "gap_detected"
            else "unknown"
        )
        confidence_hint = (
            "high"
            if continuity_state == "continuous" and base_snapshot_id is not None and not is_resync
            else "medium_high"
            if continuity_state == "resynced" and base_snapshot_id is not None
            else "low"
        )
        completeness_basis = {
            "base_snapshot_id_present": base_snapshot_id is not None,
            "stream_session_id_present": bool(stream_session_id),
            "source_event_id_present": current_event_id is not None,
            "continuity_state": continuity_state,
            "is_resync": bool(is_resync),
            "transport_role": transport_role,
        }
        policy_note = "board completeness is evaluated conservatively by continuity series, not by single event"

    payload["completeness_hint"] = {
        "evaluation_unit": "board_series",
        "completeness": completeness,
        "confidence_hint": confidence_hint,
        "completeness_basis": completeness_basis,
        "policy_note": policy_note,
    }

    payload["origin_hint"] = {
        "source_layer": "collector",
        "provider": provider,
        "transport": transport,
        "endpoint_or_channel": channel,
        "origin_role": origin_role,
        "collector_id": collector_id,
        "stream_session_id": stream_session_id,
        "description": description,
    }

    return payload