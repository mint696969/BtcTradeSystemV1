# path: ./tools/test_phase4a_health_warroom_read_only_evidence_consumption_entry_criteria_guard.py
# desc: Phase 4-A Health / WarRoom read-only evidence consumption entry criteria guard.

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

DOC_PATH = "tmp/docs/architecture/PHASE4A_HEALTH_WARROOM_READ_ONLY_EVIDENCE_CONSUMPTION_ENTRY_CRITERIA_2026-05-29.md"
EVIDENCE_DOC_PATH = "tmp/docs/architecture/PHASE4A_REAL_DATA_VALIDATION_EVIDENCE_CONNECTION_ENTRY_CRITERIA_2026-05-26.md"
OP_READINESS_DOC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_ARCHIVE_RETENTION_AND_UI_LATENCY_CLOSE_2026-05-29.md"
HEALTH_DIGEST_SPEC_PATH = "tmp/docs/architecture/08_HEALTH_DIGEST_SHARED_ADAPTER_WIDGET_SPEC_2026-04-15_MERGED.md"
PHASE_DE_CLOSE_PATH = "tmp/docs/architecture/PHASE4A_PHASE_D_E_HEALTH_WARROOM_OPERATIONAL_READING_CLOSE_2026-05-17.md"
INDEX_PATH = "tmp/docs/_INDEX.md"
STATE_PATH = "tmp/gpt_room/11_STATE.json"

EVIDENCE_CONTRACT_PATH = "btcts_next/src/btcts/processing/l4_consumer_models/shared/real_data_validation_evidence.py"
EVIDENCE_CONTRACT_TEST_PATH = "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_real_data_validation_evidence.py"
CONSUMER_SKELETON_PATH = "btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/real_data_validation_evidence_consumption.py"
CONSUMER_SKELETON_TEST_PATH = "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_real_data_validation_evidence_consumption.py"

FORBIDDEN_IMPLEMENTATION_PATHS = [
    "btcts_next/src/btcts/apps/operator_ui",
    "btcts_next/src/btcts/market_engine",
    "btcts_next/src/btcts/collector",
    "btcts_next/src/btcts/collector_vnext",
    "btcts_next/src/btcts/execution",
    "btcts_next/src/btcts/broker",
]

COMPILE_TARGETS = [
    EVIDENCE_CONTRACT_PATH,
    EVIDENCE_CONTRACT_TEST_PATH,
    CONSUMER_SKELETON_PATH,
    CONSUMER_SKELETON_TEST_PATH,
]


def _read_text(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _compile_targets(failures: List[str]) -> Dict[str, Any]:
    passed: list[str] = []
    failed: list[dict[str, str]] = []
    cache_root = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "health_warroom_evidence_consumption_entry"
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


def _probe_evidence_contract(failures: List[str]) -> Dict[str, Any]:
    try:
        from btcts.processing.l4_consumer_models.shared.real_data_validation_evidence import (
            RealDataValidationEvidenceSummary,
            build_real_data_validation_evidence_summary,
            real_data_validation_evidence_summary_to_snapshot,
        )
    except Exception as exc:
        failures.append(f"evidence contract import failed: {type(exc).__name__}: {exc}")
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    try:
        summary = build_real_data_validation_evidence_summary(
            source_output_ref="tmp/work/phase4a_extended_real_data_validation_review/probe_phase4a_extended_real_data_validation_review.out.json",
            review_output_ref="tmp/work/phase4a_extended_real_data_validation_review_entry/review_extended_real_data_validation_review_output_v1.out.json",
            evidence_trace_refs=("extended:36rows",),
        )
        snapshot = real_data_validation_evidence_summary_to_snapshot(summary)
    except Exception as exc:
        failures.append(f"evidence contract probe failed: {type(exc).__name__}: {exc}")
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    checks = {
        "is_dataclass_summary": isinstance(summary, RealDataValidationEvidenceSummary),
        "evidence_type": summary.evidence_type == "real_data_validation_evidence_summary",
        "evidence_version": summary.evidence_version == "phase4a.real_data_validation_evidence.v1",
        "source_kind": summary.source_kind == "extended_real_data_validation_review_output",
        "exchange": summary.exchange == "bitflyer",
        "symbol": summary.symbol == "BTC_JPY",
        "channel_count": summary.channel_count == 4,
        "replay_row_count": summary.replay_row_count == 36,
        "board_row_count": summary.board_row_count == 18,
        "trade_row_count": summary.trade_row_count == 18,
        "monotonic_check_count": summary.monotonic_check_count == 7,
        "diagnostic_note_count": summary.diagnostic_note_count == 0,
        "snapshot_read_only": snapshot.get("read_only_contract") is True,
        "snapshot_diagnostic_only": snapshot.get("diagnostic_evidence_only") is True,
        "snapshot_not_runtime_signal": snapshot.get("not_runtime_signal") is True,
        "snapshot_not_runtime_wiring": snapshot.get("not_runtime_wiring") is True,
        "snapshot_not_ui_rendering": snapshot.get("not_ui_rendering") is True,
        "snapshot_not_market_engine_input": snapshot.get("not_market_engine_input") is True,
        "snapshot_not_collector_writer": snapshot.get("not_collector_writer") is True,
        "snapshot_not_broker_or_order": snapshot.get("not_broker_or_order_automation") is True,
        "snapshot_not_inference_or_training": snapshot.get("not_inference_or_training") is True,
    }
    bad = [name for name, ok in checks.items() if not ok]
    for name in bad:
        failures.append(f"evidence contract probe check failed: {name}")

    forbidden_keys = [
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
    forbidden_present = [key for key in forbidden_keys if key in snapshot]
    for key in forbidden_present:
        failures.append(f"evidence snapshot contains forbidden key: {key}")

    return {
        "ok": not bad and not forbidden_present,
        "checks": checks,
        "bad": bad,
        "forbidden_present": forbidden_present,
        "snapshot_key_count": len(snapshot),
    }



def _run_plain_ok(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"plain-ok test missing: {rel_path}")
        return {"returncode": None, "ok": False, "stdout_tail": "", "stderr_tail": ""}
    proc = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=120,
    )
    ok = proc.returncode == 0 and (proc.stdout or "").strip() == "ok"
    if not ok:
        failures.append(f"{rel_path} must emit plain 'ok'")
    return {
        "returncode": proc.returncode,
        "ok": bool(ok),
        "stdout_tail": (proc.stdout or "")[-2000:],
        "stderr_tail": (proc.stderr or "")[-2000:],
    }

def _check_docs(failures: List[str]) -> Dict[str, Any]:
    required = {
        DOC_PATH: [
            "Health / WarRoom read-only evidence consumption entry criteria",
            "This entry does not open Health UI rendering yet.",
            "This entry does not open WarRoom UI rendering yet.",
            "Health / WarRoom evidence consumption != runtime signal",
            "Health / WarRoom read-only evidence consumer contract / adapter skeleton only",
            "tools/test_phase4a_health_warroom_read_only_evidence_consumption_entry_criteria_guard.py",
        ],
        EVIDENCE_DOC_PATH: [
            "The read-only evidence summary contract skeleton is saved and primary-guarded.",
            "Any runtime/UI/Health/WarRoom consumption must start from a separate entry criteria/spec and guard.",
            "The evidence contract output shape is stable enough for a future guarded consumer-entry discussion.",
        ],
        OP_READINESS_DOC_PATH: [
            "normal D-hot retention target = 10 days",
            "hard minimum D-hot retention = 7 days",
            "archive_retention_readiness_report_v1",
            "slow_count_ge_1s = 0",
        ],
        HEALTH_DIGEST_SPEC_PATH: [
            "Before opening Health / WarRoom read-only evidence consumption, Operator UI latency was short-term stabilized.",
            "This is a latency/readiness fix only. It does not open Health / WarRoom runtime consumption",
        ],
        PHASE_DE_CLOSE_PATH: [
            "Health / WarRoom consume compact rows rather than owning raw contract meaning.",
            "Health / WarRoom operational reading is operator review only.",
            "Operational reading is not an execution instruction.",
        ],
        INDEX_PATH: [
            "PHASE4A_HEALTH_WARROOM_READ_ONLY_EVIDENCE_CONSUMPTION_ENTRY_CRITERIA_2026-05-29.md",
            "UI rendering / runtime wiring / market_engine / collector writer / broker-order / inference / training は開かない。",
        ],
        STATE_PATH: [
            "health_warroom_read_only_evidence_consumption",
        ],
    }
    missing: list[dict[str, str]] = []
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
    return {"missing_count": len(missing), "missing": missing}



def _check_state_phase(failures: List[str]) -> Dict[str, Any]:
    text = _read_text(STATE_PATH)
    allowed_fragments = [
        "operational_readiness_and_archive_retention_readiness_closed_ready_for_health_warroom_consumption_entry",
        "health_warroom_read_only_evidence_consumption_entry_and_skeleton_closed_ready_for_next_guarded_slice",
    ]
    matched = [fragment for fragment in allowed_fragments if fragment in text]
    if not matched:
        failures.append("state is neither entry-ready nor skeleton-close for Health/WarRoom evidence consumption")
    required_boundary_fragments = [
        "Streamlit rendering",
        "route wiring",
        "runtime state writer",
        "market_engine integration",
        "collector writer/backfill",
        "broker/order/execution",
        "inference/training",
        "raw D/E scanner",
    ]
    missing_boundary = [fragment for fragment in required_boundary_fragments if fragment not in text]
    for fragment in missing_boundary:
        failures.append(f"state missing closed-boundary fragment: {fragment}")
    return {
        "matched": matched,
        "allowed_count": len(allowed_fragments),
        "missing_boundary": missing_boundary,
    }

def _check_evidence_contract_boundary(failures: List[str]) -> Dict[str, Any]:
    text = _read_text(EVIDENCE_CONTRACT_PATH)
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
    missing: list[str] = []
    forbidden_hits: list[str] = []
    for fragment in required:
        if fragment not in text:
            missing.append(fragment)
            failures.append(f"evidence contract missing required boundary fragment: {fragment}")
    for fragment in forbidden:
        if fragment in text:
            forbidden_hits.append(fragment)
            failures.append(f"evidence contract contains forbidden runtime/order field: {fragment}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def _check_no_premature_consumption_implementation(failures: List[str]) -> Dict[str, Any]:
    hits: list[str] = []
    patterns = ["real_data_validation_evidence", "RealDataValidationEvidence", "evidence_consumption"]
    allowed = {
        EVIDENCE_CONTRACT_PATH,
        EVIDENCE_CONTRACT_TEST_PATH,
        CONSUMER_SKELETON_PATH,
        CONSUMER_SKELETON_TEST_PATH,
    }
    for rel_root in FORBIDDEN_IMPLEMENTATION_PATHS:
        root = REPO_ROOT / rel_root
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            rel_path = path.relative_to(REPO_ROOT).as_posix()
            if rel_path in allowed:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue
            if any(pattern in text for pattern in patterns):
                hits.append(rel_path)
                failures.append(f"premature Health/WarRoom/runtime evidence consumption implementation found: {rel_path}")
    return {"hit_count": len(hits), "hits": hits}


def _check_index_ordering(failures: List[str]) -> Dict[str, Any]:
    text = _read_text(INDEX_PATH)
    entry = "PHASE4A_HEALTH_WARROOM_READ_ONLY_EVIDENCE_CONSUMPTION_ENTRY_CRITERIA_2026-05-29.md"
    evidence = "PHASE4A_REAL_DATA_VALIDATION_EVIDENCE_CONNECTION_ENTRY_CRITERIA_2026-05-26.md"
    entry_pos = text.find(entry)
    evidence_pos = text.find(evidence)
    ok = entry_pos >= 0 and evidence_pos >= 0 and entry_pos > evidence_pos
    # This entry follows evidence contract close; it does not need to be first historical current spec.
    if entry_pos < 0:
        failures.append("Health/WarRoom evidence consumption entry spec missing from docs/_INDEX.md")
    return {"entry_pos": entry_pos, "evidence_pos": evidence_pos, "after_evidence_anchor": bool(ok)}


def main() -> int:
    failures: List[str] = []
    compile_result = _compile_targets(failures)
    evidence_contract_probe = _probe_evidence_contract(failures)
    consumer_skeleton_test = _run_plain_ok(CONSUMER_SKELETON_TEST_PATH, failures)
    docs = _check_docs(failures)
    state_phase = _check_state_phase(failures)
    evidence_contract_boundary = _check_evidence_contract_boundary(failures)
    premature_consumption = _check_no_premature_consumption_implementation(failures)
    index_ordering = _check_index_ordering(failures)
    summary = {
        "phase": "phase4a_health_warroom_read_only_evidence_consumption_entry_criteria_guard",
        "checks": {
            "compile": compile_result,
            "evidence_contract_probe": evidence_contract_probe,
            "consumer_skeleton_test": consumer_skeleton_test,
            "docs": docs,
            "state_phase": state_phase,
            "evidence_contract_boundary": evidence_contract_boundary,
            "premature_consumption": premature_consumption,
            "index_ordering": index_ordering,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
