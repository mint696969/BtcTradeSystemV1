# path: ./tools/test_phase4a_autotrade_milestone_ig_decision_policy_gate_visibility_registry_chain_completion_closeout_review_guard.py
# desc: Guard S170 closeout review remains read-only metadata/status-only with no UI implementation, commands, runtime payload loading, final/chain/status/checkpoint builder execution, decision append, mode apply, grants, writes, or broker behavior.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.ai_operator_display_sources import load_operator_display_sources
from btcts.apps.operator_ui.hub.decision_policy_gate_visibility_registry_chain_completion_closeout_review import (
    CLOSEOUT_CATALOG_SOURCE_KEYS,
    CLOSEOUT_REVIEW_KEY,
    DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CONTRACT,
    build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_registry_chain_completion_closeout_review.py"
GUARD = REPO_ROOT / "tools/test_phase4a_autotrade_milestone_ig_decision_policy_gate_visibility_registry_chain_completion_closeout_review_guard.py"
CLOSE_GUARD = REPO_ROOT / "tools/test_phase4a_autotrade_milestone_ig_decision_policy_gate_visibility_registry_chain_completion_closeout_review_close_guard.py"
RELATED = (
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/ai_operator_display_sources.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_registry_chain_completion_final_status_index.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_registry_chain_completion_final_status_index_registry_visibility.py",
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
    "build_decision_policy_gate_visibility_registry_chain_completion_final_status_index_packet",
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
EXPECTED_CATALOG_SOURCE_KEYS = (
    "autotrade_decision_ledger_policy_gate_display",
    "decision_policy_gate_static_section_model",
    "decision_policy_gate_dashboard_status_index",
    "decision_policy_gate_visibility_chain_summary",
    "decision_policy_gate_visibility_completion_checkpoint",
    "decision_policy_gate_visibility_completion_status_index",
    "decision_policy_gate_visibility_completion_status_index_registry_visibility_chain_completion",
    "decision_policy_gate_visibility_completion_status_index_registry_visibility_chain_completion_final_status_index",
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

    packet = build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_packet()
    runtime_sources = load_operator_display_sources()
    encoded = json.loads(json.dumps(packet, ensure_ascii=False, sort_keys=True))
    catalog_reviews = tuple(packet.get("catalog_reviews") or ())
    dashboard_reviews = tuple(packet.get("dashboard_catalog_reviews") or ())
    checks = {
        "contract_shape": DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CONTRACT["closeout_review_only"] is True and DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CONTRACT["no_command_buttons"] is True,
        "review_key_constant": CLOSEOUT_REVIEW_KEY == "decision_policy_gate_read_only_visibility_registry_chain_completion_closeout_review",
        "catalog_source_keys_constant": CLOSEOUT_CATALOG_SOURCE_KEYS == EXPECTED_CATALOG_SOURCE_KEYS,
        "catalog_source_count": packet["catalog_source_count"] == 8 and len(catalog_reviews) == 8 and len(dashboard_reviews) == 8,
        "all_catalog_entries_available": packet["all_catalog_entries_available"] is True and all(item.get("source_entry_available") is True for item in catalog_reviews),
        "all_dashboard_entries_available": packet["all_dashboard_entries_available"] is True and all(item.get("source_entry_available") is True for item in dashboard_reviews),
        "all_registry_visible": packet["all_health_page_visible"] is True and packet["all_future_widget_page_visible"] is True,
        "all_read_only_contracts": packet["all_read_only_contracts"] is True and all(item.get("read_only_contract") is True for item in catalog_reviews),
        "all_not_runtime_or_ui": packet["all_not_runtime_or_ui"] is True and all(item.get("not_runtime_wiring") is True and item.get("not_ui_rendering") is True for item in catalog_reviews),
        "all_safety_flags_false": packet["all_safety_flags_false"] is True,
        "closeout_review_completed": packet["closeout_review_completed"] is True,
        "final_contract_snapshots_present": packet["final_status_index_contract"].get("final_status_index_only") is True and packet["final_status_index_registry_visibility_contract"].get("final_status_index_visibility_only") is True,
        "does_not_execute_final_status_index_builder": "build_decision_policy_gate_visibility_registry_chain_completion_final_status_index_packet" not in module_text,
        "does_not_execute_chain_completion_builder": "build_decision_policy_gate_visibility_completion_status_index_registry_visibility_chain_completion_packet" not in module_text,
        "runtime_source_not_added": CLOSEOUT_REVIEW_KEY not in runtime_sources and packet["not_loaded_as_runtime_display_source"] is True,
        "summary_line_suffix": str(packet["summary_line"]).endswith("read_only_visibility_registry_chain_completion_closeout_review"),
        "json_safe": encoded["closeout_review_key"] == CLOSEOUT_REVIEW_KEY and encoded["catalog_source_count"] == 8,
        "visibility_flags_false": _all_false(packet),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty_lines = [line for line in proc.stdout.splitlines() if line.strip()]
    allowed_dirty_markers = (
        "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_registry_chain_completion_closeout_review.py",
        "tools/test_phase4a_autotrade_milestone_ig_decision_policy_gate_visibility_registry_chain_completion_closeout_review_guard.py",
        "tools/test_phase4a_autotrade_milestone_ig_decision_policy_gate_visibility_registry_chain_completion_closeout_review_close_guard.py",
    )
    unexpected_dirty = [line for line in dirty_lines if not any(marker in line for marker in allowed_dirty_markers)]
    failures.extend(f"unexpected dirty file during IG: {line}" for line in unexpected_dirty)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_ig_decision_policy_gate_visibility_registry_chain_completion_closeout_review_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"only_expected_files_dirty": not unexpected_dirty},
        "sample": {
            "summary_line": packet.get("summary_line"),
            "catalog_source_keys": packet.get("catalog_source_keys"),
            "runtime_source_keys": tuple(runtime_sources.keys()),
        },
        "dirty_lines": dirty_lines,
        "unexpected_dirty": unexpected_dirty,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_decision_policy_gate_visibility_registry_chain_completion_closeout_review_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
