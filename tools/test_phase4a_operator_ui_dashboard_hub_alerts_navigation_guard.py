# path: ./tools/test_phase4a_operator_ui_dashboard_hub_alerts_navigation_guard.py
# desc: CP-6 guard for bounded dashboard hub alerts/navigation status strip.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SELF_PATH = "tools/test_phase4a_operator_ui_dashboard_hub_alerts_navigation_guard.py"
CP_GUARDS = [
    "tools/test_phase4a_operator_ui_polish_roadmap_guard.py",
    "tools/test_phase4a_operator_ui_health_widget_readability_guard.py",
    "tools/test_phase4a_operator_ui_health_language_presentation_guard.py",
    "tools/test_phase4a_operator_ui_collector_widget_structure_guard.py",
    "tools/test_phase4a_operator_ui_warroom_widget_structure_guard.py",
    "tools/test_phase4a_operator_ui_other_tabs_widget_consistency_guard.py",
]
APP = "btcts_next/src/btcts/apps/operator_ui/app.py"
COMMON_TEXTS = "btcts_next/src/btcts/apps/operator_ui/texts/common.py"
LIVE_SHELL = "btcts_next/src/btcts/apps/operator_ui/components/live_shell.py"

COMPILE_TARGETS = [SELF_PATH, *CP_GUARDS, APP, COMMON_TEXTS, LIVE_SHELL]

REQUIRED_APP_FRAGMENTS = [
    "def render_dashboard_hub_status_strip(",
    "display-only dashboard hub status strip",
    "does not decide market meaning, load data, or change routing",
    "live_shell.get_registered_slots(selected_page_key)",
    "live_shell.panel_container(",
    "dashboard_hub_status_title",
    "dashboard_hub_selected_page",
    "dashboard_hub_refresh",
    "dashboard_hub_registered_widgets",
    "dashboard_hub_alert_normal",
    "dashboard_hub_alert_attention",
    "render_dashboard_hub_status_strip(",
    "page_defs = [",
    "selection = st.sidebar.radio(",
    "pages = {page_key: page_module for page_key, _, page_module in page_defs}",
    "page_module.render()",
    "live_shell.render_page_auto_refresh(",
]

REQUIRED_COMMON_TEXTS = [
    "dashboard_hub_status_title",
    "dashboard_hub_status_caption",
    "dashboard_hub_selected_page",
    "dashboard_hub_refresh",
    "dashboard_hub_registered_widgets",
    "dashboard_hub_alert_normal",
    "dashboard_hub_alert_attention",
    "ダッシュボードハブ",
    "市場意味の判定は行いません",
]

FORBIDDEN_APP_PATTERNS = [
    "from btcts.market_engine",
    "btcts.market_engine",
    "from btcts.broker",
    "btcts.broker",
    "broker_order",
    "place_order",
    "submit_order",
    "execute_order",
    "run_training",
    "training_job",
    "start_inference_runtime",
    "run_inference_runtime",
    "payload_loader",
    "dataset_reader",
    "copy_executor",
    "delete_executor",
    "archive_gc_enable",
    "page_defs = {}",
]


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "operator_ui_dashboard_hub_alerts_navigation"
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
        failures.append(f"CP-6 dashboard hub missing fragment: {label}::{fragment}")
    return {"missing": missing}


def _check_forbidden(failures: list[str]) -> dict[str, Any]:
    text = _read(APP)
    hits = [pattern for pattern in FORBIDDEN_APP_PATTERNS if pattern in text]
    for pattern in hits:
        failures.append(f"CP-6 dashboard hub opened forbidden boundary or rewrote routing: {pattern}")
    return {"hits": hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_targets": {rel: _compile(rel, failures) for rel in COMPILE_TARGETS},
        "app_fragments": _check_fragments(APP, REQUIRED_APP_FRAGMENTS, "app", failures),
        "common_texts": _check_fragments(COMMON_TEXTS, REQUIRED_COMMON_TEXTS, "common_texts", failures),
        "forbidden_boundaries": _check_forbidden(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operator_ui_dashboard_hub_alerts_navigation_guard_cp6",
        "cp": "CP-6",
        "status": "closed" if not failures else "open",
        "dashboard_hub_contract": {
            "app_owner": APP,
            "text_owner": COMMON_TEXTS,
            "common_shell": LIVE_SHELL,
            "routing_rewrite": False,
            "layout_rewrite": False,
            "market_meaning_owner": False,
            "presentation_only": True,
        },
        "next_recommended_cp": "manual navigation smoke, then CP-7 UI first-complete close" if not failures else "fix_cp6_dashboard_hub",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
