# path: ./tools/test_phase4a_tmp_docs_current_truth_sync_close_guard.py
# desc: Close guard for tmp/docs current-truth sync before next-thread handoff.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_ROOT = REPO_ROOT / "tmp" / "docs" / "architecture"

SELF_PATH = "tools/test_phase4a_tmp_docs_current_truth_sync_close_guard.py"
DOCS_GUARD_PATH = "tools/test_phase4a_tmp_docs_current_truth_sync_guard.py"
ADDENDUM_PATH = DOC_ROOT / "PHASE4A_CURRENT_TRUTH_HOT_COLD_L4_DASHBOARD_DOCS_SYNC_2026-06-07.md"
FINAL_ADDENDUM_PATH = DOC_ROOT / "PHASE4A_DASHBOARD_HUB_DISPLAY_SOURCE_FINAL_BUNDLE_SYNC_2026-06-11.md"
FOCUS_JSON = REPO_ROOT / "tmp" / "gpt_room" / "09_FOCUS.json"
STATE_JSON = REPO_ROOT / "tmp" / "gpt_room" / "11_STATE.json"

REQUIRED_ADDENDUM_FRAGMENTS = [
    "HEAD = 657ca595",
    "primary_total_guard_ok = true",
    "compile.passed_count = 66",
    "next_thread_ready = true",
    "candidate_delete_files = 0",
    "too_new_files = 56",
    "too_new_gb = 126.353368",
    "hot_cold_duplicate_safe_dataset_view_model",
    "catalog_ready_payload_not_opened",
    "payload_loader_status = not_opened",
    "dataset_reader_status = not_opened",
    "dashboard_rendering_status = not_opened",
    "copy_delete_gc_status = not_opened",
    "superseded for execution planning",
    "python.exe\" -m streamlit",
    "L4 = shared-first shape owner",
    "UI is display/orchestration owner, not market meaning owner",
]

FINAL_REQUIRED_ADDENDUM_FRAGMENTS = [
    "HEAD = ac08a855",
    "primary_total_guard_ok = true",
    "compile.passed_count = 94",
    "next_thread_ready = true",
    "dashboard_hub_display_source_manual_smoke_record_close_guard",
    "dashboard_hub_display_source_operator_ui_integration_close_guard",
    "catalog_ready_payload_not_opened",
    "panel_visible = true",
    "details_expander_opened = true",
    "payload loader",
    "dataset reader",
    "inference/training",
    "choose a new guarded workstream",
]

ROOM_REQUIRED_FRAGMENTS = [
    "phase4a_dashboard_hub_display_source_final_bundle_closed_next_thread_ready",
    "dashboard_hub_display_source_final_bundle_sync_closed_pending_commit",
    "ac08a855",
    "dashboard_hub_display_source_final_bundle_closed",
    "next_thread_start_with_project_bootstrap_and_choose_new_guarded_workstream",
]

FORBIDDEN_ADDENDUM_CLAIMS = [
    "payload_loader_status = opened",
    "dataset_reader_status = opened",
    "dashboard_rendering_status = opened",
    "copy executor opened",
    "delete executor opened",
    "archive GC enabled",
    "candidate_delete_files = 28 is current",
]


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "tmp_docs_current_truth_sync_close"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"{rel_path} did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1600:], "stderr_tail": (proc.stderr or "")[-1600:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {"ok": ok, "returncode": proc.returncode, "phase": parsed.get("phase"), "docs_sync_status": parsed.get("docs_sync_status"), "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}


def _check_addendum(failures: list[str]) -> dict[str, Any]:
    if not ADDENDUM_PATH.exists():
        failures.append(f"missing docs current-truth addendum: {ADDENDUM_PATH.relative_to(REPO_ROOT)}")
        return {"missing": ["<file exists>"], "final_missing": [], "forbidden_hits": []}
    if not FINAL_ADDENDUM_PATH.exists():
        failures.append(f"missing final docs current-truth addendum: {FINAL_ADDENDUM_PATH.relative_to(REPO_ROOT)}")
        return {"missing": [], "final_missing": ["<file exists>"], "forbidden_hits": []}

    text = ADDENDUM_PATH.read_text(encoding="utf-8")
    final_text = FINAL_ADDENDUM_PATH.read_text(encoding="utf-8")
    missing = [fragment for fragment in REQUIRED_ADDENDUM_FRAGMENTS if fragment not in text]
    final_missing = [fragment for fragment in FINAL_REQUIRED_ADDENDUM_FRAGMENTS if fragment not in final_text]
    forbidden_hits = [token for token in FORBIDDEN_ADDENDUM_CLAIMS if token in text or token in final_text]
    for fragment in missing:
        failures.append(f"docs current-truth close addendum missing fragment: {fragment}")
    for fragment in final_missing:
        failures.append(f"final docs current-truth close addendum missing fragment: {fragment}")
    for token in forbidden_hits:
        failures.append(f"docs current-truth close addendum contains forbidden stale claim: {token}")

    room_missing: list[str] = []
    for path in [FOCUS_JSON, STATE_JSON]:
        if not path.exists():
            room_missing.append(f"{path.relative_to(REPO_ROOT)}::<file exists>")
            continue
        room_text = path.read_text(encoding="utf-8")
        for fragment in ROOM_REQUIRED_FRAGMENTS:
            if fragment not in room_text:
                room_missing.append(f"{path.relative_to(REPO_ROOT)}::{fragment}")
    for item in room_missing:
        failures.append(f"room final sync missing fragment: {item}")
    return {"missing": missing, "final_missing": final_missing, "room_missing": room_missing, "forbidden_hits": forbidden_hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_docs_guard": _compile(DOCS_GUARD_PATH, failures),
        "docs_guard": _run_json_guard(DOCS_GUARD_PATH, failures),
        "addendum_shape": _check_addendum(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_tmp_docs_current_truth_sync_close_guard",
        "close_status": "closed" if not failures else "open",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
