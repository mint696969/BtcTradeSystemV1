# path: ./tools/test_collector_vnext_invariants.py
# desc: P0 invariant smoke test for Collector vNext canonical/state contracts.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, Iterable, List

from btcts.collector_vnext.config import load_config
from btcts.collector_vnext.ids import SequenceManager, make_session_id
from btcts.collector_vnext.emit_rest import emit_rest_board_snapshot, emit_rest_trades
from btcts.collector_vnext.emit_ws import emit_ws_trade_smoke, emit_ws_board_smoke


def _setup_env() -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    tmp_root = repo_root / "tmp" / "_vnext_invariant_test"

    if tmp_root.exists():
        shutil.rmtree(tmp_root)

    data_root = tmp_root / "data"
    logs_root = tmp_root / "logs"
    state_root = tmp_root / "state"

    os.environ["BTCTS_DATA_ROOT"] = str(data_root)
    os.environ["BTCTS_LOGS_ROOT"] = str(logs_root)
    os.environ["BTCTS_STATE_ROOT"] = str(state_root)
    os.environ["BTC_TS_DATA_DIR"] = str(data_root)
    os.environ["BTC_TS_LOGS_DIR"] = str(logs_root)
    os.environ["BTCTS_WS_SSL_VERIFY"] = "0"

    data_root.mkdir(parents=True, exist_ok=True)
    logs_root.mkdir(parents=True, exist_ok=True)
    state_root.mkdir(parents=True, exist_ok=True)

    return tmp_root


def _iter_jsonl(root: Path) -> Iterable[Dict[str, Any]]:
    if not root.exists():
        return []
    for path in root.rglob("*.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def _find_first(records: Iterable[Dict[str, Any]], record_type: str) -> Dict[str, Any] | None:
    for rec in records:
        if rec.get("record_type") == record_type:
            return rec
    return None


def _assert(cond: bool, message: str, failures: List[str]) -> None:
    if not cond:
        failures.append(message)


def _check_common_canonical(record: Dict[str, Any], failures: List[str]) -> None:
    required = [
        "schema_version",
        "schema_contract",
        "schema_contract_version",
        "payload_contract_version",
        "record_type",
        "record_id",
        "collector_id",
        "collector_role",
        "host_name",
        "session_id",
        "stream_session_id",
        "exchange",
        "market",
        "symbol",
        "instrument_id",
        "channel",
        "transport",
        "source_event_id",
        "source_sequence",
        "sequence_id",
        "exchange_ts",
        "collector_ts",
        "ingest_ts",
        "event_ts",
        "quality_flags",
        "is_partial",
        "is_reconstructed",
        "confidence_score",
        "payload",
    ]
    for key in required:
        _assert(key in record, f"canonical missing common field: {key}", failures)

    _assert(
        record.get("schema_version") == "collector.vnext.canonical",
        "canonical schema_version must be collector.vnext.canonical",
        failures,
    )
    _assert(
        record.get("schema_contract") == "collector.vnext.canonical.required.v1",
        "canonical schema_contract must be collector.vnext.canonical.required.v1",
        failures,
    )
    _assert(record.get("schema_contract_version") == 1, "schema_contract_version must be 1", failures)
    _assert(record.get("payload_contract_version") == 1, "payload_contract_version must be 1", failures)

    payload = record.get("payload")
    _assert(isinstance(payload, dict), "payload must be dict", failures)
    if not isinstance(payload, dict):
        return

    for key in ["integration_hint", "dedupe_hint", "completeness_hint", "origin_hint"]:
        _assert(key in payload, f"payload missing {key}", failures)


def _check_trade(record: Dict[str, Any], failures: List[str]) -> None:
    _check_common_canonical(record, failures)
    payload = record.get("payload", {})

    for key in ["trade_id", "side", "price", "size", "notional"]:
        _assert(key in payload, f"trade payload missing {key}", failures)

    dedupe = payload.get("dedupe_hint", {})
    unified_key = dedupe.get("unified_key", {})
    _assert(dedupe.get("entity_kind") == "trade", "trade dedupe_hint.entity_kind must be trade", failures)
    _assert(
        unified_key.get("instrument_id") == "bitflyer.spot.BTC_JPY",
        "trade dedupe unified_key.instrument_id must be bitflyer.spot.BTC_JPY",
        failures,
    )
    _assert(dedupe.get("native_id_required") is True, "trade native_id_required must be true", failures)
    _assert(dedupe.get("fallback_key_enabled") is False, "trade fallback_key_enabled must be false", failures)

    comp = payload.get("completeness_hint", {})
    _assert(comp.get("evaluation_unit") == "trade_event", "trade completeness evaluation_unit must be trade_event", failures)

    origin = payload.get("origin_hint", {})
    _assert(origin.get("source_layer") == "collector", "trade origin_hint.source_layer must be collector", failures)


def _check_board(record: Dict[str, Any], failures: List[str]) -> None:
    _check_common_canonical(record, failures)
    payload = record.get("payload", {})

    dedupe = payload.get("dedupe_hint", {})
    event_key = dedupe.get("event_dedupe_key", {})
    series_key = dedupe.get("series_key", {})
    _assert(dedupe.get("entity_kind") == "board", "board dedupe_hint.entity_kind must be board", failures)
    _assert(
        event_key.get("instrument_id") == "bitflyer.spot.BTC_JPY",
        "board event_dedupe_key.instrument_id must be bitflyer.spot.BTC_JPY",
        failures,
    )
    _assert(
        series_key.get("instrument_id") == "bitflyer.spot.BTC_JPY",
        "board series_key.instrument_id must be bitflyer.spot.BTC_JPY",
        failures,
    )

    comp = payload.get("completeness_hint", {})
    _assert(comp.get("evaluation_unit") == "board_series", "board completeness evaluation_unit must be board_series", failures)

    origin = payload.get("origin_hint", {})
    _assert(origin.get("source_layer") == "collector", "board origin_hint.source_layer must be collector", failures)


def main() -> int:
    tmp_root = _setup_env()
    cfg = load_config()

    seq = SequenceManager.start(1)
    session_id = make_session_id(cfg.collector_id)

    results = {
        "rest_board": None,
        "rest_trades": None,
        "ws_trade": None,
        "ws_board": None,
    }

    failures: List[str] = []

    try:
        results["rest_board"] = emit_rest_board_snapshot(seq, session_id)
    except Exception as exc:
        failures.append(f"rest_board failed: {exc}")

    try:
        results["rest_trades"] = emit_rest_trades(seq, session_id)
    except Exception as exc:
        failures.append(f"rest_trades failed: {exc}")

    try:
        results["ws_trade"] = emit_ws_trade_smoke(seq, session_id)
    except Exception as exc:
        failures.append(f"ws_trade failed: {exc}")

    try:
        results["ws_board"] = emit_ws_board_smoke(seq, session_id)
    except Exception as exc:
        failures.append(f"ws_board failed: {exc}")

    canonical_root = tmp_root / "data" / "market_data"
    records = list(_iter_jsonl(canonical_root))

    trade = _find_first(records, "market.trade")
    board_snapshot = _find_first(records, "market.orderbook.snapshot")
    board_diff = _find_first(records, "market.orderbook.diff")

    _assert(trade is not None, "canonical market.trade not found", failures)
    _assert(board_snapshot is not None, "canonical market.orderbook.snapshot not found", failures)
    _assert(board_diff is not None, "canonical market.orderbook.diff not found", failures)

    if trade is not None:
        _check_trade(trade, failures)
    if board_snapshot is not None:
        _check_board(board_snapshot, failures)
    if board_diff is not None:
        _check_board(board_diff, failures)

    summary = {
        "tmp_root": str(tmp_root),
        "results": results,
        "canonical_record_count": len(records),
        "failures": failures,
        "ok": len(failures) == 0,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
