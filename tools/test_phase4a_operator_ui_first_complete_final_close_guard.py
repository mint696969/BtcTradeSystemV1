# path: ./tools/test_phase4a_operator_ui_first_complete_final_close_guard.py
# desc: Final close guard for Operator UI first-complete workstream after manual Streamlit smoke.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SELF_PATH = "tools/test_phase4a_operator_ui_first_complete_final_close_guard.py"

PREREQ_GUARDS = [
    "tools/test_phase4a_operator_ui_polish_roadmap_guard.py",
    "tools/test_phase4a_operator_ui_health_widget_readability_guard.py",
    "tools/test_phase4a_operator_ui_health_language_presentation_guard.py",
    "tools/test_phase4a_operator_ui_collector_widget_structure_guard.py",
    "tools/test_phase4a_operator_ui_warroom_widget_structure_guard.py",
    "tools/test_phase4a_operator_ui_other_tabs_widget_consistency_guard.py",
    "tools/test_phase4a_operator_ui_dashboard_hub_alerts_navigation_guard.py",
    "tools/test_phase4a_operator_ui_first_complete_close_guard.py",
    "tools/test_phase4a_operator_ui_manual_smoke_readability_fix_guard.py",
]

UI_FILES = [
    "btcts_next/src/btcts/apps/operator_ui/app.py",
    "btcts_next/src/btcts/apps/operator_ui/components/live_shell.py",
    "btcts_next/src/btcts/apps/operator_ui/components/dashboard_hub_source_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/components/evidence_presentation_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/components/health_detail_panels.py",
    "btcts_next/src/btcts/apps/operator_ui/components/health_top_panels.py",
    "btcts_next/src/btcts/apps/operator_ui/components/warroom_header.py",
    "btcts_next/src/btcts/apps/operator_ui/texts/common.py",
    "btcts_next/src/btcts/apps/operator_ui/texts/health.py",
    "btcts_next/src/btcts/apps/operator_ui/views/collector_page.py",
    "btcts_next/src/btcts/apps/operator_ui/views/config_page.py",
    "btcts_next/src/btcts/apps/operator_ui/views/logs_page.py",
    "btcts_next/src/btcts/apps/operator_ui/views/replay_page.py",
    "btcts_next/src/btcts/apps/operator_ui/views/research_page.py",
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
]

ROOM_RECORDS = [
    "tmp/gpt_room/memory/roadmaps/2026-06-11_operator_ui_polish_to_prediction_entry_roadmap.md",
    "tmp/gpt_room/memory/roadmaps/2026-06-11_operator_ui_polish_phase_design.md",
    "tmp/gpt_room/memory/worklog/2026-06-11_operator_ui_polish_cp0_cp1_guard_green.md",
    "tmp/gpt_room/memory/worklog/2026-06-11_operator_ui_polish_cp2_guard_green.md",
    "tmp/gpt_room/memory/worklog/2026-06-11_operator_ui_polish_cp3_guard_green.md",
    "tmp/gpt_room/memory/worklog/2026-06-11_operator_ui_polish_cp4_cp5_guard_green.md",
    "tmp/gpt_room/memory/worklog/2026-06-11_operator_ui_polish_cp6_guard_green.md",
    "tmp/gpt_room/memory/worklog/2026-06-11_operator_ui_polish_cp7_static_close_ready.md",
    "tmp/gpt_room/memory/worklog/2026-06-11_operator_ui_manual_smoke_readability_fix.md",
    "tmp/gpt_room/memory/worklog/2026-06-11_operator_ui_manual_smoke_readability_fix_green.md",
    "tmp/gpt_room/memory/worklog/2026-06-11_operator_ui_manual_smoke_readability_label_color_fix.md",
    "tmp/gpt_room/memory/smoke/2026-06-11_operator_ui_polish_manual_streamlit_smoke.md",
    "tmp/gpt_room/memory/handoffs/2026-06-11_operator_ui_first_complete_static_close_readiness_handoff.md",
    "tmp/gpt_room/memory/handoffs/2026-06-11_operator_ui_first_complete_final_close_handoff.md",
    "tmp/gpt_room/memory/worklog/2026-06-11_operator_ui_first_complete_final_close.md",
    "tmp/gpt_room/08_STATUS.md",
]

COMPILE_TARGETS = [SELF_PATH, *PREREQ_GUARDS, *UI_FILES]

EXPECTED_FINAL_RECORD_FRAGMENTS = {
    "tmp/gpt_room/memory/smoke/2026-06-11_operator_ui_polish_manual_streamlit_smoke.md": [
        "manual_streamlit_smoke = passed_by_operator",
        "visual_ui_first_complete_claim_allowed = true",
        "Health:",
        "Collector:",
        "WarRoom:",
        "Other tabs:",
        "Dashboard hub:",
    ],
    "tmp/gpt_room/memory/handoffs/2026-06-11_operator_ui_first_complete_final_close_handoff.md": [
        "Operator UI first-complete final close handoff",
        "UI first-complete workstream is closed",
        "manual_streamlit_smoke = passed_by_operator",
        "Next recommended workstream",
        "prediction / inference entry remains separate",
        "closed boundaries remain closed",
    ],
    "tmp/gpt_room/memory/worklog/2026-06-11_operator_ui_first_complete_final_close.md": [
        "Operator UI first-complete final close",
        "CP-0..CP-7 static guards green",
        "manual Streamlit smoke passed",
        "manual readability issue fixed",
        "final close guard prepared",
    ],
    "tmp/gpt_room/08_STATUS.md": [
        "Operator UI polish manual Streamlit smoke passed",
        "Operator UI first-complete final close prepared",
        "manual_streamlit_smoke = passed_by_operator",
        "UI first-complete workstream is ready to close",
    ],
}

FORBIDDEN_PATTERNS = [
    "from btcts.broker",
    "btcts.broker",
    "broker_order",
    "place_order",
    "submit_order",
    "execute_order",
    "run_training",
    "training_job",
    "fit_model",
    "start_inference_runtime",
    "run_inference_runtime",
    "payload_loader",
    "dataset_reader",
    "copy_executor",
    "delete_executor",
    "archive_gc_enable",
]


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "operator_ui_first_complete_final_close"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_guard(rel_path: str) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / rel_path)],
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
    )
    parsed: dict[str, Any] | None = None
    try:
        parsed = json.loads(proc.stdout)
    except Exception:
        parsed = None
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "parsed_ok": None if parsed is None else parsed.get("ok"),
        "parsed_status": None if parsed is None else parsed.get("status"),
        "stderr_tail": proc.stderr[-600:],
    }


def _check_prereq_guards(failures: list[str]) -> dict[str, Any]:
    results = {rel_path: _run_guard(rel_path) for rel_path in PREREQ_GUARDS}
    for rel_path, result in results.items():
        if not result.get("ok"):
            failures.append(f"final close prerequisite guard failed: {rel_path}")
        if result.get("parsed_ok") is not True:
            failures.append(f"final close prerequisite guard did not report ok true: {rel_path}")
        status = result.get("parsed_status")
        if rel_path.endswith("first_complete_close_guard.py"):
            if status != "static_close_ready":
                failures.append(f"CP-7 close-readiness status mismatch: {rel_path}: {status}")
        elif rel_path.endswith("manual_smoke_readability_fix_guard.py"):
            if status != "fixed_static_ready_for_resmoke":
                failures.append(f"readability fix status mismatch: {rel_path}: {status}")
        elif status != "closed":
            failures.append(f"final close prerequisite guard did not report closed: {rel_path}: {status}")
    return results


def _check_files_exist(paths: list[str], failures: list[str], label: str) -> dict[str, Any]:
    missing = [rel_path for rel_path in paths if not (REPO_ROOT / rel_path).exists()]
    for rel_path in missing:
        failures.append(f"final close missing {label}: {rel_path}")
    return {"missing": missing}


def _check_record_fragments(failures: list[str]) -> dict[str, Any]:
    missing: list[dict[str, str]] = []
    for rel_path, fragments in EXPECTED_FINAL_RECORD_FRAGMENTS.items():
        text = _read(rel_path)
        for fragment in fragments:
            if fragment not in text:
                missing.append({"path": rel_path, "fragment": fragment})
                failures.append(f"final close record missing fragment: {rel_path}::{fragment}")
    return {"missing": missing}


def _check_forbidden_boundaries(failures: list[str]) -> dict[str, Any]:
    joined = "\n".join(_read(path) for path in UI_FILES)
    hits = [pattern for pattern in FORBIDDEN_PATTERNS if pattern in joined]
    for pattern in hits:
        failures.append(f"final close found forbidden opened boundary: {pattern}")
    return {"hits": hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_targets": {rel: _compile(rel, failures) for rel in COMPILE_TARGETS},
        "prerequisite_guards": _check_prereq_guards(failures),
        "ui_files_exist": _check_files_exist(UI_FILES, failures, "ui file"),
        "room_records_exist": _check_files_exist(ROOM_RECORDS, failures, "room record"),
        "final_record_fragments": _check_record_fragments(failures),
        "forbidden_boundaries": _check_forbidden_boundaries(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operator_ui_first_complete_final_close",
        "status": "closed" if not failures else "open",
        "close_contract": {
            "ui_first_complete_workstream_closed": not failures,
            "manual_streamlit_smoke_recorded": True,
            "visual_ui_first_complete_claim_allowed": not failures,
            "prediction_inference_entry_opened": False,
            "next_recommended_workstream": "prediction/inference entry criteria and guarded roadmap",
        },
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
