# path: ./tools/test_phase4a_autotrade_milestone_hu_decision_policy_gate_visibility_completion_checkpoint_guard.py
# desc: Guard S158 visibility completion checkpoint remains pure data/status-only with no UI implementation, commands, runtime payload loading, decision append, mode apply, grants, writes, or broker behavior.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.ai_operator_display_sources import load_operator_display_sources
from btcts.apps.operator_ui.hub.decision_policy_gate_visibility_completion_checkpoint import (
    CHECKPOINT_COMPONENT_KEYS,
    CHECKPOINT_KEY,
    DECISION_POLICY_GATE_VISIBILITY_COMPLETION_CHECKPOINT_CONTRACT,
    build_decision_policy_gate_visibility_completion_checkpoint_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_completion_checkpoint.py"
RELATED = (
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_chain_summary_registry_visibility.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_chain_summary.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_dashboard_status_index_registry_visibility.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_dashboard_status_index.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_static_section_registry_visibility.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility.py",
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
RUNTIME_FORBIDDEN_SOURCE_KEYS = (
    "autotrade_decision_ledger_policy_gate_display",
    "decision_policy_gate_static_section_model",
    "decision_policy_gate_dashboard_status_index",
    "decision_policy_gate_visibility_chain_summary",
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

    packet = build_decision_policy_gate_visibility_completion_checkpoint_packet()
    encoded = json.loads(json.dumps(packet, ensure_ascii=False, sort_keys=True))
    components = tuple(packet.get("components") or ())
    component_keys = tuple(item.get("component_key") for item in components)
    runtime_sources = load_operator_display_sources()
    checks = {
        "contract_shape": DECISION_POLICY_GATE_VISIBILITY_COMPLETION_CHECKPOINT_CONTRACT["checkpoint_only"] is True and DECISION_POLICY_GATE_VISIBILITY_COMPLETION_CHECKPOINT_CONTRACT["visibility_completion_checkpoint_only"] is True,
        "checkpoint_key_constant": CHECKPOINT_KEY == "decision_policy_gate_read_only_visibility_completion_checkpoint",
        "checkpoint_components_declared": tuple(CHECKPOINT_COMPONENT_KEYS) == component_keys,
        "packet_is_data_only": packet["data_model_only"] is True and packet["not_ui_rendering"] is True and packet["not_runtime_payload_loading"] is True,
        "packet_flags_false": _all_false(packet),
        "components_present": packet["component_count"] == 4 and len(components) == 4,
        "components_complete": all(item.get("complete_for_read_only_visibility") is True for item in components),
        "components_read_only": all(item.get("read_only_contract") is True and item.get("not_runtime_payload_loading") is True and item.get("no_command_buttons") is True for item in components),
        "completion_ready": packet["read_only_visibility_completion_ready"] is True and packet["all_source_entries_available"] is True,
        "visible_pages_present": packet["health_page_visible"] is True and packet["future_widget_page_visible"] is True and packet["visible_page_count"] >= 1,
        "contract_snapshots_present": packet["display_packet_contract"]["read_only_contract"] is True and packet["dashboard_status_index_contract"]["status_index_only"] is True and packet["visibility_chain_summary_contract"]["summary_only"] is True,
        "registry_contract_snapshots_present": packet["display_registry_visibility_contract"]["read_only_contract"] is True and packet["dashboard_status_index_registry_visibility_contract"]["status_index_visibility_only"] is True and packet["visibility_chain_summary_registry_visibility_contract"]["visibility_summary_visibility_only"] is True,
        "not_runtime_loaded": all(key not in runtime_sources for key in RUNTIME_FORBIDDEN_SOURCE_KEYS) and packet["not_loaded_as_runtime_display_source"] is True,
        "summary_line_safe": packet["summary_line"].endswith("read_only_visibility_completion_checkpoint") and "components=4" in packet["summary_line"],
        "json_safe": encoded["checkpoint_key"] == CHECKPOINT_KEY and encoded["component_count"] == 4,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty_lines = [line for line in proc.stdout.splitlines() if line.strip()]
    allowed_dirty_markers = (
        "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_completion_checkpoint.py",
        "tools/test_phase4a_autotrade_milestone_hu_decision_policy_gate_visibility_completion_checkpoint_guard.py",
        "tools/test_phase4a_autotrade_milestone_hu_decision_policy_gate_visibility_completion_checkpoint_close_guard.py",
    )
    unexpected_dirty = [line for line in dirty_lines if not any(marker in line for marker in allowed_dirty_markers)]
    failures.extend(f"unexpected dirty file during HU: {line}" for line in unexpected_dirty)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_hu_decision_policy_gate_visibility_completion_checkpoint_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"only_expected_files_dirty": not unexpected_dirty},
        "sample": {"packet": packet, "runtime_source_keys": tuple(runtime_sources.keys())},
        "dirty_lines": dirty_lines,
        "unexpected_dirty": unexpected_dirty,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_decision_policy_gate_visibility_completion_checkpoint_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
