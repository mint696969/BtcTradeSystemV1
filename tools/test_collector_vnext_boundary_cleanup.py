# path: ./tools/test_collector_vnext_boundary_cleanup.py
# desc: Verify Collector vNext boundary-cleanup invariants for Layer2 board canonical, compact removal, and smoke/runtime split.

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
from btcts.ingestion.l2_canonical import (
    make_orderbook_event_payload,
    make_orderbook_snapshot_payload,
    make_trade_event_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _setup_env() -> Path:
    tmp_root = REPO_ROOT / "tmp" / "_vnext_boundary_cleanup_test"

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


def _check_no_compact_root(cfg, failures: List[str]) -> None:
    roots = cfg.roots()
    _assert("compact" not in roots, 'config.roots() must not expose "compact"', failures)


def _check_runtime_placeholder(failures: List[str]) -> None:
    runtime_path = REPO_ROOT / "btcts_next" / "src" / "btcts" / "collector_vnext" / "runtime.py"
    _assert(runtime_path.exists(), "runtime.py must exist as production-runtime placeholder", failures)

    text = runtime_path.read_text(encoding="utf-8")
    _assert(
        "production runtime is not implemented yet" in text,
        "runtime.py must clearly state that production runtime is not implemented yet",
        failures,
    )


def _check_smoke_labels(failures: List[str]) -> None:
    app_path = REPO_ROOT / "btcts_next" / "src" / "btcts" / "collector_vnext" / "app.py"
    daemon_path = REPO_ROOT / "btcts_next" / "src" / "btcts" / "collector_vnext" / "daemon.py"
    run_ps1 = REPO_ROOT / "tools" / "run_collector_vnext.ps1"
    run_daemon_ps1 = REPO_ROOT / "tools" / "run_collector_vnext_daemon.ps1"

    app_text = app_path.read_text(encoding="utf-8")
    daemon_text = daemon_path.read_text(encoding="utf-8")
    run_ps1_text = run_ps1.read_text(encoding="utf-8")
    run_daemon_ps1_text = run_daemon_ps1.read_text(encoding="utf-8")

    _assert("Smoke entrypoint" in app_text, "app.py must be labeled as smoke entrypoint", failures)
    _assert("smoke cycle completed" in app_text, "app.py status message must mention smoke cycle", failures)
    _assert("Smoke daemon" in daemon_text, "daemon.py must be labeled as smoke daemon", failures)
    _assert("smoke daemon" in daemon_text, "daemon.py messages must mention smoke daemon", failures)
    _assert("Safe smoke launcher" in run_ps1_text, "run_collector_vnext.ps1 must be labeled as smoke launcher", failures)
    _assert(
        "Safe smoke-daemon launcher" in run_daemon_ps1_text,
        "run_collector_vnext_daemon.ps1 must be labeled as smoke-daemon launcher",
        failures,
    )


def _check_compact_artifacts_removed(failures: List[str]) -> None:
    removed_file = REPO_ROOT / "btcts_next" / "src" / "btcts" / "collector_vnext" / "transforms" / "raw_to_compact.py"
    _assert(not removed_file.exists(), "raw_to_compact.py must be removed", failures)

    writer_path = REPO_ROOT / "btcts_next" / "src" / "btcts" / "collector_vnext" / "writer.py"
    paths_path = REPO_ROOT / "btcts_next" / "src" / "btcts" / "collector_vnext" / "paths.py"

    writer_text = writer_path.read_text(encoding="utf-8")
    paths_text = paths_path.read_text(encoding="utf-8")

    _assert("def write_compact" not in writer_text, "writer.py must not define write_compact", failures)
    _assert("compact_dir" not in paths_text, "paths.py must not define compact_dir", failures)


def _check_unified_ws_board_lane_contract(failures: List[str]) -> None:
    lane_path = REPO_ROOT / "btcts_next" / "src" / "btcts" / "collector_vnext" / "unified_ws_board_lane.py"
    emit_rest_path = REPO_ROOT / "btcts_next" / "src" / "btcts" / "collector_vnext" / "emit_rest.py"
    helper_path = REPO_ROOT / "btcts_next" / "src" / "btcts" / "collector_vnext" / "transforms" / "board_structural_hints.py"
    _assert(lane_path.exists(), "unified_ws_board_lane.py must exist", failures)
    _assert(emit_rest_path.exists(), "emit_rest.py must exist", failures)
    _assert(helper_path.exists(), "board_structural_hints.py must exist", failures)

    text = lane_path.read_text(encoding="utf-8")
    emit_rest_text = emit_rest_path.read_text(encoding="utf-8") if emit_rest_path.exists() else ""
    helper_text = helper_path.read_text(encoding="utf-8") if helper_path.exists() else ""
    _assert("def apply_board_structural_hints" in helper_text, "board structural hint helper must expose apply_board_structural_hints", failures)
    _assert(
        (
            "from .transforms.board_structural_hints import apply_board_structural_hints" in emit_rest_text
            or "from .transforms.facade import (" in emit_rest_text
        ),
        "emit_rest.py must import board structural hint helper directly or through Phase F facade",
        failures,
    )
    _assert("apply_board_structural_hints(" in emit_rest_text, "emit_rest.py must use board structural hint helper for board payload", failures)

    required_fragments = [
        'event_id_kind = "snapshot" if is_snapshot else "delta"',
        'f"bitflyer:unified:board_ws:{stream_session_id}:{event_id_kind}:{board_event_no}"',
        'canonical_payload["stream_event_no"] = board_event_no',
        'canonical_payload["snapshot_id"] = current_event_id if is_snapshot else None',
        'canonical_payload["base_snapshot_id"] = current_base_snapshot_id',
        'canonical_payload["prev_event_id"] = last_board_event_id',
        'canonical_payload["rebuild_required"] = current_base_snapshot_id is None and not is_snapshot',
        'canonical_payload["is_gap_fill"] = False',
        'canonical_payload["is_resync"] = False',
        "apply_board_structural_hints(",
        "lane_snapshot = self.snapshot()",
    ]
    for fragment in required_fragments:
        _assert(fragment in text, f"unified ws board lane missing contract fragment: {fragment}", failures)

    unknown_guard_pos = text.find('if message_kind == "unknown":')
    increment_pos = text.find("board_event_no += 1", unknown_guard_pos)
    _assert(unknown_guard_pos >= 0, "unified ws board lane must guard unknown board messages", failures)
    _assert(increment_pos > unknown_guard_pos, "board_event_no must increment after unknown-message guard", failures)

    lane_snapshot_pos = text.find("lane_snapshot = self.snapshot()")
    state_update_pos = text.find('saw_snapshot=bool(lane_snapshot.get("saw_snapshot"))')
    _assert(lane_snapshot_pos >= 0, "lane_snapshot must be captured before state update", failures)
    _assert(state_update_pos > lane_snapshot_pos, "lane_snapshot must be defined before saw_snapshot state update", failures)

    reconnect_except_pos = text.find("except Exception as exc:")
    reconnect_prev_reset_pos = text.find("last_board_event_id = None", reconnect_except_pos)
    reconnect_base_reset_pos = text.find("current_base_snapshot_id = None", reconnect_except_pos)
    _assert(reconnect_except_pos >= 0, "unified ws board lane must handle reconnect exceptions", failures)
    _assert(
        reconnect_prev_reset_pos > reconnect_except_pos,
        "unified ws board lane must reset prev event chain on reconnect",
        failures,
    )
    _assert(
        reconnect_base_reset_pos > reconnect_except_pos,
        "unified ws board lane must reset base snapshot chain on reconnect",
        failures,
    )


def _check_l2_canonical_public_boundary_contract(failures: List[str]) -> None:
    public_init_path = REPO_ROOT / "btcts_next" / "src" / "btcts" / "ingestion" / "l2_canonical" / "__init__.py"
    _assert(public_init_path.exists(), "L2 canonical public __init__.py must exist", failures)

    text = public_init_path.read_text(encoding="utf-8") if public_init_path.exists() else ""
    required_exports = [
        "OrderBookRebuilder",
        "OrderBookState",
        "TradeAggregator",
        "make_orderbook_event_payload",
        "make_orderbook_snapshot_payload",
        "make_trade_event_payload",
        "normalize_orderbook_levels",
    ]
    for name in required_exports:
        _assert(name in text, f"L2 canonical public boundary must export: {name}", failures)

    _assert("collector_vnext" not in text, "L2 canonical public boundary must not depend on collector_vnext", failures)


def _check_l2_canonical_no_collector_reverse_dependency(failures: List[str]) -> None:
    l2_root = REPO_ROOT / "btcts_next" / "src" / "btcts" / "ingestion" / "l2_canonical"
    _assert(l2_root.exists(), "L2 canonical root must exist", failures)

    for path in l2_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(REPO_ROOT)
        _assert(
            "collector_vnext" not in text,
            f"L2 canonical file must not depend on collector_vnext: {rel}",
            failures,
        )
        _assert(
            "btcts.collector_vnext" not in text,
            f"L2 canonical file must not import collector_vnext: {rel}",
            failures,
        )


def _check_collector_transforms_use_l2_public_boundary_only(failures: List[str]) -> None:
    transforms_root = REPO_ROOT / "btcts_next" / "src" / "btcts" / "collector_vnext" / "transforms"
    _assert(transforms_root.exists(), "collector_vnext/transforms must exist", failures)

    forbidden_import_fragments = [
        "btcts.ingestion.l2_canonical.orderbook.payload",
        "btcts.ingestion.l2_canonical.tradeflow.payload",
    ]

    for path in transforms_root.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(REPO_ROOT)

        for fragment in forbidden_import_fragments:
            _assert(
                fragment not in text,
                f"collector transform must not import L2 private payload module directly: {rel} -> {fragment}",
                failures,
            )


def _check_orderbook_l2_payload_owner_contract(failures: List[str]) -> None:
    owner_path = REPO_ROOT / "btcts_next" / "src" / "btcts" / "ingestion" / "l2_canonical" / "orderbook" / "payload.py"
    rest_transform_path = REPO_ROOT / "btcts_next" / "src" / "btcts" / "collector_vnext" / "transforms" / "raw_to_canonical.py"
    ws_transform_path = REPO_ROOT / "btcts_next" / "src" / "btcts" / "collector_vnext" / "transforms" / "ws_board_to_canonical.py"

    _assert(owner_path.exists(), "L2 orderbook payload owner must exist", failures)
    _assert(rest_transform_path.exists(), "raw_to_canonical.py must exist", failures)
    _assert(ws_transform_path.exists(), "ws_board_to_canonical.py must exist", failures)

    owner_text = owner_path.read_text(encoding="utf-8") if owner_path.exists() else ""
    rest_text = rest_transform_path.read_text(encoding="utf-8") if rest_transform_path.exists() else ""
    ws_text = ws_transform_path.read_text(encoding="utf-8") if ws_transform_path.exists() else ""

    _assert("def make_orderbook_snapshot_payload" in owner_text, "L2 owner must expose make_orderbook_snapshot_payload", failures)
    _assert("def make_orderbook_event_payload" in owner_text, "L2 owner must expose make_orderbook_event_payload", failures)
    _assert("def normalize_orderbook_levels" in owner_text, "L2 owner must expose normalize_orderbook_levels", failures)

    _assert(
        "from btcts.ingestion.l2_canonical import make_orderbook_snapshot_payload" in rest_text,
        "REST board transform must delegate payload shape through L2 public boundary",
        failures,
    )
    _assert(
        "from btcts.ingestion.l2_canonical import make_orderbook_event_payload" in ws_text,
        "WS board transform must delegate payload shape through L2 public boundary",
        failures,
    )
    _assert(
        "btcts.ingestion.l2_canonical.orderbook.payload" not in rest_text,
        "REST board transform must not import L2 owner private payload module directly",
        failures,
    )
    _assert(
        "btcts.ingestion.l2_canonical.orderbook.payload" not in ws_text,
        "WS board transform must not import L2 owner private payload module directly",
        failures,
    )

    _assert('"event_type": "snapshot"' not in rest_text, "REST board transform must not own canonical snapshot shape", failures)
    _assert('"event_type": "snapshot" if snapshot else "delta"' not in ws_text, "WS board transform must not own canonical event shape", failures)


def _check_trade_l2_payload_owner_contract(failures: List[str]) -> None:
    owner_path = REPO_ROOT / "btcts_next" / "src" / "btcts" / "ingestion" / "l2_canonical" / "tradeflow" / "payload.py"
    rest_transform_path = REPO_ROOT / "btcts_next" / "src" / "btcts" / "collector_vnext" / "transforms" / "raw_to_canonical_trades.py"
    ws_transform_path = REPO_ROOT / "btcts_next" / "src" / "btcts" / "collector_vnext" / "transforms" / "ws_trade_to_canonical.py"

    _assert(owner_path.exists(), "L2 trade payload owner must exist", failures)
    _assert(rest_transform_path.exists(), "raw_to_canonical_trades.py must exist", failures)
    _assert(ws_transform_path.exists(), "ws_trade_to_canonical.py must exist", failures)

    owner_text = owner_path.read_text(encoding="utf-8") if owner_path.exists() else ""
    rest_text = rest_transform_path.read_text(encoding="utf-8") if rest_transform_path.exists() else ""
    ws_text = ws_transform_path.read_text(encoding="utf-8") if ws_transform_path.exists() else ""

    _assert("def make_trade_event_payload" in owner_text, "L2 owner must expose make_trade_event_payload", failures)
    _assert(
        "from btcts.ingestion.l2_canonical import make_trade_event_payload" in rest_text,
        "REST trade transform must delegate payload shape through L2 public boundary",
        failures,
    )
    _assert(
        "from btcts.ingestion.l2_canonical import make_trade_event_payload" in ws_text,
        "WS trade transform must delegate payload shape through L2 public boundary",
        failures,
    )
    _assert(
        "btcts.ingestion.l2_canonical.tradeflow.payload" not in rest_text,
        "REST trade transform must not import L2 owner private payload module directly",
        failures,
    )
    _assert(
        "btcts.ingestion.l2_canonical.tradeflow.payload" not in ws_text,
        "WS trade transform must not import L2 owner private payload module directly",
        failures,
    )

    _assert('"trade_id":' not in rest_text, "REST trade transform must not own canonical trade shape", failures)
    _assert('"trade_id":' not in ws_text, "WS trade transform must not own canonical trade shape", failures)
    _assert('"notional":' not in rest_text, "REST trade transform must not own trade notional shape", failures)
    _assert('"notional":' not in ws_text, "WS trade transform must not own trade notional shape", failures)


def _check_l2_payload_function_contracts(failures: List[str]) -> None:
    snapshot = make_orderbook_snapshot_payload(
        bids=[{"price": "100", "size": "1.5"}, {"price": "bad", "size": "1"}],
        asks=[{"price": 101, "size": 2}],
        snapshot_id="snap-test",
        depth=10,
    )
    _assert(snapshot.get("event_type") == "snapshot", "L2 snapshot payload event_type must be snapshot", failures)
    _assert(snapshot.get("snapshot_id") == "snap-test", "L2 snapshot payload must preserve snapshot_id", failures)
    _assert(snapshot.get("base_snapshot_id") == "snap-test", "L2 snapshot payload base_snapshot_id must equal snapshot_id", failures)
    _assert(len(snapshot.get("bids", [])) == 1, "L2 snapshot payload must skip invalid bid levels", failures)
    _assert(len(snapshot.get("asks", [])) == 1, "L2 snapshot payload must normalize ask levels", failures)

    delta = make_orderbook_event_payload(
        event_type="delta",
        bids=[{"price": "100", "size": "0"}],
        asks=[{"price": "101", "size": "0.25"}],
    )
    _assert(delta.get("event_type") == "delta", "L2 event payload event_type must be delta", failures)
    _assert(delta.get("snapshot_id") is None, "L2 delta payload snapshot_id must default to None", failures)
    _assert(delta.get("base_snapshot_id") is None, "L2 delta payload base_snapshot_id must default to None", failures)
    _assert(delta.get("rebuild_required") is False, "L2 delta payload rebuild_required must default to False", failures)

    bad_event_raised = False
    try:
        make_orderbook_event_payload(event_type="bad", bids=[], asks=[])
    except ValueError:
        bad_event_raised = True
    _assert(bad_event_raised, "L2 orderbook payload owner must reject unsupported event_type", failures)

    trade = make_trade_event_payload(
        trade_id=123,
        side="BUY",
        price="100",
        size="0.5",
        trade_ts="2026-01-01T00:00:00Z",
    )
    _assert(isinstance(trade, dict), "L2 trade payload must return dict for valid trade", failures)
    if isinstance(trade, dict):
        _assert(trade.get("trade_id") == 123, "L2 trade payload must preserve trade_id", failures)
        _assert(trade.get("price") == 100.0, "L2 trade payload must normalize price", failures)
        _assert(trade.get("size") == 0.5, "L2 trade payload must normalize size", failures)
        _assert(trade.get("notional") == 50.0, "L2 trade payload must compute notional", failures)
        _assert(trade.get("liquidity_role") == "taker", "L2 trade payload liquidity_role must default to taker", failures)

    invalid_trade = make_trade_event_payload(
        trade_id=124,
        side="SELL",
        price="bad",
        size="0.5",
    )
    _assert(invalid_trade is None, "L2 trade payload must return None for invalid numeric trade fields", failures)


def _check_trade_structural_hint_contract(failures: List[str]) -> None:
    helper_path = REPO_ROOT / "btcts_next" / "src" / "btcts" / "collector_vnext" / "transforms" / "trade_structural_hints.py"
    emit_rest_path = REPO_ROOT / "btcts_next" / "src" / "btcts" / "collector_vnext" / "emit_rest.py"
    emit_ws_path = REPO_ROOT / "btcts_next" / "src" / "btcts" / "collector_vnext" / "emit_ws.py"

    _assert(helper_path.exists(), "trade_structural_hints.py must exist", failures)
    _assert(emit_rest_path.exists(), "emit_rest.py must exist", failures)
    _assert(emit_ws_path.exists(), "emit_ws.py must exist", failures)

    helper_text = helper_path.read_text(encoding="utf-8") if helper_path.exists() else ""
    emit_rest_text = emit_rest_path.read_text(encoding="utf-8") if emit_rest_path.exists() else ""
    emit_ws_text = emit_ws_path.read_text(encoding="utf-8") if emit_ws_path.exists() else ""

    _assert("def apply_trade_structural_hints" in helper_text, "trade structural hint helper must expose apply_trade_structural_hints", failures)
    _assert(
        (
            "from .transforms.trade_structural_hints import apply_trade_structural_hints" in emit_rest_text
            or "from .transforms.facade import (" in emit_rest_text
        ),
        "emit_rest.py must import trade structural hint helper directly or through Phase F facade",
        failures,
    )
    _assert(("from .transforms.trade_structural_hints import apply_trade_structural_hints" in emit_ws_text or "from .transforms.facade import (" in emit_ws_text), "emit_ws.py must import trade structural hint helper directly or through Phase F facade", failures)
    _assert("apply_trade_structural_hints(" in emit_rest_text, "emit_rest.py must use trade structural hint helper", failures)
    _assert("apply_trade_structural_hints(" in emit_ws_text, "emit_ws.py must use trade structural hint helper", failures)


def _check_board_payload(record: Dict[str, Any], *, require_stream_event_no: bool, failures: List[str]) -> None:
    payload = record.get("payload", {})
    _assert(isinstance(payload, dict), "board payload must be dict", failures)
    if not isinstance(payload, dict):
        return

    required_keys = [
        "event_type",
        "snapshot_id",
        "base_snapshot_id",
        "prev_event_id",
        "continuity_state",
        "rebuild_required",
        "is_gap_fill",
        "is_resync",
        "integration_hint",
        "dedupe_hint",
        "completeness_hint",
        "origin_hint",
        "bids",
        "asks",
    ]
    for key in required_keys:
        _assert(key in payload, f"board payload missing required key: {key}", failures)

    forbidden_keys = [
        "best_bid",
        "best_ask",
        "mid",
        "spread",
        "mid_price",
        "depth",
    ]
    for key in forbidden_keys:
        _assert(key not in payload, f"board payload must not contain convenience field: {key}", failures)

    if require_stream_event_no:
        _assert(payload.get("event_type") == "delta", "WS board diff payload event_type must be delta", failures)
        _assert("stream_event_no" in payload, "WS board payload must contain stream_event_no", failures)
        _assert(payload.get("snapshot_id") is None, "WS board diff snapshot_id must be None", failures)
        _assert(payload.get("base_snapshot_id") is not None, "WS board diff base_snapshot_id must be present", failures)
        _assert(payload.get("prev_event_id") is not None, "WS board diff prev_event_id must be present", failures)
    else:
        _assert(payload.get("event_type") == "snapshot", "REST board snapshot payload event_type must be snapshot", failures)
        _assert(payload.get("snapshot_id") is not None, "REST board snapshot snapshot_id must be present", failures)
        _assert(payload.get("base_snapshot_id") == payload.get("snapshot_id"), "REST board snapshot base_snapshot_id must equal snapshot_id", failures)
        _assert(payload.get("prev_event_id") is None, "REST board snapshot prev_event_id must be None", failures)


def _check_trade_payload(record: Dict[str, Any], *, failures: List[str]) -> None:
    payload = record.get("payload", {})
    _assert(isinstance(payload, dict), "trade payload must be dict", failures)
    if not isinstance(payload, dict):
        return

    required_keys = [
        "trade_id",
        "side",
        "price",
        "size",
        "notional",
        "liquidity_role",
        "trade_ts",
        "integration_hint",
        "dedupe_hint",
        "completeness_hint",
        "origin_hint",
    ]
    for key in required_keys:
        _assert(key in payload, f"trade payload missing required key: {key}", failures)

    _assert(payload.get("trade_id") is not None, "trade payload trade_id must be present", failures)
    _assert(payload.get("liquidity_role") == "taker", "trade payload liquidity_role must be taker", failures)
    _assert(payload.get("price") is not None, "trade payload price must be present", failures)
    _assert(payload.get("size") is not None, "trade payload size must be present", failures)


def main() -> int:
    tmp_root = _setup_env()
    cfg = load_config()

    failures: List[str] = []

    _check_no_compact_root(cfg, failures)
    _check_runtime_placeholder(failures)
    _check_smoke_labels(failures)
    _check_compact_artifacts_removed(failures)
    _check_unified_ws_board_lane_contract(failures)
    _check_l2_canonical_public_boundary_contract(failures)
    _check_l2_canonical_no_collector_reverse_dependency(failures)
    _check_collector_transforms_use_l2_public_boundary_only(failures)
    _check_orderbook_l2_payload_owner_contract(failures)
    _check_trade_l2_payload_owner_contract(failures)
    _check_l2_payload_function_contracts(failures)
    _check_trade_structural_hint_contract(failures)

    seq = SequenceManager.start(1)
    session_id = make_session_id(cfg.collector_id)

    results: Dict[str, Any] = {
        "rest_board": None,
        "rest_trades": None,
        "ws_trade": None,
        "ws_board": None,
    }

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

    _assert(results["rest_board"] is not None, "rest_board result must exist", failures)
    _assert(results["ws_board"] is not None, "ws_board result must exist", failures)

    if isinstance(results["rest_board"], dict):
        _assert("compact_path" not in results["rest_board"], "rest_board result must not expose compact_path", failures)

    canonical_root = tmp_root / "data" / "market_data"
    records = list(_iter_jsonl(canonical_root))

    board_snapshot = _find_first(records, "market.orderbook.snapshot")
    board_diff = _find_first(records, "market.orderbook.diff")
    trade_event = _find_first(records, "market.trade")

    _assert(board_snapshot is not None, "canonical market.orderbook.snapshot not found", failures)
    _assert(board_diff is not None, "canonical market.orderbook.diff not found", failures)
    _assert(trade_event is not None, "canonical market.trade not found", failures)

    if board_snapshot is not None:
        _check_board_payload(board_snapshot, require_stream_event_no=False, failures=failures)

    if board_diff is not None:
        _check_board_payload(board_diff, require_stream_event_no=True, failures=failures)

    if trade_event is not None:
        _check_trade_payload(trade_event, failures=failures)

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