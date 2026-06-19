# path: ./tools/test_phase4a_autotrade_milestone_iq_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_catalog_guard.py
# desc: Guard S180 closeout review chain closeout final status index catalog entry remains metadata-only with no rendering, commands, runtime payload loading, chain-closeout-summary/final/closeout/chain/status/checkpoint builder execution, decision append, mode apply, grants, writes, or broker behavior.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.ai_operator_display_sources import (
    load_operator_display_source_catalog,
    load_operator_display_sources,
)
from btcts.apps.operator_ui.components.operator_display_source_catalog import (
    load_operator_dashboard_display_source_catalog,
    select_display_sources_for_consumer,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index import (
    DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CHAIN_CLOSEOUT_FINAL_STATUS_INDEX_CONTRACT,
)
from btcts.apps.operator_ui.hub.display_source_registry import (
    display_source_keys_for_page,
    load_dashboard_hub_display_source_registry,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/ai_operator_display_sources.py"
FINAL_STATUS_INDEX = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index.py"
SOURCE_KEY = "decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index"
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
FORBIDDEN_CATALOG_TOKENS = (
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
    "command_buttons_allowed=True",
    "forms_or_toggles_allowed=True",
    "runtime_wiring_allowed=True",
    "ui_rendering_implementation_allowed=True",
    "decision_append_allowed=True",
    "decision_ledger_integration_allowed=True",
    "live_shadow_behavior_change_allowed=True",
    "persist_true_allowed=True",
    "would_append_shadow_decision=True",
    "would_apply_mode=True",
    "would_execute_prearmed_grant=True",
    "would_write_runtime_artifact=True",
    "would_write_preview_status_artifact=True",
    "would_send_to_broker=True",
)
FORBIDDEN_GUARD_EXECUTION_TOKENS = (
    "build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_packet(",
    "build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_summary_packet(",
    "build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_final_status_index_packet(",
    "build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_packet(",
    "build_decision_policy_gate_visibility_registry_chain_completion_final_status_index_packet(",
    "build_decision_policy_gate_visibility_completion_status_index_registry_visibility_chain_completion_packet(",
    "build_decision_policy_gate_visibility_completion_status_index_packet(",
    "build_decision_policy_gate_visibility_completion_checkpoint_packet(",
)
EXPECTED_FALSE_FLAGS = (
    "command_buttons_allowed",
    "forms_or_toggles_allowed",
    "runtime_wiring_allowed",
    "ui_rendering_implementation_allowed",
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
EXPECTED_DEPENDENCIES = (
    "decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_summary",
    "decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_summary_registry_visibility",
)


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
    return out


def _entry(items: tuple[dict, ...] | list[dict], source_key: str) -> dict:
    matches = [dict(item) for item in items if isinstance(item, dict) and item.get("source_key") == source_key]
    return matches[0] if matches else {}


def _all_false(payload: dict[str, object]) -> bool:
    return all(payload.get(name) is False for name in EXPECTED_FALSE_FLAGS)


def main() -> int:
    failures: list[str] = []
    catalog_text = CATALOG.read_text(encoding="utf-8")
    guard_text = Path(__file__).read_text(encoding="utf-8")
    try:
        compile(catalog_text, str(CATALOG), "exec")
        compile(FINAL_STATUS_INDEX.read_text(encoding="utf-8"), str(FINAL_STATUS_INDEX), "exec")
    except Exception as exc:
        failures.append(f"compile failed: {exc}")
    imports = _imports_from(CATALOG)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        if any(item == prefix or item.startswith(prefix + ".") for item in imports):
            failures.append(f"forbidden import in catalog: {prefix}")
    for token in FORBIDDEN_CATALOG_TOKENS:
        if token in catalog_text:
            failures.append(f"forbidden token in catalog: {token}")
    for token in FORBIDDEN_GUARD_EXECUTION_TOKENS:
        if guard_text.count(token) > 1:
            failures.append(f"guard may execute forbidden builder: {token}")

    ai_catalog = load_operator_display_source_catalog()
    ai_entry = _entry(ai_catalog, SOURCE_KEY)
    dashboard_catalog = load_operator_dashboard_display_source_catalog()
    dashboard_entry = _entry(tuple(dashboard_catalog.get("sources") or ()), SOURCE_KEY)
    registry = load_dashboard_hub_display_source_registry()
    health_keys = display_source_keys_for_page("health", registry)
    logs_keys = display_source_keys_for_page("logs", registry)
    health_selection = select_display_sources_for_consumer("health_tab", dashboard_catalog)
    future_selection = select_display_sources_for_consumer("future_widget", dashboard_catalog)
    built_sources = load_operator_display_sources()
    catalog_keys = [item.get("source_key") for item in ai_catalog if isinstance(item, dict)]
    checks = {
        "ai_entry_present": bool(ai_entry),
        "dashboard_entry_present": bool(dashboard_entry) and dashboard_entry.get("source_origin") == "ai_operator_display_sources",
        "entry_references_final_status_index_builder": ai_entry.get("status_index_module") == "btcts.apps.operator_ui.hub.decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index" and ai_entry.get("status_index_builder") == "build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_packet",
        "entry_dependencies": tuple(ai_entry.get("source_dependencies") or ()) == EXPECTED_DEPENDENCIES,
        "entry_metadata_only": ai_entry.get("data_model_only") is True and ai_entry.get("status_index_only") is True and ai_entry.get("final_status_index_only") is True and ai_entry.get("chain_closeout_final_status_index_only") is True and ai_entry.get("closeout_review_chain_closeout_final_status_index_only") is True and ai_entry.get("registry_visibility_chain_completion_closeout_review_chain_closeout_final_status_index_only") is True and ai_entry.get("not_runtime_payload_loading") is True and ai_entry.get("not_ui_rendering") is True,
        "entry_safety_flags_false": _all_false(ai_entry),
        "final_status_index_contract_still_data_only": DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CHAIN_CLOSEOUT_FINAL_STATUS_INDEX_CONTRACT["final_status_index_only"] is True and DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CHAIN_CLOSEOUT_FINAL_STATUS_INDEX_CONTRACT["no_command_buttons"] is True,
        "health_selection_includes_entry": SOURCE_KEY in tuple(item.get("source_key") for item in health_selection),
        "future_selection_includes_entry": SOURCE_KEY in tuple(item.get("source_key") for item in future_selection),
        "registry_health_page_includes_entry": SOURCE_KEY in health_keys,
        "registry_future_page_includes_entry": SOURCE_KEY in logs_keys,
        "no_duplicate_catalog_source_key": len(catalog_keys) == len(set(catalog_keys)),
        "not_loaded_as_runtime_display_source": SOURCE_KEY not in built_sources,
        "source_catalog_contains_entry": SOURCE_KEY in tuple(item.get("source_key") for item in built_sources.get("source_catalog") or ()),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty_lines = [line for line in proc.stdout.splitlines() if line.strip()]
    allowed_dirty_markers = (
        "btcts_next/src/btcts/apps/operator_ui/components/ai_operator_display_sources.py",
        "tools/test_phase4a_autotrade_milestone_iq_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_catalog_guard.py",
        "tools/test_phase4a_autotrade_milestone_iq_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_catalog_close_guard.py",
    )
    unexpected_dirty = [line for line in dirty_lines if not any(marker in line for marker in allowed_dirty_markers)]
    failures.extend(f"unexpected dirty file during IQ: {line}" for line in unexpected_dirty)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_iq_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_catalog_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"only_expected_files_dirty": not unexpected_dirty},
        "sample": {
            "ai_entry": ai_entry,
            "dashboard_entry": dashboard_entry,
            "health_keys": health_keys,
            "logs_keys": logs_keys,
        },
        "dirty_lines": dirty_lines,
        "unexpected_dirty": unexpected_dirty,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_catalog_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
