# path: ./tools/test_phase4a_operator_ui_health_language_presentation_guard.py
# desc: CP-2 guard for Health tab language presentation layer.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SELF_PATH = "tools/test_phase4a_operator_ui_health_language_presentation_guard.py"
CP0_GUARD = "tools/test_phase4a_operator_ui_polish_roadmap_guard.py"
CP1_GUARD = "tools/test_phase4a_operator_ui_health_widget_readability_guard.py"
HEALTH_TEXTS = "btcts_next/src/btcts/apps/operator_ui/texts/health.py"
DASHBOARD_PANEL = "btcts_next/src/btcts/apps/operator_ui/components/dashboard_hub_source_panel.py"
UI_TEXT = "btcts_next/src/btcts/apps/operator_ui/ui_text.py"

COMPILE_TARGETS = [
    SELF_PATH,
    CP0_GUARD,
    CP1_GUARD,
    HEALTH_TEXTS,
    DASHBOARD_PANEL,
    UI_TEXT,
]

REQUIRED_HEALTH_TEXT_KEYS = [
    "health_widget_dashboard_source_title",
    "health_widget_dashboard_source_subtitle",
    "health_widget_status_label",
    "health_widget_details_label",
    "health_widget_hot_cold_metadata_title",
    "health_widget_no_dashboard_source_diagnostics",
    "ダッシュボード表示元診断",
    "状態",
    "詳細",
]

REQUIRED_DASHBOARD_FRAGMENTS = [
    "from btcts.apps.operator_ui.ui_text import get_text",
    "st.session_state.get(\"ui_lang\", \"en\")",
    "get_text(lang, \"health_widget_dashboard_source_title\")",
    "get_text(lang, \"health_widget_dashboard_source_subtitle\")",
    "get_text(lang, 'health_widget_status_label')",
    "get_text(lang, \"health_widget_details_label\")",
    "get_text(lang, \"health_widget_hot_cold_metadata_title\")",
    "get_text(lang, \"health_widget_no_dashboard_source_diagnostics\")",
    "live_shell.render_scrollable_key_value_rows",
    "not_broker_or_order_wiring",
]

FORBIDDEN_DASHBOARD_PATTERNS = [
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
]


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "operator_ui_health_language_presentation"
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
        failures.append(f"CP-2 language presentation missing fragment: {label}::{fragment}")
    return {"missing": missing}


def _check_forbidden(failures: list[str]) -> dict[str, Any]:
    text = _read(DASHBOARD_PANEL)
    hits = [pattern for pattern in FORBIDDEN_DASHBOARD_PATTERNS if pattern in text]
    for pattern in hits:
        failures.append(f"CP-2 language presentation opened forbidden boundary: {pattern}")
    return {"hits": hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_targets": {rel: _compile(rel, failures) for rel in COMPILE_TARGETS},
        "health_text_keys": _check_fragments(HEALTH_TEXTS, REQUIRED_HEALTH_TEXT_KEYS, "health_texts", failures),
        "dashboard_language_usage": _check_fragments(DASHBOARD_PANEL, REQUIRED_DASHBOARD_FRAGMENTS, "dashboard_panel", failures),
        "forbidden_boundaries": _check_forbidden(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operator_ui_health_language_presentation_guard_cp2",
        "cp": "CP-2",
        "status": "closed" if not failures else "open",
        "language_presentation_contract": {
            "text_owner": HEALTH_TEXTS,
            "render_consumer": DASHBOARD_PANEL,
            "presentation_only": True,
            "upstream_semantics_unchanged": True,
        },
        "next_recommended_cp": "manual Health ja smoke, then CP-3 Collector widget structure" if not failures else "fix_cp2_language_presentation",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
