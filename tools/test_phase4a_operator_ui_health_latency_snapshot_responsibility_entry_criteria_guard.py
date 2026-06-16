# path: ./tools/test_phase4a_operator_ui_health_latency_snapshot_responsibility_entry_criteria_guard.py
# desc: Phase 4-A Operator UI Health latency snapshot responsibility separation entry criteria guard.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operator_ui_health_latency_snapshot_responsibility_entry_criteria_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATOR_UI_HEALTH_LATENCY_SNAPSHOT_RESPONSIBILITY_SEPARATION_ENTRY_CRITERIA_2026-06-03.md"
HEALTH_SERVICE_PATH = "btcts_next/src/btcts/apps/operator_ui/health_data_service.py"
HEALTH_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/health_page.py"
COLLECTOR_STATE_SERVICE_PATH = "btcts_next/src/btcts/apps/operator_ui/collector_state_service.py"
AUDIT_MODEL_PATH = "btcts_next/src/btcts/apps/operator_ui/health_audit_read_model.py"
FOCUS_PATH = "tmp/gpt_room/09_FOCUS.json"
LOCAL_TRUTH_NOTE_PATH = "tmp/gpt_room/memory/notes/2026-06-03_local_truth_reconciliation_and_next_task_alignment.md"

REQUIRED_SPEC_FRAGMENTS = [
    "Operator UI Health latency snapshot responsibility separation entry criteria",
    "entry criteria / guard-only",
    "BTC / bitFlyer only",
    "_hot_remaining_data_files(...) returns [] by default",
    "BTCTS_OPERATOR_UI_SCAN_HOT_REMAINING=1 is required to opt in",
    "_audit_max_lines_for_range(\"1h\") = 50000",
    "_audit_max_lines_for_range(\"24h\") = 120000",
    "_audit_max_lines_for_range(\"1w\") = 240000",
    "load_health_snapshot(...) composes current_state_bundle, timeline_bundle, continuity_bundle, anomaly_bundle, page_meta_bundle together",
    "apps/operator_ui/views/          = Streamlit rendering only",
    "apps/operator_ui/components/     = UI components / presenters only",
    "apps/operator_ui/*_service.py    = application read services / composition boundary",
    "processing/l4_consumer_models/   = wording-free shared read models / contracts",
    "collector_vnext/                 = capture/runtime owner, not UI read-model owner",
    "Do not implement full UI architecture rewrite.",
    "Do not add raw D/E scanner.",
    "Do not reopen Hot/Cold as active focus.",
    SELF_PATH,
]

REQUIRED_HEALTH_SERVICE_FRAGMENTS = [
    "from btcts.apps.operator_ui.health_audit_read_model import (",
    "HealthAuditInput",
    "audit_max_lines_for_range as _audit_max_lines_for_range_impl",
    "build_health_audit_input",
    "def _audit_max_lines_for_range(range_key: str) -> int:",
    "return _audit_max_lines_for_range_impl(range_key)",
    'def load_health_audit_input(*, range_key: str = "1h") -> HealthAuditInput:',
    "audit_input = load_health_audit_input(range_key=range_key)",
    "audit_rows = list(audit_input.rows)",
    "def load_health_snapshot(*, range_key: str = \"1h\") -> dict[str, Any]:",
    "current_state_bundle",
    "timeline_bundle",
    "continuity_bundle",
    "anomaly_bundle",
    "page_meta_bundle",
]

REQUIRED_AUDIT_MODEL_FRAGMENTS = [
    'HEALTH_AUDIT_READ_MODEL_VERSION = "health_audit_read_model.v1"',
    "class HealthAuditInput:",
    "def audit_max_lines_for_range(range_key: str) -> int:",
    "HEALTH_AUDIT_DEFAULT_MAX_LINES",
    "HEALTH_AUDIT_MAX_LINES_BY_RANGE = {",
    '"24h": 36000',
    '"1w": 72000',
    "def build_health_audit_input(",
    "bounded_input_only",
]

REQUIRED_COLLECTOR_SERVICE_FRAGMENTS = [
    "def _hot_remaining_data_files(",
    "BTCTS_OPERATOR_UI_SCAN_HOT_REMAINING",
    "return []",
    "scan_file_budget",
    "scan_dir_budget",
    "operator_ui_opt_in_bounded_sample",
]

FORBIDDEN_HEALTH_PAGE_FRAGMENTS = [
    ".rglob(",
    "os.walk(",
    "glob.glob(",
    "read_jsonl_tail(",
    "open(_audit",
    "archive_gc",
    "place_order",
    "broker_order",
]

FORBIDDEN_ENTRY_IMPLEMENTATION_FILES = [
    "btcts_next/src/btcts/apps/operator_ui/health_snapshot_models.py",
    "btcts_next/src/btcts/apps/operator_ui/health_timeline_read_model.py",
    "btcts_next/src/btcts/apps/operator_ui/health_continuity_read_model.py",
    "btcts_next/src/btcts/apps/operator_ui/health_snapshot_composer.py",
]

FORBIDDEN_FOCUS_ACTIVE_FRAGMENTS = [
    "operational_readiness_hot_cold_retention_explicit_dry_run_plan_entry_next",
    "start_hot_cold_retention_dry_run_plan_entry_only",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "operator_ui_health_latency_snapshot_responsibility_entry"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _check_fragments(rel_path: str, fragments: list[str], failures: list[str], *, label: str) -> dict[str, Any]:
    text = _read(rel_path)
    if not text:
        failures.append(f"missing or empty {label}: {rel_path}")
        return {"missing_file": True, "missing": fragments}
    missing = [fragment for fragment in fragments if fragment not in text]
    for fragment in missing:
        failures.append(f"missing {label} fragment in {rel_path}: {fragment}")
    return {"missing_count": len(missing), "missing": missing}


def _check_collector_scan_default_disabled(failures: list[str]) -> dict[str, Any]:
    text = _read(COLLECTOR_STATE_SERVICE_PATH)
    bad: list[str] = []
    if "rglob(" in text:
        bad.append("collector_state_service must not use rglob for hot remaining files")
    if "BTCTS_OPERATOR_UI_SCAN_HOT_REMAINING" not in text:
        bad.append("collector hot sample must remain explicit opt-in")
    if "return []" not in text:
        bad.append("collector hot sample must return [] by default")
    if "scan_file_budget" not in text or "scan_dir_budget" not in text:
        bad.append("collector hot sample must remain bounded when opt-in")
    for item in bad:
        failures.append(item)
    return {"ok": not bad, "bad": bad}


def _check_health_page_is_render_only_for_entry(failures: list[str]) -> dict[str, Any]:
    text = _read(HEALTH_PAGE_PATH)
    hits = [fragment for fragment in FORBIDDEN_HEALTH_PAGE_FRAGMENTS if fragment in text]
    for fragment in hits:
        failures.append(f"Health page must remain render/presenter only for this entry: {fragment}")
    return {"hit_count": len(hits), "hits": hits}


def _check_entry_does_not_implement_future_files(failures: list[str]) -> dict[str, Any]:
    hits = [rel for rel in FORBIDDEN_ENTRY_IMPLEMENTATION_FILES if (REPO_ROOT / rel).exists()]
    for rel in hits:
        failures.append(f"entry slice must not add implementation file yet: {rel}")
    return {"hit_count": len(hits), "hits": hits}


def _check_focus_alignment(failures: list[str]) -> dict[str, Any]:
    focus = _read(FOCUS_PATH)
    note = _read(LOCAL_TRUTH_NOTE_PATH)
    combined = focus + "\n" + note
    bad: list[str] = []
    if "phase4a_operator_ui_health_latency_snapshot_responsibility_separation_entry_criteria" not in focus:
        bad.append("FOCUS current task must point to Health latency snapshot responsibility entry")
    for fragment in FORBIDDEN_FOCUS_ACTIVE_FRAGMENTS:
        if fragment in focus:
            bad.append(f"FOCUS still carries stale active Hot/Cold fragment: {fragment}")

    collector_correction_markers = [
        "collector_render_time_hot_data_scan",
        "Collector page hot-data sampling is already corrected",
        "_hot_remaining_data_files(...) returns [] by default",
        "BTCTS_OPERATOR_UI_SCAN_HOT_REMAINING=1",
    ]
    health_latency_markers = [
        "remaining_latency_focus",
        "Remaining local latency concern",
        "Health audit tail / snapshot composition responsibility separation",
        "The remaining Health-side concern is in",
    ]
    if not any(marker in combined for marker in collector_correction_markers):
        bad.append("local truth reconciliation note/focus missing collector correction")
    if not any(marker in combined for marker in health_latency_markers):
        bad.append("local truth reconciliation note/focus missing remaining Health latency focus")
    for item in bad:
        failures.append(item)
    return {"ok": not bad, "bad": bad}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_health_service": _compile(HEALTH_SERVICE_PATH, failures),
        "compile_health_page": _compile(HEALTH_PAGE_PATH, failures),
        "compile_collector_state_service": _compile(COLLECTOR_STATE_SERVICE_PATH, failures),
        "compile_audit_model": _compile(AUDIT_MODEL_PATH, failures),
        "spec": _check_fragments(SPEC_PATH, REQUIRED_SPEC_FRAGMENTS, failures, label="spec"),
        "health_service_current_facts": _check_fragments(HEALTH_SERVICE_PATH, REQUIRED_HEALTH_SERVICE_FRAGMENTS, failures, label="health service"),
        "audit_model_current_facts": _check_fragments(AUDIT_MODEL_PATH, REQUIRED_AUDIT_MODEL_FRAGMENTS, failures, label="audit model"),
        "collector_service_current_facts": _check_fragments(COLLECTOR_STATE_SERVICE_PATH, REQUIRED_COLLECTOR_SERVICE_FRAGMENTS, failures, label="collector service"),
        "collector_scan_default_disabled": _check_collector_scan_default_disabled(failures),
        "health_page_render_only_for_entry": _check_health_page_is_render_only_for_entry(failures),
        "entry_does_not_implement_future_files": _check_entry_does_not_implement_future_files(failures),
        "focus_alignment": _check_focus_alignment(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operator_ui_health_latency_snapshot_responsibility_separation_entry_criteria_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
