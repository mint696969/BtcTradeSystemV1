# path: ./btcts_next/src/btcts/collector_vnext/transforms/facade.py
# desc: Stable collector runtime adapter import surface for Phase F transform migration.

from __future__ import annotations

from typing import Any, Dict, List, Optional

from btcts.collector_vnext.transforms.board_structural_hints import (
    apply_board_structural_hints as _apply_board_structural_hints,
)
from btcts.collector_vnext.transforms.raw_to_canonical import (
    canonical_board_snapshot as _canonical_board_snapshot,
)
from btcts.collector_vnext.transforms.raw_to_canonical_trades import (
    canonical_trades as _canonical_trades,
)
from btcts.collector_vnext.transforms.trade_structural_hints import (
    apply_trade_structural_hints as _apply_trade_structural_hints,
)
from btcts.collector_vnext.transforms.ws_board_to_canonical import (
    BoardLevelsAdapter,
    canonical_board_event as _canonical_board_event,
)
from btcts.collector_vnext.transforms.ws_trade_to_canonical import (
    canonical_ws_trade as _canonical_ws_trade,
)

COLLECTOR_TRANSFORM_FACADE_VERSION = "collector_transform_facade.v1"


def canonical_board_snapshot(
    source_payload: Dict[str, Any],
    *,
    depth: int = 50,
    snapshot_id: str | None = None,
) -> Dict[str, Any]:
    return _canonical_board_snapshot(
        source_payload,
        depth=depth,
        snapshot_id=snapshot_id,
    )


def canonical_board_event(
    payload: Dict[str, Any],
    *,
    snapshot: bool,
    adapter: BoardLevelsAdapter,
) -> Dict[str, Any]:
    return _canonical_board_event(
        payload,
        snapshot=snapshot,
        adapter=adapter,
    )


def canonical_trades(source_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    return _canonical_trades(source_payload)


def canonical_ws_trade(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    return _canonical_ws_trade(msg)


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
    return _apply_board_structural_hints(
        payload,
        exchange=exchange,
        symbol=symbol,
        channel=channel,
        provider=provider,
        transport=transport,
        transport_role=transport_role,
        origin_role=origin_role,
        collector_id=collector_id,
        stream_session_id=stream_session_id,
        current_event_id=current_event_id,
        base_snapshot_id=base_snapshot_id,
        continuity_state=continuity_state,
        is_resync=is_resync,
        description=description,
    )


def apply_trade_structural_hints(
    trade: Dict[str, Any],
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
    seen_in_rest: bool,
    seen_in_ws: bool,
    description: str,
) -> Dict[str, Any]:
    return _apply_trade_structural_hints(
        trade,
        exchange=exchange,
        symbol=symbol,
        channel=channel,
        provider=provider,
        transport=transport,
        transport_role=transport_role,
        origin_role=origin_role,
        collector_id=collector_id,
        stream_session_id=stream_session_id,
        seen_in_rest=seen_in_rest,
        seen_in_ws=seen_in_ws,
        description=description,
    )


__all__ = [
    "COLLECTOR_TRANSFORM_FACADE_VERSION",
    "BoardLevelsAdapter",
    "canonical_board_snapshot",
    "canonical_board_event",
    "canonical_trades",
    "canonical_ws_trade",
    "apply_board_structural_hints",
    "apply_trade_structural_hints",
]
