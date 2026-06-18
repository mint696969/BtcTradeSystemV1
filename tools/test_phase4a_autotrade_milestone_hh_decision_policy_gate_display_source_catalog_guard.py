# path: ./tools/test_phase4a_autotrade_milestone_hh_decision_policy_gate_display_source_catalog_guard.py
# desc: Guard S145 display source catalog entry for decision ledger policy gate display remains catalog/status-only with no rendering, commands, runtime wiring, decision append, mode apply, grants, writes, or broker behavior.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.ai_operator_display_sources import (
    AI_OPERATOR_DISPLAY_SOURCE_CATALOG,
    load_operator_display_source_catalog,
)
from btcts.apps.operator_ui.components.autotrade_decision_ledger_policy_gate_display import (
    AUTOTRADE_DECISION_LEDGER_POLICY_GATE_DISPLAY_CONTRACT,
)
from btcts.apps.operator_ui.components.operator_display_source_catalog import (
    load_operator_dashboard_display_source_catalog,
    select_display_sources_for_consumer,
)
from btcts.apps.operator_ui.hub.display_source_registry import (
    display_source_keys_for_page,
    load_dashboard_hub_display_source_registry,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/ai_operator_display_sources.py"
DISPLAY_MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/autotrade_decision_ledger_policy_gate_display.py"
FORBIDDEN_IMPORT_PREFIXES = (
    "streamlit",
    "btcts.autotrade.live_shadow",
    "btcts.autotrade.ledger",
    "btcts.autotrade.execution",
    "btcts.autotrade.runtime_paths",
    "btcts.collector_vnext",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
    "websocket",
)
FORBIDDEN_TOKENS = (
    "st.button",
    "st.checkbox",
    "streamlit",
    "append_decision_jsonl",
    "run_shadow_decision_from_snapshot",
    "run_latest_market_state_shadow_decision",
    "build_action_candidate",
    "build_shadow_decision_record",
    "decision_ledger_path",
    "default_shadow_decision_ledger_path",
    "persist=True",
    "persist: bool = True",
    "validate_and_append_command",
    "submit_mode_change_command_request",
    "Path(",
    "mkdir(",
    "write_text(",
    ".write(",
    "open(",
    "append_jsonl(",
    "json.dump",
    "place_order(",
    "send_order(",
    "create_order(",
    "requests.get",
    "requests.post",
    "httpx.get",
    "httpx.post",
    '"decision_append_allowed": True',
    '"decision_ledger_integration_allowed": True',
    '"live_shadow_behavior_change_allowed": True',
    '"persist_true_allowed": True',
    '"would_append_shadow_decision": True',
    '"would_apply_mode": True',
    '"would_execute_prearmed_grant": True',
    '"would_write_runtime_artifact": True',
    '"would_write_preview_status_artifact": True',
    '"would_send_to_broker": True',
)
EXPECTED_FALSE_FLAGS = (
    "decision_append_allowed",
    "decision_ledger_integration_allowed",
    "live_shadow_behavior_change_allowed",
    "persist_true_allowed",
    "would_append_shadow_decision",
    "would_apply_mode",
    "would_execute_prearmed_grant",
    "would_write_runtime_artifact",
    "would_write_preview_status_artifact",
    "would_send_to_broker",
)
SOURCE_KEY = "autotrade_decision_ledger_policy_gate_display"
SOURCE_TYPE = "autotrade_decision_ledger_policy_gate_display_packet"


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
    return out


def _entry(items: tuple[dict, ...]) -> dict:
    for item in items:
        if item.get("source_key") == SOURCE_KEY:
            return dict(item)
    return {}


def _all_false(payload: dict[str, object]) -> bool:
    return all(payload.get(name) is False for name in EXPECTED_FALSE_FLAGS)


def main() -> int:
    failures: list[str] = []
    catalog_text = CATALOG.read_text(encoding="utf-8") if CATALOG.exists() else ""
    display_text = DISPLAY_MODULE.read_text(encoding="utf-8") if DISPLAY_MODULE.exists() else ""
    for target, text in ((CATALOG, catalog_text), (DISPLAY_MODULE, display_text)):
        try:
            compile(text, str(target), "exec")
        except Exception as exc:
            failures.append(f"compile failed: {target.relative_to(REPO_ROOT)}: {exc}")
        imports = _imports_from(target)
        for prefix in FORBIDDEN_IMPORT_PREFIXES:
            if any(item == prefix or item.startswith(prefix + ".") for item in imports):
                failures.append(f"forbidden import in {target.relative_to(REPO_ROOT)}: {prefix}")
    for token in FORBIDDEN_TOKENS:
        if token in catalog_text:
            failures.append(f"forbidden token in catalog: {token}")

    ai_catalog = load_operator_display_source_catalog()
    ai_entry = _entry(ai_catalog)
    dashboard_catalog = load_operator_dashboard_display_source_catalog()
    dashboard_entry = _entry(tuple(dict(item) for item in dashboard_catalog.get("sources") or ()))
    future_sources = select_display_sources_for_consumer("future_widget", dashboard_catalog)
    health_sources = select_display_sources_for_consumer("health_tab", dashboard_catalog)
    registry = load_dashboard_hub_display_source_registry()
    health_page_keys = display_source_keys_for_page("health", registry)
    future_page_keys = display_source_keys_for_page("logs", registry)

    checks = {
        "entry_present_in_ai_catalog": bool(ai_entry) and ai_entry.get("source_type") == SOURCE_TYPE,
        "entry_present_in_dashboard_catalog": bool(dashboard_entry) and dashboard_entry.get("source_origin") == "ai_operator_display_sources",
        "entry_is_read_only_catalog_only": ai_entry.get("read_only_contract") is True and ai_entry.get("not_runtime_wiring") is True and ai_entry.get("not_ui_rendering") is True and ai_entry.get("no_command_buttons") is True,
        "entry_references_display_packet_builder": ai_entry.get("display_packet_builder") == "build_autotrade_decision_ledger_policy_gate_display_packet" and ai_entry.get("display_packet_module", "").endswith("autotrade_decision_ledger_policy_gate_display"),
        "entry_safety_flags_false": _all_false(ai_entry),
        "display_contract_still_read_only": AUTOTRADE_DECISION_LEDGER_POLICY_GATE_DISPLAY_CONTRACT["not_ui_rendering"] is True and AUTOTRADE_DECISION_LEDGER_POLICY_GATE_DISPLAY_CONTRACT["no_command_buttons"] is True,
        "future_widget_selection_includes_entry": SOURCE_KEY in tuple(item.get("source_key") for item in future_sources),
        "health_selection_includes_entry": SOURCE_KEY in tuple(item.get("source_key") for item in health_sources),
        "registry_health_page_includes_entry": SOURCE_KEY in health_page_keys,
        "registry_future_pages_include_entry": SOURCE_KEY in future_page_keys,
        "no_duplicate_catalog_source_key": sum(1 for item in AI_OPERATOR_DISPLAY_SOURCE_CATALOG if item.get("source_key") == SOURCE_KEY) == 1,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty_lines = [line for line in proc.stdout.splitlines() if line.strip()]
    allowed_dirty_markers = (
        "btcts_next/src/btcts/apps/operator_ui/components/ai_operator_display_sources.py",
        "tools/test_phase4a_autotrade_milestone_hh_decision_policy_gate_display_source_catalog_guard.py",
        "tools/test_phase4a_autotrade_milestone_hh_decision_policy_gate_display_source_catalog_close_guard.py",
    )
    unexpected_dirty = [line for line in dirty_lines if not any(marker in line for marker in allowed_dirty_markers)]
    failures.extend(f"unexpected dirty file during HH: {line}" for line in unexpected_dirty)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_hh_decision_policy_gate_display_source_catalog_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"only_expected_files_dirty": not unexpected_dirty},
        "sample": {
            "ai_entry": ai_entry,
            "dashboard_entry": dashboard_entry,
            "health_page_keys": health_page_keys,
            "future_page_keys": future_page_keys,
        },
        "dirty_lines": dirty_lines,
        "unexpected_dirty": unexpected_dirty,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_decision_policy_gate_display_source_catalog_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
