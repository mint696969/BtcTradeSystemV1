# path: ./tools/test_phase4a_autotrade_milestone_hr_decision_policy_gate_visibility_chain_summary_guard.py
# desc: Guard S155 visibility chain summary packet remains pure data with no UI implementation, commands, runtime payload loading, decision append, mode apply, grants, writes, or broker behavior.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.ai_operator_display_sources import load_operator_display_source_catalog, load_operator_display_sources
from btcts.apps.operator_ui.hub.decision_policy_gate_visibility_chain_summary import (
    DECISION_POLICY_GATE_VISIBILITY_CHAIN_SUMMARY_CONTRACT,
    SUMMARY_KEY,
    build_decision_policy_gate_visibility_chain_summary_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_chain_summary.py"
RELATED = (
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_dashboard_status_index_registry_visibility.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_dashboard_status_index.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_static_section_registry_visibility.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility.py",
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
SOURCE_KEYS = (
    "autotrade_decision_ledger_policy_gate_display",
    "decision_policy_gate_static_section_model",
    "decision_policy_gate_dashboard_status_index",
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
    for target in (MODULE, *RELATED):
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

    catalog = load_operator_display_source_catalog()
    runtime_sources = load_operator_display_sources()
    packet = build_decision_policy_gate_visibility_chain_summary_packet(catalog)
    encoded = json.loads(json.dumps(packet, ensure_ascii=False, sort_keys=True))
    chain = tuple(packet.get("chain") or ())
    catalog_keys = tuple(item.get("source_key") for item in catalog if isinstance(item, dict))
    checks = {
        "contract_shape": DECISION_POLICY_GATE_VISIBILITY_CHAIN_SUMMARY_CONTRACT["summary_only"] is True and DECISION_POLICY_GATE_VISIBILITY_CHAIN_SUMMARY_CONTRACT["visibility_summary_only"] is True,
        "summary_key_constant": SUMMARY_KEY == "decision_policy_gate_read_only_visibility_chain_summary",
        "packet_is_data_only": packet["data_model_only"] is True and packet["not_ui_rendering"] is True and packet["not_runtime_payload_loading"] is True,
        "packet_flags_false": _all_false(packet),
        "chain_components_present": packet["chain_component_count"] == 3 and len(chain) == 3,
        "chain_entries_available": all(item.get("catalog_entry_available") is True and item.get("source_entry_available") is True for item in chain),
        "chain_read_only": all(item.get("read_only_contract") is True and item.get("not_runtime_payload_loading") is True and item.get("no_command_buttons") is True for item in chain),
        "catalog_contains_expected_sources": all(key in catalog_keys for key in SOURCE_KEYS),
        "visibility_summary_present": packet["chain_ready_for_read_only_visibility"] is True and packet["health_page_visible"] is True and packet["future_widget_page_visible"] is True and packet["visible_page_count"] >= 1,
        "contracts_embedded": packet["display_packet_contract"]["read_only_contract"] is True and packet["static_section_model_contract"]["data_model_only"] is True and packet["dashboard_status_index_contract"]["status_index_only"] is True,
        "not_runtime_loaded": all(key not in runtime_sources for key in SOURCE_KEYS) and packet["not_loaded_as_runtime_display_source"] is True,
        "summary_line_safe": packet["summary_line"].endswith("read_only_visibility_summary") and "components=3" in packet["summary_line"],
        "json_safe": encoded["summary_key"] == SUMMARY_KEY and encoded["chain_component_count"] == 3,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty_lines = [line for line in proc.stdout.splitlines() if line.strip()]
    allowed_dirty_markers = (
        "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_chain_summary.py",
        "tools/test_phase4a_autotrade_milestone_hr_decision_policy_gate_visibility_chain_summary_guard.py",
        "tools/test_phase4a_autotrade_milestone_hr_decision_policy_gate_visibility_chain_summary_close_guard.py",
    )
    unexpected_dirty = [line for line in dirty_lines if not any(marker in line for marker in allowed_dirty_markers)]
    failures.extend(f"unexpected dirty file during HR: {line}" for line in unexpected_dirty)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_hr_decision_policy_gate_visibility_chain_summary_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"only_expected_files_dirty": not unexpected_dirty},
        "sample": {"packet": packet, "runtime_source_keys": tuple(runtime_sources.keys())},
        "dirty_lines": dirty_lines,
        "unexpected_dirty": unexpected_dirty,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_decision_policy_gate_visibility_chain_summary_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
