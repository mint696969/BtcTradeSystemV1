# path: ./tools/test_phase4a_autotrade_milestone_iv_chain_completion_final_status_guard.py
# desc: Guard S185 chain completion final status index packet remains metadata/status-only with no UI implementation, commands, runtime payload loading, chain-completion/final/closeout/chain/status/checkpoint builder execution, decision append, mode apply, grants, writes, or broker behavior.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.ai_operator_display_sources import load_operator_display_sources
from btcts.apps.operator_ui.hub.decision_policy_gate_chain_completion_final_status_index import (
    CHAIN_COMPLETION_FINAL_STATUS_INDEX_COMPONENT_KEYS,
    CHAIN_COMPLETION_FINAL_STATUS_INDEX_KEY,
    DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CHAIN_CLOSEOUT_FINAL_STATUS_INDEX_REGISTRY_VISIBILITY_CHAIN_COMPLETION_FINAL_STATUS_INDEX_CONTRACT,
    build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_final_status_index_packet,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_registry_visibility import (
    build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_registry_visibility_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_chain_completion_final_status_index.py"
REGISTRY_VISIBILITY = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_registry_visibility.py"
FORBIDDEN_IMPORT_PREFIXES = (
    "streamlit", "btcts.autotrade.live_shadow", "btcts.autotrade.ledger", "btcts.autotrade.execution", "btcts.autotrade.runtime_paths", "btcts.collector_vnext", "requests", "httpx", "ccxt", "pybitflyer", "websocket",
)
FORBIDDEN_MODULE_TOKENS = (
    "streamlit", "st.button", "st.checkbox", "load_operator_display_sources",
    "build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_packet",
    "build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_packet",
    "build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_summary_packet",
    "build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_final_status_index_packet",
    "build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_packet",
    "build_decision_policy_gate_visibility_registry_chain_completion_final_status_index_packet",
    "build_decision_policy_gate_visibility_completion_status_index_registry_visibility_chain_completion_packet",
    "build_decision_policy_gate_visibility_completion_status_index_packet",
    "build_decision_policy_gate_visibility_completion_checkpoint_packet",
    "append_decision_jsonl", "run_shadow_decision_from_snapshot", "run_latest_market_state_shadow_decision", "build_action_candidate", "build_shadow_decision_record", "decision_ledger_path", "default_shadow_decision_ledger_path", "persist=True", "persist: bool = True", "validate_and_append_command", "submit_mode_change_command_request", "mkdir(", "write_text(", ".write(", "open(", "append_jsonl(", "json.dump", "place_order(", "send_order(", "create_order(", "requests.get", "requests.post", "httpx.get", "httpx.post", "command_buttons_allowed=True", "forms_or_toggles_allowed=True", "runtime_wiring_allowed=True", "ui_rendering_implementation_allowed=True", "decision_append_allowed=True", "decision_ledger_integration_allowed=True", "live_shadow_behavior_change_allowed=True", "persist_true_allowed=True", "would_append_shadow_decision=True", "would_apply_mode=True", "would_execute_prearmed_grant=True", "would_write_runtime_artifact=True", "would_write_preview_status_artifact=True", "would_send_to_broker=True",
)
EXPECTED_COMPONENT_KEYS = (
    "decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion",
    "decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_registry_visibility",
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


def main() -> int:
    failures: list[str] = []
    module_text = MODULE.read_text(encoding="utf-8") if MODULE.exists() else ""
    for target in (MODULE, REGISTRY_VISIBILITY):
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

    registry_visibility_packet = build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_registry_visibility_packet()
    packet = build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_final_status_index_packet(registry_visibility_packet)
    packet_default = build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_final_status_index_packet()
    runtime_sources = load_operator_display_sources()
    encoded = json.loads(json.dumps(packet, ensure_ascii=False, sort_keys=True))
    components = tuple(packet.get("components") or ())
    checks = {
        "contract_shape": DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CHAIN_CLOSEOUT_FINAL_STATUS_INDEX_REGISTRY_VISIBILITY_CHAIN_COMPLETION_FINAL_STATUS_INDEX_CONTRACT["final_status_index_only"] is True and DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CHAIN_CLOSEOUT_FINAL_STATUS_INDEX_REGISTRY_VISIBILITY_CHAIN_COMPLETION_FINAL_STATUS_INDEX_CONTRACT["chain_completion_final_status_index_only"] is True,
        "key_constant": CHAIN_COMPLETION_FINAL_STATUS_INDEX_KEY == "decision_policy_gate_read_only_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_final_status_index",
        "component_keys": CHAIN_COMPLETION_FINAL_STATUS_INDEX_COMPONENT_KEYS == EXPECTED_COMPONENT_KEYS and tuple(packet["final_status_index_components"]) == EXPECTED_COMPONENT_KEYS,
        "component_count": packet["component_count"] == 2 and len(components) == 2,
        "final_component_is_registry_visibility": packet["final_component_key"] == EXPECTED_COMPONENT_KEYS[-1] and packet["final_component_visibility_packet_type"] == EXPECTED_COMPONENT_KEYS[-1],
        "components_ready": all(item.get("ready_for_chain_completion_final_status_index") is True for item in components),
        "chain_completion_metadata_component": components[0].get("source_key") == EXPECTED_COMPONENT_KEYS[0] and components[0].get("chain_completion_builder") == "build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_packet",
        "registry_visibility_component": components[1].get("source_key") == EXPECTED_COMPONENT_KEYS[0] and components[1].get("visibility_packet_type") == EXPECTED_COMPONENT_KEYS[1],
        "final_status_index_ready": packet["chain_completion_final_status_index_ready"] is True,
        "all_visibility_true": packet["all_health_page_visible"] is True and packet["all_future_widget_page_visible"] is True and packet["all_not_loaded_as_runtime_display_source"] is True,
        "all_safety_flags_false": packet["all_safety_flags_false"] is True,
        "contract_snapshots_present": packet["chain_completion_contract"].get("chain_completion_only") is True and packet["chain_completion_registry_visibility_contract"].get("chain_completion_visibility_only") is True,
        "does_not_execute_chain_completion_builder": "build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_packet" not in module_text,
        "does_not_execute_chain_closeout_final_status_index_builder": "build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_packet" not in module_text,
        "does_not_execute_closeout_review_builder": "build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_packet" not in module_text,
        "not_runtime_loaded": CHAIN_COMPLETION_FINAL_STATUS_INDEX_KEY not in runtime_sources and packet["not_loaded_as_runtime_display_source"] is True,
        "default_build_matches": packet_default["chain_completion_final_status_index_ready"] is True and packet_default["component_count"] == 2,
        "summary_line_suffix": str(packet["summary_line"]).endswith("read_only_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_final_status_index"),
        "json_safe": encoded["final_status_index_key"] == CHAIN_COMPLETION_FINAL_STATUS_INDEX_KEY and encoded["component_count"] == 2,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty_lines = [line for line in proc.stdout.splitlines() if line.strip()]
    allowed_dirty_markers = (
        "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_chain_completion_final_status_index.py",
        "tools/test_phase4a_autotrade_milestone_iv_chain_completion_final_status_guard.py",
        "tools/test_phase4a_autotrade_milestone_iv_chain_completion_final_status_close_guard.py",
    )
    unexpected_dirty = [line for line in dirty_lines if not any(marker in line for marker in allowed_dirty_markers)]
    failures.extend(f"unexpected dirty file during IV: {line}" for line in unexpected_dirty)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_iv_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_final_status_index_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"only_expected_files_dirty": not unexpected_dirty},
        "sample": {"summary_line": packet.get("summary_line"), "component_keys": packet.get("final_status_index_components"), "runtime_source_keys": tuple(runtime_sources.keys())},
        "dirty_lines": dirty_lines,
        "unexpected_dirty": unexpected_dirty,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_s185_final_status_index_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
