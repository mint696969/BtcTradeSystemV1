# path: ./tools/test_collector_vnext_canonical_rebuild_audit.py
# desc: Audit canonical board/control data and verify rebuild + continuity integrity from stored records.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from btcts.ingestion.l2_canonical.orderbook.book_rebuilder import OrderBookRebuilder


# =========================
# 設定
# =========================
CANONICAL_ROOT = Path("var/collector_vnext/data/market_data")
MAX_GROUPS = 5

INCLUDE_SYSTEM_GROUPS = False
SHOW_ALL_SESSIONS = False
PREFER_BOARD_WS = True
MAX_SESSIONS_PER_GROUP = 20

CONTROL_RECORD_TYPES = {
    "stream.gap_detected",
    "stream.resync_started",
    "stream.resync_completed",
    "system.provider_error",
    "stream.started",
}

BOARD_RECORD_TYPES = {
    "market.orderbook.snapshot",
    "market.orderbook.diff",
}


# =========================
# ユーティリティ
# =========================
def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows


def _record_type(record: Dict[str, Any]) -> str:
    return str(record.get("record_type") or "")


def _payload(record: Dict[str, Any]) -> Dict[str, Any]:
    p = record.get("payload")
    return p if isinstance(p, dict) else {}


def _extract_board_event(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    payload = _payload(record)
    record_type = _record_type(record)

    if record_type == "market.orderbook.snapshot":
        return {
            "event_type": "snapshot",
            "bids": payload.get("bids") or [],
            "asks": payload.get("asks") or [],
        }

    if record_type == "market.orderbook.diff":
        return {
            "event_type": "delta",
            "bids": payload.get("bids") or [],
            "asks": payload.get("asks") or [],
        }

    return None


def _best(book: OrderBookRebuilder) -> Tuple[Optional[float], Optional[float]]:
    return book.best_bid(), book.best_ask()


def _record_sort_key(record: Dict[str, Any]) -> Tuple[int, str, str]:
    sequence_id = int(record.get("sequence_id") or 0)
    event_ts = str(record.get("event_ts") or "")
    record_id = str(record.get("record_id") or "")
    return (sequence_id, event_ts, record_id)


def _stream_session_id(record: Dict[str, Any]) -> str:
    return str(record.get("stream_session_id") or "unknown")


def _group_key_from_path(path: Path) -> Tuple[str, str, str]:
    parts = path.parts

    exchange = "unknown"
    symbol = "unknown"
    date = "unknown"

    for part in parts:
        if part.startswith("exchange="):
            exchange = part.split("=", 1)[1]
        elif part.startswith("symbol="):
            symbol = part.split("=", 1)[1]
        elif part.startswith("date="):
            date = part.split("=", 1)[1]

    return exchange, symbol, date


def _discover_groups() -> Dict[Tuple[str, str, str], List[Path]]:
    grouped: Dict[Tuple[str, str, str], List[Path]] = defaultdict(list)

    for path in CANONICAL_ROOT.rglob("*.jsonl"):
        text = str(path).replace("\\", "/")

        if any(f"/type={record_type}/" in text for record_type in BOARD_RECORD_TYPES | CONTROL_RECORD_TYPES):
            grouped[_group_key_from_path(path)].append(path)

    return grouped


def _continuity_fields(record: Dict[str, Any]) -> Dict[str, Any]:
    payload = _payload(record)
    return {
        "continuity_state": payload.get("continuity_state"),
        "rebuild_required": payload.get("rebuild_required"),
        "is_gap_fill": payload.get("is_gap_fill"),
        "is_resync": payload.get("is_resync"),
        "snapshot_id": payload.get("snapshot_id"),
        "base_snapshot_id": payload.get("base_snapshot_id"),
        "prev_event_id": payload.get("prev_event_id"),
        "stream_event_no": payload.get("stream_event_no"),
    }


# =========================
# セッション監査
# =========================
def _audit_session(stream_session_id: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
    records.sort(key=_record_sort_key)

    rebuilder = OrderBookRebuilder()

    snapshot_count = 0
    diff_count = 0
    started_count = 0
    gap_count = 0
    resync_started_count = 0
    resync_completed_count = 0
    provider_error_count = 0

    deltas_before_first_snapshot = 0
    no_change_after_delta_count = 0

    pending_gap = False
    first_board_event_type: Optional[str] = None

    first_snapshot_continuity_state: Optional[str] = None
    first_snapshot_is_resync: Optional[bool] = None
    first_snapshot_prev_event_id: Optional[str] = None

    continuity_issues: List[Dict[str, Any]] = []

    previous_stream_event_no: Optional[int] = None
    previous_board_record_id: Optional[str] = None
    previous_board_event_type: Optional[str] = None

    for index, record in enumerate(records):
        record_type = _record_type(record)
        payload = _payload(record)

        if record_type == "stream.started":
            started_count += 1
            continue

        if record_type == "stream.gap_detected":
            gap_count += 1
            pending_gap = True
            continue

        if record_type == "stream.resync_started":
            resync_started_count += 1
            continue

        if record_type == "stream.resync_completed":
            resync_completed_count += 1
            pending_gap = False
            continue

        if record_type == "system.provider_error":
            provider_error_count += 1
            pending_gap = True
            continue

        board_event = _extract_board_event(record)
        if board_event is None:
            continue

        if first_board_event_type is None:
            first_board_event_type = board_event["event_type"]

        continuity = _continuity_fields(record)

        if board_event["event_type"] == "snapshot":
            snapshot_count += 1

            if first_snapshot_continuity_state is None:
                first_snapshot_continuity_state = continuity["continuity_state"]
                first_snapshot_is_resync = bool(continuity["is_resync"])
                first_snapshot_prev_event_id = continuity["prev_event_id"]

            if pending_gap and not bool(continuity["is_resync"]):
                continuity_issues.append(
                    {
                        "index": index,
                        "type": "snapshot_after_gap_without_is_resync",
                        "record_id": record.get("record_id"),
                        "event_ts": record.get("event_ts"),
                    }
                )

        elif board_event["event_type"] == "delta":
            diff_count += 1
            if not rebuilder.snapshot_loaded:
                deltas_before_first_snapshot += 1

            if previous_board_event_type is None and gap_count == 0 and resync_started_count == 0:
                continuity_issues.append(
                    {
                        "index": index,
                        "type": "delta_before_snapshot_without_gap_control",
                        "record_id": record.get("record_id"),
                        "event_ts": record.get("event_ts"),
                    }
                )

        before = _best(rebuilder)
        had_snapshot_before = rebuilder.snapshot_loaded
        rebuilder.apply_event(board_event)
        after = _best(rebuilder)

        if board_event["event_type"] == "delta" and had_snapshot_before and before == after:
            no_change_after_delta_count += 1

        stream_event_no_raw = continuity.get("stream_event_no")
        if stream_event_no_raw is not None:
            try:
                stream_event_no = int(stream_event_no_raw)
            except Exception:
                stream_event_no = None
        else:
            stream_event_no = None

        if previous_stream_event_no is not None and stream_event_no is not None:
            if stream_event_no <= previous_stream_event_no:
                continuity_issues.append(
                    {
                        "index": index,
                        "type": "stream_event_no_not_increasing",
                        "previous_stream_event_no": previous_stream_event_no,
                        "current_stream_event_no": stream_event_no,
                        "record_id": record.get("record_id"),
                    }
                )

        prev_event_id = continuity.get("prev_event_id")
        current_record_id = record.get("record_id")

        if previous_board_record_id is None:
            if prev_event_id not in (None, ""):
                continuity_issues.append(
                    {
                        "index": index,
                        "type": "first_board_event_has_prev_event_id",
                        "prev_event_id": prev_event_id,
                        "record_id": current_record_id,
                    }
                )
        else:
            if prev_event_id in (None, ""):
                continuity_issues.append(
                    {
                        "index": index,
                        "type": "missing_prev_event_id",
                        "record_id": current_record_id,
                    }
                )

        previous_stream_event_no = stream_event_no if stream_event_no is not None else previous_stream_event_no
        previous_board_record_id = str(current_record_id) if current_record_id is not None else previous_board_record_id
        previous_board_event_type = board_event["event_type"]

    final_best = _best(rebuilder)

    expected_gap_before_snapshot = first_board_event_type == "delta"
    gap_control_consistent = (not expected_gap_before_snapshot) or (gap_count >= 1 and resync_started_count >= 1)

    resync_completion_consistent = True
    if expected_gap_before_snapshot and snapshot_count >= 1:
        resync_completion_consistent = resync_completed_count >= 1 or bool(first_snapshot_is_resync)

    return {
        "stream_session_id": stream_session_id,
        "record_count": len(records),
        "snapshot_count": snapshot_count,
        "diff_count": diff_count,
        "started_count": started_count,
        "gap_count": gap_count,
        "resync_started_count": resync_started_count,
        "resync_completed_count": resync_completed_count,
        "provider_error_count": provider_error_count,
        "first_board_event_type": first_board_event_type,
        "deltas_before_first_snapshot": deltas_before_first_snapshot,
        "gap_control_consistent": gap_control_consistent,
        "resync_completion_consistent": resync_completion_consistent,
        "first_snapshot_continuity_state": first_snapshot_continuity_state,
        "first_snapshot_is_resync": first_snapshot_is_resync,
        "first_snapshot_prev_event_id": first_snapshot_prev_event_id,
        "no_change_after_delta_count": no_change_after_delta_count,
        "final_best": final_best,
        "continuity_issue_count": len(continuity_issues),
        "continuity_issues_sample": continuity_issues[:10],
    }


# =========================
# グループ監査
# =========================
def audit_group(exchange: str, symbol: str, date: str, paths: List[Path]) -> Dict[str, Any]:
    all_records: List[Dict[str, Any]] = []

    for path in paths:
        all_records.extend(_load_jsonl(path))

    sessions: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for record in all_records:
        sessions[_stream_session_id(record)].append(record)

    session_results: List[Dict[str, Any]] = []
    for stream_session_id, records in sorted(sessions.items(), key=lambda x: x[0]):
        session_results.append(_audit_session(stream_session_id, records))

    return {
        "exchange": exchange,
        "symbol": symbol,
        "date": date,
        "session_count": len(session_results),
        "sessions": session_results,
    }


def _session_sort_key(session: Dict[str, Any]) -> Tuple[int, str]:
    stream_session_id = str(session.get("stream_session_id") or "")
    is_board_ws = "-board_ws-" in stream_session_id
    has_issues = int(session.get("continuity_issue_count") or 0) > 0
    is_delta_first = session.get("first_board_event_type") == "delta"

    if PREFER_BOARD_WS:
        priority = (
            0 if (is_board_ws and has_issues) else
            1 if (is_board_ws and is_delta_first) else
            2 if is_board_ws else
            3
        )
    else:
        priority = 0

    return (priority, stream_session_id)


def _build_group_summary(group_result: Dict[str, Any]) -> Dict[str, Any]:
    sessions = group_result.get("sessions") or []

    board_ws_sessions = [
        s for s in sessions
        if "-board_ws-" in str(s.get("stream_session_id") or "")
    ]

    delta_first_sessions = [
        s for s in board_ws_sessions
        if s.get("first_board_event_type") == "delta"
    ]

    gap_consistent_sessions = [
        s for s in board_ws_sessions
        if bool(s.get("gap_control_consistent", False))
    ]

    resync_consistent_sessions = [
        s for s in board_ws_sessions
        if bool(s.get("resync_completion_consistent", False))
    ]

    issue_sessions = [
        s for s in board_ws_sessions
        if int(s.get("continuity_issue_count") or 0) > 0
    ]

    return {
        "board_ws_session_count": len(board_ws_sessions),
        "board_ws_delta_first_count": len(delta_first_sessions),
        "board_ws_gap_consistent_count": len(gap_consistent_sessions),
        "board_ws_resync_consistent_count": len(resync_consistent_sessions),
        "board_ws_issue_session_count": len(issue_sessions),
    }


def _normalize_group_paths(paths: Any) -> Dict[str, Optional[Path]]:
    if isinstance(paths, dict):
        return {
            "snapshot": paths.get("snapshot"),
            "diff": paths.get("diff"),
        }

    snapshot_path: Optional[Path] = None
    diff_path: Optional[Path] = None

    if isinstance(paths, list):
        for item in paths:
            text = str(item).replace("\\", "/")
            if "/type=market.orderbook.snapshot/" in text:
                snapshot_path = item
            elif "/type=market.orderbook.diff/" in text:
                diff_path = item

    return {
        "snapshot": snapshot_path,
        "diff": diff_path,
    }


def run_audit() -> Dict[str, Any]:
    grouped = _discover_groups()

    all_keys = sorted(grouped.keys())

    if not INCLUDE_SYSTEM_GROUPS:
        all_keys = [k for k in all_keys if k[0] != "system"]

    keys = all_keys[:MAX_GROUPS]

    results: List[Dict[str, Any]] = []
    for exchange, symbol, date in keys:
        raw_paths = grouped[(exchange, symbol, date)]

        group_result = audit_group(
            exchange=exchange,
            symbol=symbol,
            date=date,
            paths=raw_paths,
        )

        all_sessions = list(group_result.get("sessions") or [])
        all_sessions.sort(key=_session_sort_key)

        summary_source = {
            **group_result,
            "sessions": all_sessions,
        }
        group_result["summary"] = _build_group_summary(summary_source)

        if SHOW_ALL_SESSIONS:
            group_result["sessions"] = all_sessions
        else:
            group_result["sessions"] = all_sessions[:MAX_SESSIONS_PER_GROUP]

        results.append(group_result)

    return {
        "group_count": len(results),
        "results": results,
    }


def main() -> None:
    result = run_audit()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
