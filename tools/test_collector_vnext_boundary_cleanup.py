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


def _check_board_payload(record: Dict[str, Any], *, require_stream_event_no: bool, failures: List[str]) -> None:
    payload = record.get("payload", {})
    _assert(isinstance(payload, dict), "board payload must be dict", failures)
    if not isinstance(payload, dict):
        return

    required_keys = [
        "snapshot_id",
        "base_snapshot_id",
        "prev_event_id",
        "continuity_state",
        "rebuild_required",
        "is_gap_fill",
        "is_resync",
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
        _assert("stream_event_no" in payload, "WS board payload must contain stream_event_no", failures)


def main() -> int:
    tmp_root = _setup_env()
    cfg = load_config()

    failures: List[str] = []

    _check_no_compact_root(cfg, failures)
    _check_runtime_placeholder(failures)
    _check_smoke_labels(failures)
    _check_compact_artifacts_removed(failures)

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

    _assert(board_snapshot is not None, "canonical market.orderbook.snapshot not found", failures)
    _assert(board_diff is not None, "canonical market.orderbook.diff not found", failures)

    if board_snapshot is not None:
        _check_board_payload(board_snapshot, require_stream_event_no=False, failures=failures)

    if board_diff is not None:
        _check_board_payload(board_diff, require_stream_event_no=True, failures=failures)

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