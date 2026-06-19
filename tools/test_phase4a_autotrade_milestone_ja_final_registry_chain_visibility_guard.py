# path: ./tools/test_phase4a_autotrade_milestone_ja_final_registry_chain_visibility_guard.py
# desc: Guard S190 final registry chain completion registry visibility packet remains metadata-only with no UI implementation, commands, runtime payload loading, builder execution, decision append, mode apply, grants, writes, or broker behavior.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.ai_operator_display_sources import load_operator_display_sources
from btcts.apps.operator_ui.components.operator_display_source_catalog import load_operator_dashboard_display_source_catalog
from btcts.apps.operator_ui.hub.decision_policy_gate_final_registry_chain_visibility import (
    DECISION_POLICY_GATE_FINAL_REGISTRY_CHAIN_COMPLETION_REGISTRY_VISIBILITY_CONTRACT,
    SOURCE_KEY,
    build_decision_policy_gate_final_registry_chain_registry_visibility_packet,
    visible_pages_for_decision_policy_gate_final_registry_chain,
)
from btcts.apps.operator_ui.hub.display_source_registry import (
    display_source_keys_for_page,
    load_dashboard_hub_display_source_registry,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_final_registry_chain_visibility.py"
CATALOG = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/ai_operator_display_sources.py"
EXPECTED_DEPENDENCIES = (
    "decision_policy_gate_read_only_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_final_status_index",
    "decision_policy_gate_read_only_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_final_status_index_registry_visibility",
)
EXPECTED_FALSE_FLAGS = (
    "command_buttons_allowed", "forms_or_toggles_allowed", "runtime_wiring_allowed", "ui_rendering_implementation_allowed", "decision_append_allowed", "decision_ledger_integration_allowed", "live_shadow_behavior_change_allowed", "persist_true_allowed", "would_append_shadow_decision", "would_apply_mode", "would_execute_prearmed_grant", "would_write_runtime_artifact", "would_write_preview_status_artifact", "would_send_to_broker", "broker_execution_requested", "mode_apply_requested", "command_ledger_append_requested", "approval_append_requested",
)
FORBIDDEN_IMPORT_PREFIXES = (
    "streamlit", "btcts.autotrade.live_shadow", "btcts.autotrade.ledger", "btcts.autotrade.execution", "btcts.autotrade.runtime_paths", "btcts.collector_vnext", "requests", "httpx", "ccxt", "pybitflyer", "websocket",
)
FORBIDDEN_MODULE_TOKENS = (
    "streamlit", "st.button", "st.checkbox", "load_operator_display_sources",
    "build_decision_policy_gate_chain_completion_final_status_index_registry_visibility_chain_completion_packet(",
    "build_decision_policy_gate_chain_completion_final_status_index_registry_visibility_packet(",
    "build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_final_status_index_packet(",
    "build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_packet(",
    "build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_packet(",
    "build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_summary_packet(",
    "build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_final_status_index_packet(",
    "build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_packet(",
    "build_decision_policy_gate_visibility_registry_chain_completion_final_status_index_packet(",
    "build_decision_policy_gate_visibility_completion_status_index_registry_visibility_chain_completion_packet(",
    "build_decision_policy_gate_visibility_completion_status_index_packet(",
    "build_decision_policy_gate_visibility_completion_checkpoint_packet(",
    "append_decision_jsonl", "run_shadow_decision_from_snapshot", "run_latest_market_state_shadow_decision", "build_action_candidate", "build_shadow_decision_record", "decision_ledger_path", "default_shadow_decision_ledger_path", "persist=True", "persist: bool = True", "validate_and_append_command", "submit_mode_change_command_request", "mkdir(", "write_text(", ".write(", "open(", "append_jsonl(", "json.dump", "place_order(", "send_order(", "create_order(", "requests.get", "requests.post", "httpx.get", "httpx.post", "command_buttons_allowed=True", "forms_or_toggles_allowed=True", "runtime_wiring_allowed=True", "ui_rendering_implementation_allowed=True", "decision_append_allowed=True", "decision_ledger_integration_allowed=True", "live_shadow_behavior_change_allowed=True", "persist_true_allowed=True", "would_append_shadow_decision=True", "would_apply_mode=True", "would_execute_prearmed_grant=True", "would_write_runtime_artifact=True", "would_write_preview_status_artifact=True", "would_send_to_broker=True",
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
    for target in (MODULE, CATALOG):
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

    catalog = load_operator_dashboard_display_source_catalog()
    registry = load_dashboard_hub_display_source_registry()
    packet = build_decision_policy_gate_final_registry_chain_registry_visibility_packet(catalog, registry)
    packet_default = build_decision_policy_gate_final_registry_chain_registry_visibility_packet()
    visible_pages = visible_pages_for_decision_policy_gate_final_registry_chain(registry)
    runtime_sources = load_operator_display_sources()
    encoded = json.loads(json.dumps(packet, ensure_ascii=False, sort_keys=True))
    page_visibility = tuple(packet.get("page_visibility") or ())
    checks = {
        "contract_shape": DECISION_POLICY_GATE_FINAL_REGISTRY_CHAIN_COMPLETION_REGISTRY_VISIBILITY_CONTRACT["catalog_metadata_only"] is True and DECISION_POLICY_GATE_FINAL_REGISTRY_CHAIN_COMPLETION_REGISTRY_VISIBILITY_CONTRACT["chain_completion_visibility_only"] is True,
        "source_key_constant": SOURCE_KEY == "decision_policy_gate_read_only_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_final_status_index_registry_visibility_chain_completion",
        "source_entry_available": packet["source_entry_available"] is True,
        "entry_references_chain_completion": packet["chain_completion_module"] == "btcts.apps.operator_ui.hub.decision_policy_gate_chain_completion_final_registry_chain" and packet["chain_completion_builder"] == "build_decision_policy_gate_chain_completion_final_status_index_registry_visibility_chain_completion_packet",
        "entry_dependencies": tuple(packet.get("source_dependencies") or ()) == EXPECTED_DEPENDENCIES,
        "entry_metadata_only": packet["source_entry"].get("data_model_only") is True and packet["source_entry"].get("chain_completion_only") is True and packet["source_entry"].get("registry_visibility_chain_completion_only") is True and packet["source_entry"].get("not_runtime_payload_loading") is True,
        "visibility_flags_false": _all_false(packet),
        "chain_completion_contract_visible": packet["chain_completion_contract"].get("chain_completion_only") is True and packet["chain_completion_contract"].get("no_command_buttons") is True,
        "does_not_execute_chain_completion_builder": "build_decision_policy_gate_chain_completion_final_status_index_registry_visibility_chain_completion_packet(" not in module_text,
        "does_not_execute_registry_visibility_builder": "build_decision_policy_gate_chain_completion_final_status_index_registry_visibility_packet(" not in module_text,
        "does_not_execute_final_status_index_builder": "build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_final_status_index_packet(" not in module_text,
        "health_page_visible": packet["health_page_visible"] is True and SOURCE_KEY in display_source_keys_for_page("health", registry),
        "future_widget_page_visible": packet["future_widget_page_visible"] is True and SOURCE_KEY in display_source_keys_for_page("logs", registry),
        "visible_pages_helper_matches_packet": tuple(packet["visible_pages"]) == visible_pages,
        "page_visibility_is_read_only": all(item.get("read_only_contract") is True and item.get("not_runtime_payload_loading") is True and item.get("no_command_buttons") is True for item in page_visibility),
        "not_runtime_loaded": SOURCE_KEY not in runtime_sources and packet["not_loaded_as_runtime_display_source"] is True,
        "default_build_matches": packet_default["source_entry_available"] is True and packet_default["health_page_visible"] is True,
        "json_safe": encoded["source_key"] == SOURCE_KEY and encoded["visible_page_count"] == packet["visible_page_count"],
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty_lines = [line for line in proc.stdout.splitlines() if line.strip()]
    allowed_dirty_markers = (
        "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_final_registry_chain_visibility.py",
        "tools/test_phase4a_autotrade_milestone_ja_final_registry_chain_visibility_guard.py",
        "tools/test_phase4a_autotrade_milestone_ja_final_registry_chain_visibility_close_guard.py",
    )
    unexpected_dirty = [line for line in dirty_lines if not any(marker in line for marker in allowed_dirty_markers)]
    failures.extend(f"unexpected dirty file during JA: {line}" for line in unexpected_dirty)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_ja_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_final_status_index_registry_visibility_chain_completion_registry_visibility_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"only_expected_files_dirty": not unexpected_dirty},
        "sample": {"visible_pages": visible_pages, "runtime_source_keys": tuple(runtime_sources.keys()), "source_entry": packet.get("source_entry")},
        "dirty_lines": dirty_lines,
        "unexpected_dirty": unexpected_dirty,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_s190_final_registry_chain_visibility_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
