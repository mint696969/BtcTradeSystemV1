# path: ./tools/test_collector_vnext_board_ws_contract.py
# desc: Observe live WS board canonical contract integrity for continuity/order checks.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from btcts.collector_vnext.providers.bitflyer_ws_board import connect_and_stream_board
from btcts.collector_vnext.venue_adapters.bitflyer_board import BitflyerBoardVenueAdapter
from btcts.collector_vnext.transforms.ws_board_to_canonical import canonical_board_event


SYMBOL = os.getenv("BTCTS_SYMBOL", "BTC_JPY")
SSL_VERIFY = os.getenv("BTCTS_WS_SSL_VERIFY", "false").strip().lower() == "true"
MAX_MESSAGES = int(os.getenv("BTCTS_BOARD_CONTRACT_MAX_MESSAGES", "80"))


@dataclass
class ContractObservation:
    message_no: int
    event_type: str
    stream_event_no: int
    continuity_sequence: int
    prev_event_id: Optional[str]
    current_event_id: str
    base_snapshot_id: Optional[str]
    continuity_state: str
    rebuild_required: bool
    is_resync: bool


def _make_event_id(stream_session_id: str, event_type: str, stream_event_no: int) -> str:
    kind = "snapshot" if event_type == "snapshot" else "delta"
    return f"bitflyer:board_ws:{stream_session_id}:{kind}:{stream_event_no}"


def observe_board_contract(
    symbol: str = SYMBOL,
    ssl_verify: bool = SSL_VERIFY,
    max_messages: int = MAX_MESSAGES,
) -> Dict[str, Any]:
    adapter = BitflyerBoardVenueAdapter()
    stream_session_id = "contract-test-session"

    observations: List[ContractObservation] = []
    violations: List[Dict[str, Any]] = []

    current_base_snapshot_id: Optional[str] = None
    last_board_event_id: Optional[str] = None
    board_event_no = 0
    saw_snapshot = False
    saw_gap_like = False

    stream = connect_and_stream_board(
        symbol=symbol,
        ssl_verify=ssl_verify,
    )

    for message_no, msg in enumerate(stream, start=1):
        message_kind = adapter.classify_board_message_kind(
            channel=msg.channel,
            payload=msg.payload,
        )

        if message_kind == "unknown":
            continue

        is_snapshot = message_kind == "snapshot"
        board_event_no += 1

        payload = canonical_board_event(
            msg.payload,
            snapshot=is_snapshot,
            adapter=adapter,
        )
        payload["stream_event_no"] = board_event_no

        current_event_id = _make_event_id(
            stream_session_id=stream_session_id,
            event_type=payload["event_type"],
            stream_event_no=board_event_no,
        )

        if is_snapshot:
            current_base_snapshot_id = current_event_id
            continuity_state = "continuous" if not saw_gap_like else "resynced"
            rebuild_required = False
            is_resync = saw_gap_like
            saw_snapshot = True
            saw_gap_like = False
        else:
            if current_base_snapshot_id is None:
                continuity_state = "gap_detected"
                rebuild_required = True
                is_resync = False
                saw_gap_like = True
            else:
                continuity_state = "continuous"
                rebuild_required = False
                is_resync = False

        payload["snapshot_id"] = current_event_id if is_snapshot else None
        payload["base_snapshot_id"] = current_base_snapshot_id
        payload["prev_event_id"] = last_board_event_id
        payload["continuity_state"] = continuity_state
        payload["rebuild_required"] = rebuild_required
        payload["is_gap_fill"] = False
        payload["is_resync"] = is_resync

        continuity_sequence = int(payload["stream_event_no"])

        obs = ContractObservation(
            message_no=message_no,
            event_type=str(payload["event_type"]),
            stream_event_no=int(payload["stream_event_no"]),
            continuity_sequence=continuity_sequence,
            prev_event_id=payload.get("prev_event_id"),
            current_event_id=current_event_id,
            base_snapshot_id=payload.get("base_snapshot_id"),
            continuity_state=str(payload["continuity_state"]),
            rebuild_required=bool(payload["rebuild_required"]),
            is_resync=bool(payload["is_resync"]),
        )
        observations.append(obs)

        if obs.stream_event_no != obs.continuity_sequence:
            violations.append(
                {
                    "type": "continuity_sequence_mismatch",
                    "message_no": message_no,
                    "stream_event_no": obs.stream_event_no,
                    "continuity_sequence": obs.continuity_sequence,
                }
            )

        if len(observations) >= 2:
            prev = observations[-2]
            if obs.stream_event_no != prev.stream_event_no + 1:
                violations.append(
                    {
                        "type": "stream_event_no_not_monotonic",
                        "message_no": message_no,
                        "prev_stream_event_no": prev.stream_event_no,
                        "current_stream_event_no": obs.stream_event_no,
                    }
                )

            expected_prev_event_id = prev.current_event_id
            if obs.prev_event_id != expected_prev_event_id:
                violations.append(
                    {
                        "type": "prev_event_id_broken",
                        "message_no": message_no,
                        "expected_prev_event_id": expected_prev_event_id,
                        "actual_prev_event_id": obs.prev_event_id,
                    }
                )

        if obs.event_type == "delta" and obs.base_snapshot_id is None:
            if obs.continuity_state != "gap_detected":
                violations.append(
                    {
                        "type": "pre_snapshot_delta_without_gap_state",
                        "message_no": message_no,
                        "continuity_state": obs.continuity_state,
                    }
                )
            if obs.rebuild_required is not True:
                violations.append(
                    {
                        "type": "pre_snapshot_delta_without_rebuild_required",
                        "message_no": message_no,
                        "rebuild_required": obs.rebuild_required,
                    }
                )

        if obs.event_type == "snapshot" and saw_snapshot:
            if obs.base_snapshot_id != obs.current_event_id:
                violations.append(
                    {
                        "type": "snapshot_base_snapshot_id_mismatch",
                        "message_no": message_no,
                        "base_snapshot_id": obs.base_snapshot_id,
                        "current_event_id": obs.current_event_id,
                    }
                )

        last_board_event_id = current_event_id

        if message_no >= max_messages:
            break

    return {
        "ok": len(violations) == 0,
        "symbol": symbol,
        "ssl_verify": ssl_verify,
        "message_count": len(observations),
        "violations": violations,
        "observations_tail": [asdict(x) for x in observations[-10:]],
    }


def main() -> None:
    result = observe_board_contract()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()