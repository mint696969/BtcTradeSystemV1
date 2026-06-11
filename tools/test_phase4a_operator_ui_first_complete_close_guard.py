# path: ./tools/test_phase4a_operator_ui_first_complete_close_guard.py
# desc: CP-7 static close-readiness guard for Operator UI first-complete workstream.

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
SELF_PATH = "tools/test_phase4a_operator_ui_first_complete_close_guard.py"

CP_GUARDS = [
    "tools/test_phase4a_operator_ui_polish_roadmap_guard.py",
    "tools/test_phase4a_operator_ui_health_widget_readability_guard.py",
    "tools/test_phase4a_operator_ui_health_language_presentation_guard.py",
    "tools/test_phase4a_operator_ui_collector_widget_structure_guard.py",
    "tools/test_phase4a_operator_ui_warroom_widget_structure_guard.py",
    "tools/test_phase4a_operator_ui_other_tabs_widget_consistency_guard.py",
    "tools/test_phase4a_operator_ui_dashboard_hub_alerts_navigation_guard.py",
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
    "tmp/gpt_room/memory/handoffs/2026-06-11_operator_ui_first_complete_static_close_readiness_handoff.md",
    "tmp/gpt_room/08_STATUS.md",
]

COMPILE_TARGETS = [SELF_PATH, *CP_GUARDS, *UI_FILES]

REQUIRED_UI_FRAGMENTS = {
    "btcts_next/src/btcts/apps/operator_ui/components/live_shell.py": [
        "def render_scrollable_text_block(",
        "def render_scrollable_key_value_rows(",
        "presentation-only helper",
    ],
    "btcts_next/src/btcts/apps/operator_ui/app.py": [
        "def render_dashboard_hub_status_strip(",
        "display-only dashboard hub status strip",
        "page_defs = [",
        "selection = st.sidebar.radio(",
        "page_module.render()",
    ],
    "btcts_next/src/btcts/apps/operator_ui/views/collector_page.py": [
        "def _render_scrollable_json_block(",
        "presentation-only scrollable JSON",
    ],
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py": [
        "def _render_warroom_scrollable_json_block(",
        "def _render_warroom_reading_caption(",
        "current_tactic_prediction_reading",
    ],
    "btcts_next/src/btcts/apps/operator_ui/views/replay_page.py": [
        "def _render_replay_scrollable_json_block(",
        "def _render_replay_scrollable_text(",
    ],
    "btcts_next/src/btcts/apps/operator_ui/views/research_page.py": [
        "def _render_research_scrollable_text(",
    ],
    "btcts_next/src/btcts/apps/operator_ui/texts/common.py": [
        "dashboard_hub_status_title",
        "dashboard_hub_alert_normal",
    ],
    "btcts_next/src/btcts/apps/operator_ui/texts/health.py": [
        "health_widget_dashboard_source_title",
    ],
}

REQUIRED_ROOM_FRAGMENTS = {
    "tmp/gpt_room/08_STATUS.md": [
        "Operator UI polish CP-6 guard green",
        "CP-7 UI first-complete static close readiness",
        "Manual Streamlit smoke",
        "pending; static guards CP-0..CP-6 only are green",
    ],
    "tmp/gpt_room/memory/handoffs/2026-06-11_operator_ui_first_complete_static_close_readiness_handoff.md": [
        "Operator UI first-complete static close readiness handoff",
        "Static guards CP-0..CP-6 are green",
        "Manual Streamlit smoke is still pending",
        "Do not claim visual UI first-complete until manual smoke is recorded",
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
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "operator_ui_first_complete_close"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_cp_guard(rel_path: str) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / rel_path)],
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=45,
    )
    ok = proc.returncode == 0
    parsed: dict[str, Any] | None = None
    try:
        parsed = json.loads(proc.stdout)
    except Exception:
        parsed = None
    return {
        "ok": ok,
        "returncode": proc.returncode,
        "parsed_ok": None if parsed is None else parsed.get("ok"),
        "parsed_status": None if parsed is None else parsed.get("status"),
        "stderr_tail": proc.stderr[-600:],
    }


def _check_cp_guards(failures: list[str]) -> dict[str, Any]:
    results = {rel_path: _run_cp_guard(rel_path) for rel_path in CP_GUARDS}
    for rel_path, result in results.items():
        if not result.get("ok"):
            failures.append(f"CP-7 close readiness prerequisite guard failed: {rel_path}")
        if result.get("parsed_ok") is not True:
            failures.append(f"CP-7 close readiness prerequisite guard did not report ok true: {rel_path}")
        if result.get("parsed_status") != "closed":
            failures.append(f"CP-7 close readiness prerequisite guard did not report closed: {rel_path}")
    return results


def _check_file_exists(paths: list[str], failures: list[str], label: str) -> dict[str, Any]:
    missing = [rel_path for rel_path in paths if not (REPO_ROOT / rel_path).exists()]
    for rel_path in missing:
        failures.append(f"CP-7 {label} missing file: {rel_path}")
    return {"missing": missing}


def _check_fragments(fragment_map: dict[str, list[str]], failures: list[str], label: str) -> dict[str, Any]:
    missing: list[dict[str, str]] = []
    for rel_path, fragments in fragment_map.items():
        text = _read(rel_path)
        for fragment in fragments:
            if fragment not in text:
                missing.append({"path": rel_path, "fragment": fragment})
                failures.append(f"CP-7 {label} missing fragment: {rel_path}::{fragment}")
    return {"missing": missing}


def _check_forbidden(failures: list[str]) -> dict[str, Any]:
    joined = "\n".join(_read(path) for path in UI_FILES)
    hits = [pattern for pattern in FORBIDDEN_PATTERNS if pattern in joined]
    for pattern in hits:
        failures.append(f"CP-7 close readiness found forbidden opened boundary: {pattern}")
    return {"hits": hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_targets": {rel: _compile(rel, failures) for rel in COMPILE_TARGETS},
        "cp_guards": _check_cp_guards(failures),
        "ui_files_exist": _check_file_exists(UI_FILES, failures, "ui_files"),
        "room_records_exist": _check_file_exists(ROOM_RECORDS, failures, "room_records"),
        "ui_fragments": _check_fragments(REQUIRED_UI_FRAGMENTS, failures, "ui_fragments"),
        "room_fragments": _check_fragments(REQUIRED_ROOM_FRAGMENTS, failures, "room_fragments"),
        "forbidden_boundaries": _check_forbidden(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operator_ui_first_complete_static_close_readiness_cp7",
        "cp": "CP-7",
        "status": "static_close_ready" if not failures else "open",
        "close_readiness_contract": {
            "static_guards_cp0_cp6_green": not failures,
            "manual_streamlit_smoke_recorded": False,
            "visual_ui_first_complete_claim_allowed": False,
            "next_required_action": "manual Streamlit smoke and final handoff update",
        },
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
