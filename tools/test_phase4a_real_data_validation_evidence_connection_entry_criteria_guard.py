# path: ./tools/test_phase4a_real_data_validation_evidence_connection_entry_criteria_guard.py
# desc: Phase 4-A real-data validation evidence connection entry criteria guard.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]

DOC_PATH = "tmp/docs/architecture/PHASE4A_REAL_DATA_VALIDATION_EVIDENCE_CONNECTION_ENTRY_CRITERIA_2026-05-26.md"
EXTENDED_DOC_PATH = "tmp/docs/architecture/PHASE4A_EXTENDED_REAL_DATA_VALIDATION_REVIEW_ENTRY_CRITERIA_2026-05-25.md"
ROADMAP_PATH = "tmp/docs/roadmap/PHASE4A_L3_FREEZE_TO_L2_CANONICAL_BOUNDARY_AND_UI_ROADMAP_2026-04-22.md"
HEALTH_SPEC_PATH = "tmp/docs/strategy/PHASE4A_HEALTH_BUNDLE_HUMAN_READABLE_OBSERVER_PACK_DRAFT_2026-04-22.md"
WARROOM_SPEC_PATH = "tmp/docs/strategy/PHASE4A_WARROOM_BUNDLE_MARKET_READING_PACK_DRAFT_2026-04-22.md"
INDEX_PATH = "tmp/docs/_INDEX.md"
STATUS_PATH = "tmp/gpt_room/08_STATUS.md"
FOCUS_PATH = "tmp/gpt_room/09_FOCUS.json"
STATE_PATH = "tmp/gpt_room/11_STATE.json"
HANDOFF_PATH = "tmp/gpt_room/memory/handoffs/2026-05-25_phase4a_extended_real_data_validation_review_slice_handoff.md"
EXTENDED_OUTPUT = "tmp/work/phase4a_extended_real_data_validation_review/probe_phase4a_extended_real_data_validation_review.out.json"
REVIEW_OUTPUT = "tmp/work/phase4a_extended_real_data_validation_review_entry/review_extended_real_data_validation_review_output_v1.out.json"
EXTENDED_GUARD_PATH = "tools/test_phase4a_extended_real_data_validation_review_entry_criteria_guard.py"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"
FUTURE_CONTRACT_PATH = "btcts_next/src/btcts/processing/l4_consumer_models/shared/real_data_validation_evidence.py"

COMPILE_TARGETS = [
    EXTENDED_GUARD_PATH,
]

FORBIDDEN_PATH_PREFIXES = [
    "btcts_next/src/btcts/apps/operator_ui",
    "btcts_next/src/btcts/market_engine",
    "btcts_next/src/btcts/execution",
    "btcts_next/src/btcts/broker",
    "btcts_next/src/btcts/collector",
    "btcts_next/src/btcts/collector_vnext",
]


def _read_text(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _compile_targets(failures: List[str]) -> Dict[str, Any]:
    passed = []
    failed = []
    cache_root = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "real_data_validation_evidence_connection_entry"
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


def _run_json(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=1800)
    parsed = None
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"json command did not emit valid JSON: {rel_path}: {exc}")
    ok = proc.returncode == 0 and isinstance(parsed, dict) and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"json command must return ok true and failures []: {rel_path}")
    return {"returncode": proc.returncode, "ok": bool(ok), "phase": parsed.get("phase") if isinstance(parsed, dict) else None, "stdout_tail": (proc.stdout or "")[-1800:], "stderr_tail": (proc.stderr or "")[-1200:]}


def _load_json(rel_path: str, failures: List[str], label: str) -> Dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"{label} missing: {rel_path}")
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        failures.append(f"{label} invalid JSON: {exc}")
        return {}
    if not isinstance(data, dict):
        failures.append(f"{label} must be object")
        return {}
    if data.get("ok") is not True or data.get("failures") != []:
        failures.append(f"{label} must be ok true and failures []")
    return data


def _check_docs(failures: List[str]) -> Dict[str, Any]:
    required = {
        DOC_PATH: [
            "real-data validation evidence connection entry criteria",
            "This entry does not open runtime wiring yet.",
            "This entry does not open UI surfacing yet.",
            "real-data validation evidence connection != runtime signal",
            "real-data validation evidence read-only contract / adapter skeleton only",
            "tools/test_phase4a_real_data_validation_evidence_connection_entry_criteria_guard.py",
        ],
        EXTENDED_DOC_PATH: [
            "## 14. Extended real-data validation review slice final close checkpoint",
            "The extended real-data validation review slice is closed and handed off.",
            "It does not open runtime, UI, market_engine, collector writer/backfill, broker-order, inference, training, or live trading behavior.",
        ],
        ROADMAP_PATH: [
            "Phase D  L4 bundle strengthen for Health / WarRoom",
            "Phase E  UI surfacing for human-readable operational reading",
            "Health タブで「届いている truth」と「観測可能性」が読める",
            "WarRoom タブで「今どう読むべきか」が読める",
        ],
        HEALTH_SPEC_PATH: [
            "Health = system truth / semantic observability / orderbook observability / active event observability",
            "Health は observer-first",
        ],
        WARROOM_SPEC_PATH: [
            "WarRoom = current market reading / current active event reading / tactic reading / operator support",
            "WarRoom は market reading / operator support consumer であり owner ではない",
        ],
        INDEX_PATH: [
            "PHASE4A_REAL_DATA_VALIDATION_EVIDENCE_CONNECTION_ENTRY_CRITERIA_2026-05-26.md",
            "PHASE4A_EXTENDED_REAL_DATA_VALIDATION_REVIEW_ENTRY_CRITERIA_2026-05-25.md",
        ],
        STATUS_PATH: [
            "extended real-data validation review slice final close checkpoint",
            "次に新しい境界を開く場合は、必ず別 entry criteria/spec と guard から開始する",
        ],
        FOCUS_PATH: [
            "real_data_validation_evidence_connection_entry_commit_checkpoint_e15a5b59_is_complete",
            "treat_real_data_validation_evidence_connection_entry_guard_as_closed_and_saved",
            "next_connect_real_data_validation_evidence_connection_entry_guard_to_primary_or_open_contract_only_if_guarded",
            "do_not_open_ui_runtime_market_engine_collector_writer_broker_order_inference_training_from_evidence_entry_checkpoint",
        ],
        HANDOFF_PATH: [
            "Phase 4-A extended real-data validation review slice handoff",
            "Responsibility boundaries preserved",
        ],
    }
    missing = []
    for rel_path, fragments in required.items():
        text = _read_text(rel_path)
        if not text:
            failures.append(f"required file missing or empty: {rel_path}")
            missing.append({"path": rel_path, "fragment": "__missing_or_empty__"})
            continue
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"required fragment missing: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})

    index_text = _read_text(INDEX_PATH)
    current_pos = index_text.find("### current formal spec")
    evidence_pos = index_text.find("PHASE4A_REAL_DATA_VALIDATION_EVIDENCE_CONNECTION_ENTRY_CRITERIA_2026-05-26.md")
    extended_pos = index_text.find("PHASE4A_EXTENDED_REAL_DATA_VALIDATION_REVIEW_ENTRY_CRITERIA_2026-05-25.md")
    ordering_ok = current_pos >= 0 and evidence_pos >= 0 and extended_pos >= 0 and current_pos < evidence_pos < extended_pos
    if not ordering_ok:
        failures.append("real-data validation evidence connection entry doc must be first current formal spec")
    return {"missing_count": len(missing), "missing": missing, "ordering_ok": bool(ordering_ok)}


def _check_outputs(failures: List[str]) -> Dict[str, Any]:
    extended = _load_json(EXTENDED_OUTPUT, failures, "extended output")
    review = _load_json(REVIEW_OUTPUT, failures, "review output")
    rows: Dict[str, Any] = {}
    if extended:
        totals = extended.get("totals", {}) if isinstance(extended.get("totals"), dict) else {}
        channel = extended.get("channel_review", {}) if isinstance(extended.get("channel_review"), dict) else {}
        expected = {
            "inventory_json_ok_count": 36,
            "inventory_json_error_count": 0,
            "replay_json_ok_count": 36,
            "replay_json_error_count": 0,
            "replay_row_count": 36,
            "report_board_count": 18,
            "report_trade_count": 18,
        }
        mismatches = []
        for key, expected_value in expected.items():
            actual = totals.get(key)
            if actual != expected_value:
                mismatches.append({"key": key, "actual": actual, "expected": expected_value})
                failures.append(f"extended output mismatch: {key}: {actual} expected {expected_value}")
        if channel.get("channel_count") != 4:
            failures.append(f"extended channel_count must be 4: {channel.get('channel_count')}")
        rows["extended"] = {"mismatches": mismatches, "channel_count": channel.get("channel_count"), "totals": totals}
    if review:
        checks = review.get("checks", {}) if isinstance(review.get("checks"), dict) else {}
        channel = checks.get("channel_review", {}) if isinstance(checks.get("channel_review"), dict) else {}
        baseline = checks.get("baseline_comparison", {}) if isinstance(checks.get("baseline_comparison"), dict) else {}
        if channel.get("total_replay_rows") != 36:
            failures.append(f"review total_replay_rows must be 36: {channel.get('total_replay_rows')}")
        if baseline.get("monotonic_check_count") != 7:
            failures.append(f"review monotonic_check_count must be 7: {baseline.get('monotonic_check_count')}")
        rows["review"] = {"total_replay_rows": channel.get("total_replay_rows"), "monotonic_check_count": baseline.get("monotonic_check_count")}
    return rows


def _check_future_contract_not_opened(failures: List[str]) -> Dict[str, Any]:
    path = REPO_ROOT / FUTURE_CONTRACT_PATH
    if not path.exists():
        failures.append(f"evidence contract skeleton must exist after guarded opening: {FUTURE_CONTRACT_PATH}")
        return {"exists": False, "path": FUTURE_CONTRACT_PATH, "missing": [FUTURE_CONTRACT_PATH], "forbidden": []}
    text = path.read_text(encoding="utf-8")
    required = [
        "class RealDataValidationEvidenceSummary",
        "build_real_data_validation_evidence_summary",
        "real_data_validation_evidence_summary_to_snapshot",
        "read-only evidence summary contract",
        "diagnostic evidence only",
        "not runtime signal",
        "not UI rendering",
        "not market_engine input",
        "not collector writer/backfill",
        "not broker/order automation",
        "not inference or training input",
        "not_runtime_wiring",
        "not_ui_rendering",
        "not_market_engine_input",
        "not_collector_writer",
        "not_broker_or_order_automation",
        "not_inference_or_training",
    ]
    forbidden = [
        "runtime_state_path",
        "ui_route",
        "market_engine_signal",
        "collector_write_path",
        "order_size",
        "order_price",
        "broker_account",
        "place_order",
        "broker_order",
        "live_order_placement",
        "auto_trade",
        "training_dataset",
        "inference_job",
    ]
    missing = []
    forbidden_hits = []
    for fragment in required:
        if fragment not in text:
            missing.append(fragment)
            failures.append(f"evidence contract skeleton missing required fragment: {fragment}")
    for fragment in forbidden:
        if fragment in text:
            forbidden_hits.append(fragment)
            failures.append(f"evidence contract skeleton contains forbidden fragment: {fragment}")
    return {"exists": True, "path": FUTURE_CONTRACT_PATH, "missing": missing, "forbidden": forbidden_hits}


def _check_forbidden_path_opening(failures: List[str]) -> Dict[str, Any]:
    hits = []
    for rel in FORBIDDEN_PATH_PREFIXES:
        root = REPO_ROOT / rel
        if not root.exists():
            continue
        for path in root.rglob("*real_data*validation*evidence*.py"):
            rel_path = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            hits.append(rel_path)
            failures.append(f"real-data validation evidence connection must not live in forbidden path at entry stage: {rel_path}")
    return {"hit_count": len(hits), "hits": hits}


def _check_primary_connection_static(failures: List[str]) -> Dict[str, Any]:
    text = _read_text(PRIMARY_GUARD_PATH)
    required = [
        "tools/test_phase4a_extended_real_data_validation_review_entry_criteria_guard.py",
        "extended_real_data_validation_review_entry_criteria_guard",
        "tools/test_phase4a_real_data_validation_evidence_connection_entry_criteria_guard.py",
        "real_data_validation_evidence_connection_entry_criteria_guard",
    ]
    missing = []
    for fragment in required:
        if fragment not in text:
            missing.append(fragment)
            failures.append(f"primary guard missing evidence/extended connection: {fragment}")
    return {"missing_count": len(missing), "missing": missing}


def _check_extended_checkpoint_static(failures: List[str]) -> Dict[str, Any]:
    """Do not execute the extended guard from this primary-connected guard.

    The extended guard is itself primary-connected and runs broader/real-data child guards.
    Running it from evidence guard creates expensive nested guard chains and can produce
    order-dependent false failures. Verify durable checkpoint evidence and source presence instead.
    """
    required_by_file = {
        EXTENDED_DOC_PATH: [
            "## 14. Extended real-data validation review slice final close checkpoint",
            "The extended real-data validation review slice is closed and handed off.",
            "It does not open runtime, UI, market_engine, collector writer/backfill, broker-order, inference, training, or live trading behavior.",
        ],
        STATUS_PATH: [
            "extended real-data validation review slice final close checkpoint",
            "extended entry guard: failures [] / ok true",
            "Primary guard: failures [] / ok true",
        ],
        FOCUS_PATH: [
            "extended_real_data_validation_review_slice_final_cc_is_green",
            "extended_real_data_validation_review_slice_final_close_checkpoint_is_complete",
            "extended_real_data_validation_review_slice_final_commit_checkpoint_68a21e87_is_complete",
            "treat_extended_real_data_validation_review_slice_as_closed_and_handed_off",
        ],
        HANDOFF_PATH: [
            "Phase 4-A extended real-data validation review slice handoff",
            "Responsibility boundaries preserved",
        ],
    }
    missing = []
    for rel_path, fragments in required_by_file.items():
        text = _read_text(rel_path)
        if not text:
            failures.append(f"extended checkpoint file missing or empty: {rel_path}")
            missing.append({"path": rel_path, "fragment": "__missing_or_empty__"})
            continue
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"extended checkpoint fragment missing: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})

    guard_text = _read_text(EXTENDED_GUARD_PATH)
    source_missing = []
    for fragment in [
        "phase4a_extended_real_data_validation_review_entry_criteria_guard",
        "tools/probe_phase4a_extended_real_data_validation_review.py",
        "_check_future_probe_implementation",
    ]:
        if fragment not in guard_text:
            source_missing.append(fragment)
            failures.append(f"extended guard source missing fragment: {fragment}")

    return {
        "missing_count": len(missing),
        "missing": missing,
        "source_missing_count": len(source_missing),
        "source_missing": source_missing,
    }


def main() -> int:
    failures: List[str] = []
    compile_result = _compile_targets(failures)
    # Do not execute EXTENDED_GUARD_PATH or PRIMARY_GUARD_PATH here after this guard is connected to primary.
    # Both are primary-connected guard chains and nested execution can create recursion/ordering failures.
    # Verify durable checkpoints and primary connection statically instead.
    extended_checkpoint_static = _check_extended_checkpoint_static(failures)
    docs = _check_docs(failures)
    outputs = _check_outputs(failures)
    future_contract_not_opened = _check_future_contract_not_opened(failures)
    forbidden_path_opening = _check_forbidden_path_opening(failures)
    primary_connection_static = _check_primary_connection_static(failures)
    summary = {
        "phase": "phase4a_real_data_validation_evidence_connection_entry_criteria_guard",
        "checks": {
            "compile": compile_result,
            "extended_checkpoint_static": extended_checkpoint_static,
            "docs": docs,
            "outputs": outputs,
            "future_contract_not_opened": future_contract_not_opened,
            "forbidden_path_opening": forbidden_path_opening,
            "primary_connection_static": primary_connection_static,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
