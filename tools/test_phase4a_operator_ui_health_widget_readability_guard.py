# path: ./tools/test_phase4a_operator_ui_health_widget_readability_guard.py
# desc: CP-1 guard for Health tab widget readability helpers and bounded presentation-only usage.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SELF_PATH = "tools/test_phase4a_operator_ui_health_widget_readability_guard.py"
CP0_GUARD = "tools/test_phase4a_operator_ui_polish_roadmap_guard.py"
LIVE_SHELL = "btcts_next/src/btcts/apps/operator_ui/components/live_shell.py"
DASHBOARD_PANEL = "btcts_next/src/btcts/apps/operator_ui/components/dashboard_hub_source_panel.py"
HEALTH_TOP = "btcts_next/src/btcts/apps/operator_ui/components/health_top_panels.py"
HEALTH_DETAIL = "btcts_next/src/btcts/apps/operator_ui/components/health_detail_panels.py"
HEALTH_PAGE = "btcts_next/src/btcts/apps/operator_ui/views/health_page.py"

COMPILE_TARGETS = [
    SELF_PATH,
    CP0_GUARD,
    LIVE_SHELL,
    DASHBOARD_PANEL,
    HEALTH_TOP,
    HEALTH_DETAIL,
    HEALTH_PAGE,
]

REQUIRED_BY_FILE = {
    LIVE_SHELL: [
        "def render_scrollable_text_block(",
        "def render_scrollable_key_value_rows(",
        "live-shell-scrollable-text-block",
        "overflow-y: auto",
        "overflow-wrap: anywhere",
        "white-space: pre-wrap",
        "presentation-only helper",
        "must not read data, mutate runtime state",
    ],
    DASHBOARD_PANEL: [
        "live_shell.render_scrollable_key_value_rows(summary_rows",
        "live_shell.render_scrollable_key_value_rows(detail_rows",
        "live_shell.render_scrollable_key_value_rows(hot_cold_rows",
        "not_app_py_wiring",
        "not_page_routing",
        "not_runtime_wiring",
        "not_broker_or_order_wiring",
    ],
    HEALTH_TOP: [
        "live_shell.render_scrollable_text_block(digest_caption",
        "live_shell.render_scrollable_text_block(operational_reading_caption",
        "build_health_digest_layer3_summary_caption",
        "build_health_digest_operational_reading_caption",
    ],
    HEALTH_DETAIL: [
        "live_shell.render_scrollable_text_block(",
        "build_health_digest_current_state_caption",
    ],
}

FORBIDDEN_NEW_SOURCE_PATTERNS = {
    DASHBOARD_PANEL: [
        "open(",
        "Path(",
        "read_text(",
        "write_text(",
        "load_health_snapshot",
        "load_state(",
        "from btcts.market_engine",
        "btcts.market_engine",
        "from btcts.broker",
        "btcts.broker",
        "broker_order",
        "place_order",
        "run_inference",
        "training_job",
        "payload_loader",
        "dataset_reader",
        "copy_executor",
        "delete_executor",
        "archive_gc_enable",
    ],
    LIVE_SHELL: [
        "load_health_snapshot",
        "collector_runtime_snapshot",
        "market_state_diagnostics",
        "place_order",
        "broker_order",
        "archive_gc_enable",
        "dataset_reader",
        "payload_loader",
    ],
}


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "operator_ui_health_widget_readability"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _check_required_fragments(failures: list[str]) -> dict[str, Any]:
    missing: list[dict[str, str]] = []
    for rel_path, fragments in REQUIRED_BY_FILE.items():
        text = _read(rel_path)
        for fragment in fragments:
            if fragment not in text:
                missing.append({"path": rel_path, "fragment": fragment})
                failures.append(f"CP-1 readability missing fragment: {rel_path}::{fragment}")
    return {"missing": missing}


def _check_forbidden_patterns(failures: list[str]) -> dict[str, Any]:
    hits: list[dict[str, str]] = []
    for rel_path, patterns in FORBIDDEN_NEW_SOURCE_PATTERNS.items():
        text = _read(rel_path)
        for pattern in patterns:
            if pattern in text:
                hits.append({"path": rel_path, "pattern": pattern})
                failures.append(f"CP-1 readability introduced forbidden source/runtime pattern: {rel_path}::{pattern}")
    return {"hits": hits}


def _check_cp0_guard_available(failures: list[str]) -> dict[str, Any]:
    text = _read(CP0_GUARD)
    required = [
        "phase4a_operator_ui_polish_roadmap_guard_cp0",
        "CP-0",
        "responsibility_separation",
    ]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"CP-0 guard unavailable/mismatched for CP-1: {fragment}")
    return {"missing": missing}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_targets": {rel: _compile(rel, failures) for rel in COMPILE_TARGETS},
        "cp0_guard_available": _check_cp0_guard_available(failures),
        "required_fragments": _check_required_fragments(failures),
        "forbidden_patterns": _check_forbidden_patterns(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operator_ui_health_widget_readability_guard_cp1",
        "cp": "CP-1",
        "status": "closed" if not failures else "open",
        "readability_contract": {
            "common_shell": LIVE_SHELL,
            "wrap": True,
            "local_vertical_scroll": True,
            "presentation_only": True,
            "no_new_data_reader": True,
        },
        "next_recommended_cp": "manual Health smoke, then CP-2 Health language presentation" if not failures else "fix_cp1_readability",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
