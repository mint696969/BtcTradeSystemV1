# path: ./tools/test_phase4a_autotrade_milestone_hk_decision_policy_gate_rendering_stub_policy_gate_guard.py
# desc: Guard S148 rendering stub policy gate remains policy/status-only with no Streamlit rendering, commands, runtime wiring, decision append, mode apply, grants, writes, or broker behavior.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.hub.decision_policy_gate_rendering_stub_policy_gate import (
    NON_PERMISSIONS,
    REQUIRED_PLAN_REFERENCES,
    SAFE_FIELD_GROUPS,
    build_decision_policy_gate_rendering_stub_policy_gate,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_visibility import (
    build_decision_policy_gate_dashboard_registry_visibility_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_rendering_stub_policy_gate.py"
VISIBILITY = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility.py"
PLAN = REPO_ROOT / "docs/architecture/OPERATOR_UI_DECISION_POLICY_GATE_READ_ONLY_RENDERING_PLAN_2026-06-18.md"
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
    "rendering_stub_allowed=True",
    "ui_rendering_implementation_allowed=True",
    "command_buttons_allowed=True",
    "forms_or_toggles_allowed=True",
    "runtime_wiring_allowed=True",
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
    "rendering_stub_allowed",
    "ui_rendering_implementation_allowed",
    "command_buttons_allowed",
    "forms_or_toggles_allowed",
    "runtime_wiring_allowed",
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
    text = MODULE.read_text(encoding="utf-8") if MODULE.exists() else ""
    if not MODULE.exists():
        failures.append("missing S148 rendering stub policy gate module")
    try:
        compile(text, str(MODULE), "exec")
    except Exception as exc:
        failures.append(f"compile failed: {MODULE.relative_to(REPO_ROOT)}: {exc}")
    if MODULE.exists():
        imports = _imports_from(MODULE)
        for prefix in FORBIDDEN_IMPORT_PREFIXES:
            if any(item == prefix or item.startswith(prefix + ".") for item in imports):
                failures.append(f"forbidden import in {MODULE.relative_to(REPO_ROOT)}: {prefix}")
        for token in FORBIDDEN_TOKENS:
            if token in text:
                failures.append(f"forbidden token in {MODULE.relative_to(REPO_ROOT)}: {token}")

    visibility_packet = build_decision_policy_gate_dashboard_registry_visibility_packet()
    default_gate = build_decision_policy_gate_rendering_stub_policy_gate(visibility_packet)
    acknowledged_gate = build_decision_policy_gate_rendering_stub_policy_gate(
        visibility_packet,
        rendering_plan_acknowledged=True,
    )
    requested_gate = build_decision_policy_gate_rendering_stub_policy_gate(
        visibility_packet,
        rendering_plan_acknowledged=True,
        static_read_only_stub_requested=True,
    )
    missing_gate = build_decision_policy_gate_rendering_stub_policy_gate({})
    default_payload = default_gate.to_dict()
    acknowledged_payload = acknowledged_gate.to_dict()
    requested_payload = requested_gate.to_dict()
    missing_payload = missing_gate.to_dict()
    encoded = json.loads(json.dumps(default_payload, ensure_ascii=False, sort_keys=True))

    checks = {
        "plan_doc_present": PLAN.exists(),
        "module_present": MODULE.exists(),
        "required_plan_references_visible": len(REQUIRED_PLAN_REFERENCES) == 3 and any("RENDERING_PLAN" in item or "READ_ONLY_RENDERING_PLAN" in item for item in REQUIRED_PLAN_REFERENCES),
        "safe_field_groups_visible": "required_approvals" in SAFE_FIELD_GROUPS and "registry_visibility" in SAFE_FIELD_GROUPS,
        "non_permissions_visible": "no_ui_rendering_implementation_in_s148" in NON_PERMISSIONS and "no_command_buttons_in_s148" in NON_PERMISSIONS,
        "default_gate_blocks_without_plan_ack": default_payload["gate_state"] == "blocked" and "rendering_plan_acknowledgement_missing" in default_payload["blockers"],
        "acknowledged_gate_still_policy_only": acknowledged_payload["gate_state"] == "blocked" and acknowledged_payload["rendering_plan_acknowledged"] is True and acknowledged_payload["rendering_stub_allowed"] is False,
        "requested_gate_blocks_stub_request": "static_read_only_stub_request_not_authorized_in_s148" in requested_payload["blockers"],
        "missing_visibility_blocks": "visibility_packet_missing" in missing_payload["blockers"],
        "visibility_packet_seen": acknowledged_payload["source_entry_available"] is True and acknowledged_payload["health_page_visible"] is True,
        "all_false_default": _all_false(default_payload),
        "all_false_acknowledged": _all_false(acknowledged_payload),
        "all_false_requested": _all_false(requested_payload),
        "read_only_non_executing": acknowledged_payload["read_only"] is True and acknowledged_payload["non_executing"] is True and acknowledged_payload["not_runtime_wiring"] is True and acknowledged_payload["not_ui_rendering"] is True,
        "json_safe": encoded["logic_version"].endswith("s148.v1") and encoded["rendering_stub_allowed"] is False,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty_lines = [line for line in proc.stdout.splitlines() if line.strip()]
    allowed_dirty_markers = (
        "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_rendering_stub_policy_gate.py",
        "tools/test_phase4a_autotrade_milestone_hk_decision_policy_gate_rendering_stub_policy_gate_guard.py",
        "tools/test_phase4a_autotrade_milestone_hk_decision_policy_gate_rendering_stub_policy_gate_close_guard.py",
    )
    unexpected_dirty = [line for line in dirty_lines if not any(marker in line for marker in allowed_dirty_markers)]
    failures.extend(f"unexpected dirty file during HK: {line}" for line in unexpected_dirty)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_hk_decision_policy_gate_rendering_stub_policy_gate_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"only_expected_files_dirty": not unexpected_dirty},
        "sample": {
            "default_gate": default_payload,
            "acknowledged_gate": acknowledged_payload,
            "requested_gate": requested_payload,
            "missing_gate": missing_payload,
        },
        "dirty_lines": dirty_lines,
        "unexpected_dirty": unexpected_dirty,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_decision_policy_gate_rendering_stub_policy_gate_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
