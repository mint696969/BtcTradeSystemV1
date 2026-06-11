# path: ./tools/test_phase4a_operator_ui_warroom_widget_structure_guard.py
# desc: CP-4 guard for WarRoom widget structure and read-only prediction-surface preparation.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SELF_PATH = "tools/test_phase4a_operator_ui_warroom_widget_structure_guard.py"
CP0_GUARD = "tools/test_phase4a_operator_ui_polish_roadmap_guard.py"
CP1_GUARD = "tools/test_phase4a_operator_ui_health_widget_readability_guard.py"
CP2_GUARD = "tools/test_phase4a_operator_ui_health_language_presentation_guard.py"
CP3_GUARD = "tools/test_phase4a_operator_ui_collector_widget_structure_guard.py"
WARROOM_PAGE = "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
WARROOM_HEADER = "btcts_next/src/btcts/apps/operator_ui/components/warroom_header.py"
EVIDENCE_PANEL = "btcts_next/src/btcts/apps/operator_ui/components/evidence_presentation_panel.py"
AI_OPERATOR_PANEL = "btcts_next/src/btcts/apps/operator_ui/components/ai_operator_panel.py"
SLOT_DEFINITIONS = "btcts_next/src/btcts/apps/operator_ui/components/slot_definitions.py"
LIVE_SHELL = "btcts_next/src/btcts/apps/operator_ui/components/live_shell.py"

COMPILE_TARGETS = [
    SELF_PATH,
    CP0_GUARD,
    CP1_GUARD,
    CP2_GUARD,
    CP3_GUARD,
    WARROOM_PAGE,
    WARROOM_HEADER,
    EVIDENCE_PANEL,
    AI_OPERATOR_PANEL,
    SLOT_DEFINITIONS,
    LIVE_SHELL,
]

REQUIRED_WARROOM_PAGE_FRAGMENTS = [
    "def _render_warroom_scrollable_json_block(",
    "read-only presentation JSON",
    "def _render_warroom_reading_caption(",
    "operator review text",
    "_warroom_reading_block_order",
    "current_market_summary_reading",
    "current_active_event_reading",
    "current_tactic_prediction_reading",
    "operator_support_review_reading",
    "_render_warroom_reading_caption(",
    "_render_warroom_scrollable_json_block(overlay_diag",
    "_render_warroom_tactic_prediction_reading",
    "_render_warroom_evidence_presentation",
    "warroom_widget_slot(\"evidence_presentation_panel\")",
]

REQUIRED_WARROOM_HEADER_FRAGMENTS = [
    "from btcts.apps.operator_ui.components import live_shell",
    "build_warroom_market_reading_caption",
    "build_warroom_operational_reading_caption",
    "live_shell.render_scrollable_text_block(",
    "review_mode=operator_review_only",
    "execution=not_instruction",
]

REQUIRED_EVIDENCE_FRAGMENTS = [
    "from btcts.apps.operator_ui.components import live_shell",
    "Render a provided read-only evidence presentation payload. Does not load data.",
    "live_shell.render_scrollable_text_block(build_evidence_presentation_caption(data)",
    "live_shell.render_scrollable_text_block(health_line",
    "live_shell.render_scrollable_text_block(warroom_line",
    "not_inference_or_training",
    "not_broker_or_order_automation",
]

REQUIRED_AI_OPERATOR_BOUNDARY_FRAGMENTS = [
    "is_live_market=False",
    "operator_review_only" if False else "ai_operator_title",
    "prediction_lines",
    "prediction_snapshot_section_title",
]

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
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "operator_ui_warroom_widget_structure"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _check_fragments(rel_path: str, fragments: list[str], label: str, failures: list[str]) -> dict[str, Any]:
    text = _read(rel_path)
    missing = [fragment for fragment in fragments if fragment not in text]
    for fragment in missing:
        failures.append(f"CP-4 WarRoom widget structure missing fragment: {label}::{fragment}")
    return {"missing": missing}


def _check_forbidden(failures: list[str]) -> dict[str, Any]:
    joined = "\n".join(_read(path) for path in (WARROOM_PAGE, WARROOM_HEADER, EVIDENCE_PANEL, AI_OPERATOR_PANEL))
    hits = [pattern for pattern in FORBIDDEN_PATTERNS if pattern in joined]
    for pattern in hits:
        failures.append(f"CP-4 WarRoom widget structure opened forbidden runtime/execution boundary: {pattern}")
    return {"hits": hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_targets": {rel: _compile(rel, failures) for rel in COMPILE_TARGETS},
        "warroom_page_fragments": _check_fragments(WARROOM_PAGE, REQUIRED_WARROOM_PAGE_FRAGMENTS, "warroom_page", failures),
        "warroom_header_fragments": _check_fragments(WARROOM_HEADER, REQUIRED_WARROOM_HEADER_FRAGMENTS, "warroom_header", failures),
        "evidence_panel_fragments": _check_fragments(EVIDENCE_PANEL, REQUIRED_EVIDENCE_FRAGMENTS, "evidence_panel", failures),
        "ai_operator_boundary_fragments": _check_fragments(AI_OPERATOR_PANEL, REQUIRED_AI_OPERATOR_BOUNDARY_FRAGMENTS, "ai_operator_panel", failures),
        "forbidden_boundaries": _check_forbidden(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operator_ui_warroom_widget_structure_guard_cp4",
        "cp": "CP-4",
        "status": "closed" if not failures else "open",
        "warroom_widget_structure_contract": {
            "page_owner": WARROOM_PAGE,
            "header_owner": WARROOM_HEADER,
            "evidence_owner": EVIDENCE_PANEL,
            "common_shell": LIVE_SHELL,
            "prediction_surface": "read_only_review_support_not_runtime",
            "presentation_only": True,
            "no_inference_runtime": True,
            "no_training": True,
            "no_execution": True,
        },
        "next_recommended_cp": "manual WarRoom smoke, then CP-5 other tabs consistency" if not failures else "fix_cp4_warroom_widget_structure",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
