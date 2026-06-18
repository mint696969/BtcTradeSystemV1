# path: ./tools/test_phase4a_autotrade_milestone_id_decision_policy_gate_visibility_registry_chain_completion_final_status_index_guard.py
# desc: Guard S167 final status index packet remains pure data/status-only with no UI implementation, commands, runtime payload loading, chain/status/checkpoint builder execution, decision append, mode apply, grants, writes, or broker behavior.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.ai_operator_display_sources import load_operator_display_sources
from btcts.apps.operator_ui.hub.decision_policy_gate_visibility_registry_chain_completion_final_status_index import (
    DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_FINAL_STATUS_INDEX_CONTRACT,
    FINAL_COMPONENT_KEY,
    FINAL_STATUS_INDEX_COMPONENT_KEYS,
    FINAL_STATUS_INDEX_KEY,
    build_decision_policy_gate_visibility_registry_chain_completion_final_status_index_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_registry_chain_completion_final_status_index.py"
GUARD = REPO_ROOT / "tools/test_phase4a_autotrade_milestone_id_decision_policy_gate_visibility_registry_chain_completion_final_status_index_guard.py"
CLOSE_GUARD = REPO_ROOT / "tools/test_phase4a_autotrade_milestone_id_decision_policy_gate_visibility_registry_chain_completion_final_status_index_close_guard.py"
RELATED = (
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_registry_chain_completion_registry_visibility.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_completion_status_index_registry_visibility_chain_completion.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/ai_operator_display_sources.py",
)
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
FORBIDDEN_MODULE_TOKENS = (
    "streamlit",
    "st.button",
    "st.checkbox",
    "load_operator_display_sources",
    "build_decision_policy_gate_visibility_completion_status_index_registry_visibility_chain_completion_packet",
    "build_decision_policy_gate_visibility_completion_status_index_packet",
    "build_decision_policy_gate_visibility_completion_checkpoint_packet",
    "build_decision_policy_gate_visibility_chain_summary_packet",
    "build_decision_policy_gate_dashboard_status_index_packet",
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
    "broker_execution_requested",
    "mode_apply_requested",
    "command_ledger_append_requested",
    "approval_append_requested",
)
EXPECTED_COMPONENTS = (
    "decision_policy_gate_display_registry_visibility",
    "decision_policy_gate_static_section_registry_visibility",
    "decision_policy_gate_dashboard_status_index_registry_visibility",
    "decision_policy_gate_visibility_chain_summary_registry_visibility",
    "decision_policy_gate_visibility_completion_checkpoint_registry_visibility",
    "decision_policy_gate_visibility_completion_status_index_registry_visibility",
    "decision_policy_gate_visibility_registry_chain_completion_registry_visibility",
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


def _all_false(payload: dict[str, object]) -> bool:
    return all(payload.get(name) is False for name in EXPECTED_FALSE_FLAGS)


def main() -> int:
    failures: list[str] = []
    module_text = MODULE.read_text(encoding="utf-8") if MODULE.exists() else ""
    for target in (MODULE, GUARD, CLOSE_GUARD, *RELATED):
        try:
            compile(target.read_text(encoding="utf-8"), str(target), "exec")
        except Exception as exc:
            failures.append(f"compile failed: {target.relative_to(REPO_ROOT)}: {exc}")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        if any(item == prefix or item.startswith(prefix + ".") for item in imports):
            failures.append(f"forbidden import in {MODULE.relative_to(REPO_ROOT)}: {prefix}")
    for token in FORBIDDEN_MODULE_TOKENS:
        if token in module_text:
            failures.append(f"forbidden token in {MODULE.relative_to(REPO_ROOT)}: {token}")

    packet = build_decision_policy_gate_visibility_registry_chain_completion_final_status_index_packet()
    runtime_sources = load_operator_display_sources()
    encoded = json.loads(json.dumps(packet, ensure_ascii=False, sort_keys=True))
    components = tuple(packet.get("components") or ())
    component_keys = tuple(item.get("component_key") for item in components)
    final_component = components[-1] if components else {}
    checks = {
        "contract_shape": DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_FINAL_STATUS_INDEX_CONTRACT["status_index_only"] is True and DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_FINAL_STATUS_INDEX_CONTRACT["final_status_index_only"] is True,
        "final_status_index_key_constant": FINAL_STATUS_INDEX_KEY == "decision_policy_gate_read_only_visibility_completion_status_index_registry_visibility_chain_completion_final_status_index",
        "component_keys_constant": FINAL_STATUS_INDEX_COMPONENT_KEYS == EXPECTED_COMPONENTS,
        "component_keys_match_packet": component_keys == EXPECTED_COMPONENTS,
        "component_count": packet["component_count"] == 7 and len(components) == 7,
        "final_component_is_registry_chain_completion_registry_visibility": FINAL_COMPONENT_KEY == EXPECTED_COMPONENTS[-1] and packet["final_component_key"] == FINAL_COMPONENT_KEY and final_component.get("is_final_component") is True,
        "final_component_metadata": packet["final_component_source_key"] == "decision_policy_gate_visibility_completion_status_index_registry_visibility_chain_completion" and packet["final_component_visibility_packet_type"] == "decision_policy_gate_visibility_registry_chain_completion_registry_visibility",
        "visibility_flags_false": _all_false(packet),
        "all_components_read_only": all(item.get("read_only_contract") is True and item.get("non_executing") is True and item.get("not_runtime_payload_loading") is True and item.get("not_runtime_wiring") is True and item.get("not_ui_rendering") is True and item.get("no_command_buttons") is True for item in components),
        "all_source_entries_available": packet["all_source_entries_available"] is True and all(item.get("source_entry_available") is True for item in components),
        "all_registry_visible": packet["all_health_page_visible"] is True and packet["all_future_widget_page_visible"] is True,
        "all_not_runtime_loaded": packet["all_not_loaded_as_runtime_display_source"] is True and packet["not_loaded_as_runtime_display_source"] is True,
        "final_status_index_ready": packet["final_status_index_ready"] is True,
        "does_not_execute_chain_completion_builder": "build_decision_policy_gate_visibility_completion_status_index_registry_visibility_chain_completion_packet" not in module_text,
        "does_not_execute_status_index_builder": "build_decision_policy_gate_visibility_completion_status_index_packet" not in module_text,
        "does_not_execute_checkpoint_builder": "build_decision_policy_gate_visibility_completion_checkpoint_packet" not in module_text,
        "final_registry_visibility_contract_present": packet["registry_chain_completion_registry_visibility_contract"].get("registry_chain_completion_visibility_only") is True,
        "summary_line_suffix": str(packet["summary_line"]).endswith("read_only_visibility_registry_chain_completion_final_status_index"),
        "runtime_source_not_added": FINAL_STATUS_INDEX_KEY not in runtime_sources,
        "json_safe": encoded["final_status_index_key"] == FINAL_STATUS_INDEX_KEY and encoded["component_count"] == 7,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty_lines = [line for line in proc.stdout.splitlines() if line.strip()]
    allowed_dirty_markers = (
        "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_registry_chain_completion_final_status_index.py",
        "tools/test_phase4a_autotrade_milestone_id_decision_policy_gate_visibility_registry_chain_completion_final_status_index_guard.py",
        "tools/test_phase4a_autotrade_milestone_id_decision_policy_gate_visibility_registry_chain_completion_final_status_index_close_guard.py",
    )
    unexpected_dirty = [line for line in dirty_lines if not any(marker in line for marker in allowed_dirty_markers)]
    failures.extend(f"unexpected dirty file during ID: {line}" for line in unexpected_dirty)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_id_decision_policy_gate_visibility_registry_chain_completion_final_status_index_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"only_expected_files_dirty": not unexpected_dirty},
        "sample": {
            "packet": packet,
            "runtime_source_keys": tuple(runtime_sources.keys()),
        },
        "dirty_lines": dirty_lines,
        "unexpected_dirty": unexpected_dirty,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_decision_policy_gate_visibility_registry_chain_completion_final_status_index_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
