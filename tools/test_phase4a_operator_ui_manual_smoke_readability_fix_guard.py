# path: ./tools/test_phase4a_operator_ui_manual_smoke_readability_fix_guard.py
# desc: Guard for manual-smoke readability fix after CP-7 static close readiness.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
from pathlib import Path
from typing import Any

from btcts.apps.operator_ui.ui_text import get_text

REPO_ROOT = Path(__file__).resolve().parents[1]
SELF_PATH = "tools/test_phase4a_operator_ui_manual_smoke_readability_fix_guard.py"
CP7_GUARD = "tools/test_phase4a_operator_ui_first_complete_close_guard.py"
LIVE_SHELL = "btcts_next/src/btcts/apps/operator_ui/components/live_shell.py"
HEALTH_TEXTS = "btcts_next/src/btcts/apps/operator_ui/texts/health.py"
DASHBOARD_PANEL = "btcts_next/src/btcts/apps/operator_ui/components/dashboard_hub_source_panel.py"

COMPILE_TARGETS = [SELF_PATH, CP7_GUARD, LIVE_SHELL, HEALTH_TEXTS, DASHBOARD_PANEL]

REQUIRED_LIVE_SHELL_FRAGMENTS = [
    "def render_scrollable_text_block(",
    "color: inherit;",
    "background: rgba(148, 163, 184, 0.10);",
    "live-shell-scrollable-text-block-muted",
]

FORBIDDEN_LIVE_SHELL_FRAGMENTS = [
    "color: rgba(250,250,250,0.74);",
]

REQUIRED_HEALTH_JA_VALUES = {
    "health_widget_dashboard_source_title": "ダッシュボード表示元診断",
    "health_widget_dashboard_source_subtitle": "ダッシュボードwidget向け表示元のread-only準備状態",
    "health_widget_status_label": "状態",
    "health_widget_details_label": "詳細",
    "health_widget_hot_cold_metadata_title": "Hot/Coldメタデータ",
    "health_widget_no_dashboard_source_diagnostics": "ダッシュボード表示元診断はまだ利用できません。",
}

FORBIDDEN_BOUNDARY_PATTERNS = [
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
]


def _read(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "operator_ui_manual_smoke_readability_fix"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _check_live_shell(failures: list[str]) -> dict[str, Any]:
    text = _read(LIVE_SHELL)
    missing = [fragment for fragment in REQUIRED_LIVE_SHELL_FRAGMENTS if fragment not in text]
    forbidden_hits = [fragment for fragment in FORBIDDEN_LIVE_SHELL_FRAGMENTS if fragment in text]
    for fragment in missing:
        failures.append(f"manual smoke readability fix missing live_shell fragment: {fragment}")
    for fragment in forbidden_hits:
        failures.append(f"manual smoke readability fix still has unreadable light-theme CSS: {fragment}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def _check_health_text_resolution(failures: list[str]) -> dict[str, Any]:
    resolved: dict[str, str] = {}
    bad: dict[str, str] = {}
    for key, expected in REQUIRED_HEALTH_JA_VALUES.items():
        value = get_text("ja", key)
        resolved[key] = value
        if value != expected:
            bad[key] = value
            failures.append(f"manual smoke readability fix failed ja text resolution: {key} -> {value!r}")
        if value == key:
            failures.append(f"manual smoke readability fix key still leaks in ja UI: {key}")
    return {"resolved": resolved, "bad": bad}


def _check_health_text_file_shape(failures: list[str]) -> dict[str, Any]:
    text = _read(HEALTH_TEXTS)
    ja_section_pos = text.find('    "ja": {')
    en_section_pos = text.find('    "en": {')
    title_count = text.count('"health_widget_dashboard_source_title"')
    ja_has = '"health_widget_dashboard_source_title": "ダッシュボード表示元診断"' in text[ja_section_pos:]
    en_has_japanese_misplaced = False
    if en_section_pos >= 0 and ja_section_pos > en_section_pos:
        en_section = text[en_section_pos:ja_section_pos]
        en_has_japanese_misplaced = '"health_widget_dashboard_source_title": "ダッシュボード表示元診断"' in en_section
    if title_count != 2:
        failures.append(f"manual smoke readability fix unexpected title key count in health.py: {title_count}")
    if not ja_has:
        failures.append("manual smoke readability fix ja health widget title missing from ja section")
    if en_has_japanese_misplaced:
        failures.append("manual smoke readability fix still has Japanese dashboard title misplaced in en section")
    return {"title_key_count": title_count, "ja_has": ja_has, "en_has_japanese_misplaced": en_has_japanese_misplaced}


def _check_forbidden_boundaries(failures: list[str]) -> dict[str, Any]:
    joined = "\n".join(_read(path) for path in (LIVE_SHELL, HEALTH_TEXTS, DASHBOARD_PANEL))
    hits = [pattern for pattern in FORBIDDEN_BOUNDARY_PATTERNS if pattern in joined]
    for pattern in hits:
        failures.append(f"manual smoke readability fix opened forbidden boundary: {pattern}")
    return {"hits": hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_targets": {rel: _compile(rel, failures) for rel in COMPILE_TARGETS},
        "live_shell_readability_css": _check_live_shell(failures),
        "health_text_resolution": _check_health_text_resolution(failures),
        "health_text_file_shape": _check_health_text_file_shape(failures),
        "forbidden_boundaries": _check_forbidden_boundaries(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operator_ui_manual_smoke_readability_fix",
        "status": "fixed_static_ready_for_resmoke" if not failures else "open",
        "manual_smoke_issue": {
            "observed": True,
            "visual_ui_first_complete_claim_allowed": False,
            "fix_scope": [LIVE_SHELL, HEALTH_TEXTS],
            "requires_resmoke": True,
        },
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
