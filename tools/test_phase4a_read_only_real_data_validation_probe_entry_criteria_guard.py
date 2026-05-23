# path: ./tools/test_phase4a_read_only_real_data_validation_probe_entry_criteria_guard.py
# desc: Phase 4-A read-only real-data validation probe entry criteria guard.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(os.environ.get("BTC_TS_ROOT") or os.environ.get("BTC_TS_DATA_ROOT") or r"E:\btc_ts")
DATA_DIR = Path(os.environ.get("BTC_TS_DATA_DIR") or (DATA_ROOT / "data"))

DOC_PATH = "tmp/docs/architecture/PHASE4A_READ_ONLY_REAL_DATA_VALIDATION_PROBE_ENTRY_CRITERIA_2026-05-23.md"
EXECUTION_DOC_PATH = "tmp/docs/architecture/PHASE4A_EXECUTION_REVIEW_HINT_ENTRY_CRITERIA_2026-05-23.md"
POSITION_DOC_PATH = "tmp/docs/architecture/PHASE4A_POSITION_REVIEW_HINT_ENTRY_CRITERIA_2026-05-23.md"
DIRECTION_HANDOFF_PATH = "tmp/docs/architecture/PHASE4A_DIRECTION_SLICE_HANDOFF_SUMMARY_2026-05-23.md"
INDEX_PATH = "tmp/docs/_INDEX.md"
STATUS_PATH = "tmp/gpt_room/08_STATUS.md"
FOCUS_PATH = "tmp/gpt_room/09_FOCUS.json"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"
# Do not invoke PRIMARY_GUARD_PATH from this guard; primary invokes this guard after connection.
EXECUTION_GUARD_PATH = "tools/test_phase4a_execution_review_hint_entry_criteria_guard.py"

COMPILE_TARGETS = [
    PRIMARY_GUARD_PATH,
    EXECUTION_GUARD_PATH,
    "tools/test_phase4a_position_review_hint_entry_criteria_guard.py",
    "tools/test_phase4a_direction_unconnected_scope_cleanup_guard.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_direction_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_position_review_hint_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_execution_review_hint_contract.py",
]

FORBIDDEN_PROBE_LOCATIONS = [
    "btcts_next/src/btcts/apps/operator_ui",
    "btcts_next/src/btcts/market_engine",
    "btcts_next/src/btcts/execution",
    "btcts_next/src/btcts/broker",
]

FORBIDDEN_MUTATION_TOKENS = [
    "open( DATA_ROOT",
    "open(DATA_ROOT",
    "open( DATA_DIR",
    "open(DATA_DIR",
    ".write_text(",
    ".write_bytes(",
    "mkdir(",
    "unlink(",
    "remove(",
    "rmdir(",
    "shutil.rmtree",
    "subprocess.run([\"git",
    "place_order",
    "broker_order",
    "live_order_placement",
    "auto_trade",
]


def _read_text(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _compile_targets(failures: List[str]) -> Dict[str, Any]:
    passed: List[str] = []
    failed: List[Dict[str, str]] = []
    cache_root = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "read_only_real_data_validation_probe_entry"
    cache_root.mkdir(parents=True, exist_ok=True)

    for rel_path in COMPILE_TARGETS:
        path = REPO_ROOT / rel_path
        if not path.exists():
            failed.append({"path": rel_path, "error": "missing"})
            failures.append(f"compile target missing: {rel_path}")
            continue
        try:
            cfile = cache_root / (rel_path.replace("/", "__").replace("\\", "__") + ".pyc")
            py_compile.compile(str(path), cfile=str(cfile), doraise=True)
            passed.append(rel_path)
        except Exception as exc:
            failed.append({"path": rel_path, "error": str(exc)})
            failures.append(f"py_compile failed: {rel_path}: {exc}")

    return {"passed_count": len(passed), "failed": failed}


def _run_json_guard(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / rel_path)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=900,
    )
    parsed: Dict[str, Any] | None = None
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"json guard did not emit valid JSON: {rel_path}: {exc}")

    ok = proc.returncode == 0 and isinstance(parsed, dict) and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"json guard must return ok true and failures []: {rel_path}")
    return {
        "returncode": proc.returncode,
        "ok": bool(ok),
        "phase": parsed.get("phase") if isinstance(parsed, dict) else None,
        "stdout_tail": (proc.stdout or "")[-1600:],
        "stderr_tail": (proc.stderr or "")[-1600:],
    }



def _check_primary_guard_connection_static(failures: List[str]) -> Dict[str, Any]:
    """Check primary connection without invoking primary guard.

    The primary guard invokes this guard after connection. Calling primary from
    here would create a recursive guard cycle:

        real_data_entry_guard -> primary_guard -> real_data_entry_guard

    Therefore this guard checks the primary file statically and leaves full
    primary execution to the caller.
    """
    text = _read_text(PRIMARY_GUARD_PATH)
    required = [
        "tools/test_phase4a_read_only_real_data_validation_probe_entry_criteria_guard.py",
        "read_only_real_data_validation_probe_entry_criteria_guard",
    ]
    missing: List[str] = []
    for fragment in required:
        if fragment not in text:
            failures.append(f"primary guard missing real-data validation entry connection: {fragment}")
            missing.append(fragment)
    return {"missing_count": len(missing), "missing": missing}

def _check_docs(failures: List[str]) -> Dict[str, Any]:
    required = {
        DOC_PATH: [
            "read-only real-data validation probe entry criteria",
            "Real-data validation probe is read-only.",
            "Real-data validation probe must not mutate collector state.",
            "Allowed output target for probe summaries",
            "tools/test_phase4a_read_only_real_data_validation_probe_entry_criteria_guard.py",
        ],
        EXECUTION_DOC_PATH: [
            "Execution review hint contract skeleton post-commit checkpoint is complete",
            "commit = 1cc5b13d Add guarded Execution review hint contract skeleton",
            "Execution remains review-only timing / urgency / feasibility contract.",
        ],
        POSITION_DOC_PATH: [
            "Position review hint contract skeleton post-commit checkpoint is complete",
            "commit = fae01765 Add guarded Position review hint contract skeleton",
        ],
        DIRECTION_HANDOFF_PATH: [
            "commit = d7779763 Add guarded Direction replay material slice",
            "Direction slice does not open runtime/UI/market_engine/Position/Execution.",
        ],
        INDEX_PATH: [
            "PHASE4A_READ_ONLY_REAL_DATA_VALIDATION_PROBE_ENTRY_CRITERIA_2026-05-23.md",
            "read-only real-data validation probe entry criteria",
            "Execution review hint contract skeleton close / commit checkpoint complete",
        ],
        STATUS_PATH: [
            "read-only real-data validation probe entry criteria",
            "収集済み BTC / bitFlyer data を読むだけ",
            "collector state / runtime / UI / market_engine / broker-order は変更しない",
        ],
        FOCUS_PATH: [
            "phase4a_read_only_real_data_validation_probe_entry_criteria",
            "read_only_real_data_validation_probe_entry_criteria_only",
            "real_data_validation_probe_must_not_mutate_collector_runtime_ui_market_engine_or_broker_order",
        ],
    }
    missing: List[Dict[str, str]] = []
    for rel_path, fragments in required.items():
        text = _read_text(rel_path)
        if not text:
            failures.append(f"required doc/status/focus missing or empty: {rel_path}")
            missing.append({"path": rel_path, "fragment": "__missing_or_empty__"})
            continue
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"required doc/status/focus fragment missing: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})

    index_text = _read_text(INDEX_PATH)
    current_pos = index_text.find("### current formal spec")
    real_data_pos = index_text.find("PHASE4A_READ_ONLY_REAL_DATA_VALIDATION_PROBE_ENTRY_CRITERIA_2026-05-23.md")
    execution_pos = index_text.find("PHASE4A_EXECUTION_REVIEW_HINT_ENTRY_CRITERIA_2026-05-23.md")
    ordering_ok = current_pos >= 0 and real_data_pos >= 0 and execution_pos >= 0 and current_pos < real_data_pos < execution_pos
    if not ordering_ok:
        failures.append("real-data validation probe entry criteria doc must be first current formal spec")

    return {"missing_count": len(missing), "missing": missing, "ordering_ok": bool(ordering_ok)}


def _check_data_inventory(failures: List[str]) -> Dict[str, Any]:
    collector_raw = DATA_DIR / "collector_raw"
    target = collector_raw / "exchange=bitflyer" / "symbol=BTC_JPY"
    channel_counts: Dict[str, int] = {}
    latest_dates: Dict[str, str | None] = {}

    if not DATA_ROOT.exists():
        failures.append(f"DATA_ROOT missing: {DATA_ROOT}")
    if not DATA_DIR.exists():
        failures.append(f"DATA_DIR missing: {DATA_DIR}")
    if not collector_raw.exists():
        failures.append(f"collector_raw missing: {collector_raw}")
    if not target.exists():
        failures.append(f"BTC/bitFlyer collector_raw partition missing: {target}")

    if target.exists():
        for channel_dir in sorted(path for path in target.glob("channel=*") if path.is_dir()):
            dates = sorted(path.name for path in channel_dir.glob("date=*") if path.is_dir())
            channel = channel_dir.name.removeprefix("channel=")
            channel_counts[channel] = len(dates)
            latest_dates[channel] = dates[-1].removeprefix("date=") if dates else None

    if not channel_counts:
        failures.append("BTC/bitFlyer collector_raw partition has no channel directories")

    board_snapshot_count = channel_counts.get("board_snapshot", 0)
    if board_snapshot_count <= 0:
        failures.append("BTC/bitFlyer collector_raw board_snapshot channel must have date partitions")

    return {
        "data_root": str(DATA_ROOT),
        "data_dir": str(DATA_DIR),
        "collector_raw": str(collector_raw),
        "target_partition": str(target),
        "channel_counts": channel_counts,
        "latest_dates": latest_dates,
    }


def _check_no_probe_runtime_opening(failures: List[str]) -> Dict[str, Any]:
    hits: List[Dict[str, str]] = []
    candidate_paths = [
        "tools/probe_phase4a_read_only_real_data_validation_inventory.py",
    ]

    for rel_path in candidate_paths:
        path = REPO_ROOT / rel_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_MUTATION_TOKENS:
            if token in text:
                hits.append({"path": rel_path, "token": token})
                failures.append(f"real-data validation probe contains forbidden mutation/runtime token: {rel_path}: {token}")

    forbidden_path_hits: List[str] = []
    for rel in FORBIDDEN_PROBE_LOCATIONS:
        root = REPO_ROOT / rel
        if not root.exists():
            continue
        for path in root.rglob("*real_data*probe*.py"):
            rel_path = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            forbidden_path_hits.append(rel_path)
            failures.append(f"real-data validation probe must not live in runtime/UI/market_engine/broker path: {rel_path}")

    return {
        "forbidden_token_hit_count": len(hits),
        "forbidden_token_hits": hits,
        "forbidden_path_hit_count": len(forbidden_path_hits),
        "forbidden_path_hits": forbidden_path_hits,
    }


def main() -> int:
    failures: List[str] = []

    compile_result = _compile_targets(failures)
    execution_guard = _run_json_guard(EXECUTION_GUARD_PATH, failures)
    primary_guard_connection = _check_primary_guard_connection_static(failures)
    docs = _check_docs(failures)
    data_inventory = _check_data_inventory(failures)
    no_probe_runtime_opening = _check_no_probe_runtime_opening(failures)

    summary = {
        "phase": "phase4a_read_only_real_data_validation_probe_entry_criteria_guard",
        "checks": {
            "compile": compile_result,
            "execution_guard": execution_guard,
            "primary_guard_connection": primary_guard_connection,
            "docs": docs,
            "data_inventory": data_inventory,
            "no_probe_runtime_opening": no_probe_runtime_opening,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
