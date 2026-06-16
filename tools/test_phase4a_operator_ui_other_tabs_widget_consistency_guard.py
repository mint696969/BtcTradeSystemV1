# path: ./tools/test_phase4a_operator_ui_other_tabs_widget_consistency_guard.py
# desc: CP-5 guard for other Operator UI tabs widget/readability consistency.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SELF_PATH = "tools/test_phase4a_operator_ui_other_tabs_widget_consistency_guard.py"
CP_GUARDS = [
    "tools/test_phase4a_operator_ui_polish_roadmap_guard.py",
    "tools/test_phase4a_operator_ui_health_widget_readability_guard.py",
    "tools/test_phase4a_operator_ui_health_language_presentation_guard.py",
    "tools/test_phase4a_operator_ui_collector_widget_structure_guard.py",
    "tools/test_phase4a_operator_ui_warroom_widget_structure_guard.py",
]
LOGS_PAGE = "btcts_next/src/btcts/apps/operator_ui/views/logs_page.py"
CONFIG_PAGE = "btcts_next/src/btcts/apps/operator_ui/views/config_page.py"
RESEARCH_PAGE = "btcts_next/src/btcts/apps/operator_ui/views/research_page.py"
REPLAY_PAGE = "btcts_next/src/btcts/apps/operator_ui/views/replay_page.py"
LIVE_SHELL = "btcts_next/src/btcts/apps/operator_ui/components/live_shell.py"

COMPILE_TARGETS = [SELF_PATH, *CP_GUARDS, LOGS_PAGE, CONFIG_PAGE, RESEARCH_PAGE, REPLAY_PAGE, LIVE_SHELL]

REQUIRED_BY_FILE = {
    LOGS_PAGE: [
        "from btcts.apps.operator_ui.components import live_shell",
        "def _render_logs_scrollable_json_block(",
        "presentation-only scrollable JSON",
        "live_shell.render_scrollable_text_block(",
        "_render_logs_scrollable_json_block(best_strategy",
    ],
    CONFIG_PAGE: [
        "from btcts.apps.operator_ui.components import live_shell",
        "live_shell.panel_container(label=\"Configuration selection\"",
        "Exchange Configuration",
    ],
    RESEARCH_PAGE: [
        "from btcts.apps.operator_ui.components import live_shell",
        "def _render_research_scrollable_text(",
        "Research-page long presentation text",
        "live_shell.render_scrollable_text_block(",
        "_render_research_scrollable_text(",
    ],
    REPLAY_PAGE: [
        "from btcts.apps.operator_ui.components import live_shell",
        "def _render_replay_scrollable_json_block(",
        "def _render_replay_scrollable_text(",
        "presentation-only scrollable JSON",
        "_render_replay_scrollable_json_block(report",
        "_render_replay_scrollable_json_block(regime_report",
        "_render_replay_scrollable_json_block(sandbox_report",
        "_render_replay_scrollable_text(",
    ],
    LIVE_SHELL: [
        "def render_scrollable_text_block(",
        "def render_scrollable_key_value_rows(",
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
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "operator_ui_other_tabs_widget_consistency"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _check_fragments(failures: list[str]) -> dict[str, Any]:
    missing: list[dict[str, str]] = []
    for rel_path, fragments in REQUIRED_BY_FILE.items():
        text = _read(rel_path)
        for fragment in fragments:
            if fragment not in text:
                missing.append({"path": rel_path, "fragment": fragment})
                failures.append(f"CP-5 other tabs consistency missing fragment: {rel_path}::{fragment}")
    return {"missing": missing}


def _check_forbidden(failures: list[str]) -> dict[str, Any]:
    joined = "\n".join(_read(path) for path in (LOGS_PAGE, CONFIG_PAGE, RESEARCH_PAGE, REPLAY_PAGE))
    hits = [pattern for pattern in FORBIDDEN_PATTERNS if pattern in joined]
    for pattern in hits:
        failures.append(f"CP-5 other tabs consistency opened forbidden boundary: {pattern}")
    return {"hits": hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_targets": {rel: _compile(rel, failures) for rel in COMPILE_TARGETS},
        "required_fragments": _check_fragments(failures),
        "forbidden_boundaries": _check_forbidden(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operator_ui_other_tabs_widget_consistency_guard_cp5",
        "cp": "CP-5",
        "status": "closed" if not failures else "open",
        "other_tabs_consistency_contract": {
            "logs": LOGS_PAGE,
            "config": CONFIG_PAGE,
            "research": RESEARCH_PAGE,
            "replay": REPLAY_PAGE,
            "common_shell": LIVE_SHELL,
            "presentation_only": True,
            "no_new_data_reader": True,
            "no_runtime_expansion": True,
        },
        "next_recommended_cp": "manual other-tabs smoke, then CP-6 dashboard hub alerts/navigation" if not failures else "fix_cp5_other_tabs_consistency",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
