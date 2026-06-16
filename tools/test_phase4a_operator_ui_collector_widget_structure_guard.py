# path: ./tools/test_phase4a_operator_ui_collector_widget_structure_guard.py
# desc: CP-3 guard for Collector tab widget structure and scrollable diagnostics presentation.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SELF_PATH = "tools/test_phase4a_operator_ui_collector_widget_structure_guard.py"
CP0_GUARD = "tools/test_phase4a_operator_ui_polish_roadmap_guard.py"
CP1_GUARD = "tools/test_phase4a_operator_ui_health_widget_readability_guard.py"
CP2_GUARD = "tools/test_phase4a_operator_ui_health_language_presentation_guard.py"
LIVE_SHELL = "btcts_next/src/btcts/apps/operator_ui/components/live_shell.py"
COLLECTOR_PAGE = "btcts_next/src/btcts/apps/operator_ui/views/collector_page.py"
COLLECTOR_TOP = "btcts_next/src/btcts/apps/operator_ui/components/collector_top_panels.py"
SLOT_DEFINITIONS = "btcts_next/src/btcts/apps/operator_ui/components/slot_definitions.py"

COMPILE_TARGETS = [
    SELF_PATH,
    CP0_GUARD,
    CP1_GUARD,
    CP2_GUARD,
    LIVE_SHELL,
    COLLECTOR_PAGE,
    COLLECTOR_TOP,
    SLOT_DEFINITIONS,
]

REQUIRED_COLLECTOR_FRAGMENTS = [
    "def _render_scrollable_json_block(",
    "presentation-only scrollable JSON",
    "live_shell.render_scrollable_text_block(",
    "json.dumps(payload, ensure_ascii=False, indent=2, default=str)",
    "_render_scrollable_json_block(market_state_info",
    "_render_scrollable_json_block(origin_state",
    "_render_scrollable_json_block(rate_state",
    "_render_scrollable_json_block(",
    "collector_runtime_snapshot()",
    "load_state()",
    "read_recent_audit_events(lines=200)",
    "collector_widget_slot(\"origin_continuity_audit\")",
    "collector_widget_slot(\"system_stats\")",
    "collector_widget_slot(\"execution_feed\")",
]

REQUIRED_LIVE_SHELL_FRAGMENTS = [
    "def render_scrollable_text_block(",
    "def render_scrollable_key_value_rows(",
    "if isinstance(rows, (list, tuple)):",
    "presentation-only helper",
    "must not read data, mutate runtime state",
]

REQUIRED_TOP_PANEL_FRAGMENTS = [
    "make_slot_meta(",
    "status_summary",
    "supervisor_control",
    "rate_control",
    "origin_continuity_summary",
    "st.dataframe(rows, width=\"stretch\")",
]

FORBIDDEN_NEW_PATTERNS = [
    "rglob(",
    "glob(\"**/*\")",
    "payload_loader",
    "dataset_reader",
    "from btcts.market_engine",
    "btcts.market_engine",
    "from btcts.broker",
    "btcts.broker",
    "broker_order",
    "place_order",
    "run_inference",
    "training_job",
    "archive_gc_enable",
]


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "operator_ui_collector_widget_structure"
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
        failures.append(f"CP-3 Collector widget structure missing fragment: {label}::{fragment}")
    return {"missing": missing}


def _check_forbidden(failures: list[str]) -> dict[str, Any]:
    joined = "\n".join(_read(path) for path in (COLLECTOR_PAGE, COLLECTOR_TOP, LIVE_SHELL))
    hits = [pattern for pattern in FORBIDDEN_NEW_PATTERNS if pattern in joined]
    for pattern in hits:
        failures.append(f"CP-3 Collector widget structure opened forbidden/heavy boundary: {pattern}")
    return {"hits": hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_targets": {rel: _compile(rel, failures) for rel in COMPILE_TARGETS},
        "collector_page_fragments": _check_fragments(COLLECTOR_PAGE, REQUIRED_COLLECTOR_FRAGMENTS, "collector_page", failures),
        "live_shell_fragments": _check_fragments(LIVE_SHELL, REQUIRED_LIVE_SHELL_FRAGMENTS, "live_shell", failures),
        "collector_top_panel_fragments": _check_fragments(COLLECTOR_TOP, REQUIRED_TOP_PANEL_FRAGMENTS, "collector_top_panels", failures),
        "forbidden_boundaries": _check_forbidden(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operator_ui_collector_widget_structure_guard_cp3",
        "cp": "CP-3",
        "status": "closed" if not failures else "open",
        "collector_widget_structure_contract": {
            "page_owner": COLLECTOR_PAGE,
            "top_panel_owner": COLLECTOR_TOP,
            "common_shell": LIVE_SHELL,
            "raw_json_display": "scrollable_text_block",
            "presentation_only": True,
            "no_new_data_reader": True,
            "no_heavy_scan": True,
        },
        "next_recommended_cp": "manual Collector smoke, then CP-4 WarRoom widget structure" if not failures else "fix_cp3_collector_widget_structure",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
