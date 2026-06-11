# path: ./tools/test_phase4a_tmp_docs_current_truth_sync_guard.py
# desc: Guard tmp/docs current-truth sync for Hot/Cold, L4, and dashboard hub before next-thread handoff.

from __future__ import annotations

import json
import py_compile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_ROOT = REPO_ROOT / "tmp" / "docs" / "architecture"
SELF_PATH = "tools/test_phase4a_tmp_docs_current_truth_sync_guard.py"

ADDENDUM = DOC_ROOT / "PHASE4A_CURRENT_TRUTH_HOT_COLD_L4_DASHBOARD_DOCS_SYNC_2026-06-07.md"
FINAL_ADDENDUM = DOC_ROOT / "PHASE4A_DASHBOARD_HUB_DISPLAY_SOURCE_FINAL_BUNDLE_SYNC_2026-06-11.md"
SMALL_BATCH = DOC_ROOT / "PHASE4A_OPERATIONAL_READINESS_HOT_COLD_SMALL_BATCH_GUARDED_DELETE_ENTRY_CRITERIA_2026-06-01.md"
SAFETY_CLOSE = DOC_ROOT / "PHASE4A_OPERATIONAL_READINESS_HOT_COLD_SAFETY_THREAD_CLOSE_2026-06-02.md"
DUP_ENTRY = DOC_ROOT / "PHASE4A_OPERATIONAL_READINESS_HOT_COLD_DUPLICATE_SAFE_DATASET_VIEW_ENTRY_2026-06-02.md"
L4_SPEC = DOC_ROOT / "03_L4_SHARED_CONSUMER_MODELS_SPEC_2026-04-09.md"
UI_SPEC = DOC_ROOT / "04_UI_HUB_OPERATOR_UI_SPEC_2026-04-09.md"
DE_DASHBOARD = DOC_ROOT / "PHASE4A_DE_ARCHIVE_TRANSFER_HEALTH_DASHBOARD_ENTRY_CRITERIA_2026-05-31.md"
FOCUS_JSON = REPO_ROOT / "tmp" / "gpt_room" / "09_FOCUS.json"
STATE_JSON = REPO_ROOT / "tmp" / "gpt_room" / "11_STATE.json"

REQUIRED_BY_FILE = {
    FINAL_ADDENDUM: [
        "HEAD = ac08a855",
        "primary_total_guard_ok = true",
        "compile.passed_count = 94",
        "next_thread_ready = true",
        "dashboard_hub_display_source_manual_smoke_record_close_guard",
        "dashboard_hub_display_source_health_page_insertion_close_guard",
        "dashboard_hub_display_source_operator_ui_integration_close_guard",
        "catalog_ready_payload_not_opened",
        "panel_visible = true",
        "details_expander_opened = true",
        "payload loader",
        "dataset reader",
        "inference/training",
        "UI actual growth",
        "L4 shared bundle expansion",
        "prediction / inference-adjacent read-only entry",
    ],
    ADDENDUM: [
        "HEAD = 657ca595",
        "primary_total_guard_ok = true",
        "compile.passed_count = 66",
        "candidate_delete_files = 0",
        "too_new_files = 56",
        "too_new_gb = 126.353368",
        "hot_cold_duplicate_safe_dataset_view_model",
        "catalog_ready_payload_not_opened",
        "payload_loader_status = not_opened",
        "dataset_reader_status = not_opened",
        "dashboard_rendering_status = not_opened",
        "PHASE4A_OPERATIONAL_READINESS_HOT_COLD_SMALL_BATCH_GUARDED_DELETE_ENTRY_CRITERIA_2026-06-01.md",
        "superseded for execution planning",
        "python.exe\" -m streamlit",
        "L4 = shared-first shape owner",
        "UI is display/orchestration owner, not market meaning owner",
        "next_thread_ready = true",
    ],
    SMALL_BATCH: [
        "CURRENT-TRUTH OVERRIDE",
        "superseded for execution planning",
        "candidate_delete_files = 0",
        "10-day policy",
        "plan_hash = e5bf5d3c6630c10084fc44c97614dc48c3bc4e8147e98683831eefa2923f9eb6",
    ],
    SAFETY_CLOSE: [
        "CURRENT-TRUTH ADDENDUM",
        "657ca595",
        "hot_cold_duplicate_safe_dataset_view_model",
        "catalog_ready_payload_not_opened",
    ],
    DUP_ENTRY: [
        "CURRENT-TRUTH ADDENDUM",
        "metadata-only model skeleton",
        "HotColdLogicalDatasetViewRow",
        "payload loader / reader remains unopened",
    ],
    L4_SPEC: [
        "CURRENT-TRUTH ADDENDUM",
        "657ca595",
        "dashboard display source/status line",
        "metadata-only and read-only",
    ],
    UI_SPEC: [
        "CURRENT-TRUTH ADDENDUM",
        "dashboard hub source foundation",
        "hot_cold_duplicate_safe_dataset_view_model",
        "python.exe\" -m streamlit",
    ],
    DE_DASHBOARD: [
        "CURRENT-TRUTH ADDENDUM",
        "separate older dashboard entry",
        "not the current dashboard hub source/status path",
    ],
}

ROOM_REQUIRED_BY_FILE = {
    FOCUS_JSON: [
        "phase4a_dashboard_hub_display_source_final_bundle_closed_next_thread_ready",
        "dashboard_hub_display_source_final_bundle_sync_closed_pending_commit",
        "ac08a855",
        "dashboard_hub_display_source_final_bundle_closed",
        "next_thread_start_with_project_bootstrap_and_choose_new_guarded_workstream",
    ],
    STATE_JSON: [
        "phase4a_dashboard_hub_display_source_final_bundle_closed_next_thread_ready",
        "dashboard_hub_display_source_final_bundle_sync_closed_pending_commit",
        "ac08a855",
        "dashboard_hub_display_source_final_bundle_closed",
        "next_thread_start_with_project_bootstrap_and_choose_new_guarded_workstream",
    ],
}

FORBIDDEN_ADDENDUM_CLAIMS = [
    "payload_loader_status = opened",
    "dataset_reader_status = opened",
    "dashboard_rendering_status = opened",
    "copy executor opened",
    "delete executor opened",
    "archive GC enabled",
    "candidate_delete_files = 28 is current",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile_self(failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / SELF_PATH
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "tmp_docs_current_truth_sync"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / "self.pyc"), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {SELF_PATH}: {exc}")
        return {"ok": False, "error": str(exc)}


def _check_required(failures: list[str]) -> dict[str, Any]:
    missing: list[dict[str, str]] = []
    for path, fragments in REQUIRED_BY_FILE.items():
        text = _read(path)
        if not path.exists():
            missing.append({"path": str(path.relative_to(REPO_ROOT)), "fragment": "<file exists>"})
            continue
        for fragment in fragments:
            if fragment not in text:
                missing.append({"path": str(path.relative_to(REPO_ROOT)), "fragment": fragment})
    for path, fragments in ROOM_REQUIRED_BY_FILE.items():
        text = _read(path)
        if not path.exists():
            missing.append({"path": str(path.relative_to(REPO_ROOT)), "fragment": "<file exists>"})
            continue
        for fragment in fragments:
            if fragment not in text:
                missing.append({"path": str(path.relative_to(REPO_ROOT)), "fragment": fragment})
    for item in missing:
        failures.append(f"docs/room current-truth sync missing fragment: {item['path']}::{item['fragment']}")
    return {"missing": missing}


def _check_forbidden(failures: list[str]) -> dict[str, Any]:
    text = _read(ADDENDUM)
    hits = [token for token in FORBIDDEN_ADDENDUM_CLAIMS if token in text]
    for token in hits:
        failures.append(f"docs current-truth addendum contains forbidden stale claim: {token}")
    return {"hits": hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile_self(failures),
        "required_fragments": _check_required(failures),
        "forbidden_addendum_claims": _check_forbidden(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_tmp_docs_current_truth_sync_guard",
        "docs_sync_status": "current_truth_addendum_ready" if not failures else "open",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
