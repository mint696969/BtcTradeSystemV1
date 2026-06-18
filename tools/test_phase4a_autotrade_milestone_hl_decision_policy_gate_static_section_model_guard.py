# path: ./tools/test_phase4a_autotrade_milestone_hl_decision_policy_gate_static_section_model_guard.py
# desc: Guard S149 static read-only section model remains pure data only with no UI rendering implementation, commands, runtime wiring, decision append, mode apply, grants, writes, or broker behavior.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.hub.decision_policy_gate_static_section_model import (
    DECISION_POLICY_GATE_STATIC_SECTION_MODEL_CONTRACT,
    SAFE_LABELS,
    build_decision_policy_gate_static_section_model,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_rendering_stub_policy_gate import (
    build_decision_policy_gate_rendering_stub_policy_gate,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_visibility import (
    build_decision_policy_gate_dashboard_registry_visibility_packet,
)
from btcts.apps.operator_ui.components.autotrade_decision_ledger_policy_gate_display import (
    build_autotrade_decision_ledger_policy_gate_display_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_static_section_model.py"
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
    "streamlit",
    "st.button",
    "st.checkbox",
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
        failures.append("missing S149 static section model module")
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

    display = build_autotrade_decision_ledger_policy_gate_display_packet(None)
    visibility = build_decision_policy_gate_dashboard_registry_visibility_packet()
    gate = build_decision_policy_gate_rendering_stub_policy_gate(visibility, rendering_plan_acknowledged=True)
    model = build_decision_policy_gate_static_section_model(display, visibility, gate)
    model_without_inputs = build_decision_policy_gate_static_section_model()
    encoded = json.loads(json.dumps(model, ensure_ascii=False, sort_keys=True))
    row_keys = tuple(row.get("key") for row in model.get("rows") or ())
    row_values = tuple(str(row.get("value")) for row in model.get("rows") or ())

    checks = {
        "contract_shape": DECISION_POLICY_GATE_STATIC_SECTION_MODEL_CONTRACT["data_model_only"] is True and DECISION_POLICY_GATE_STATIC_SECTION_MODEL_CONTRACT["not_ui_rendering"] is True,
        "safe_labels_present": "DECISION APPEND NOT AUTHORIZED" in SAFE_LABELS and "NO COMMAND BUTTONS" in SAFE_LABELS,
        "model_is_static_data_only": model["data_model_only"] is True and model["not_ui_rendering"] is True and model["no_command_buttons"] is True,
        "model_flags_false": _all_false(model),
        "rows_present": model["row_count"] >= 16 and len(model["rows"]) == model["row_count"],
        "rows_are_read_only": all(row.get("read_only") is True and row.get("no_command_buttons") is True for row in model["rows"]),
        "section_contains_core_rows": "gate_state" in row_keys and "decision_append_allowed" in row_keys and "ui_rendering_implementation_allowed" in row_keys,
        "labels_contain_safety_text": any("DECISION APPEND NOT AUTHORIZED" in value for value in row_values),
        "summary_line_static_only": "static_data_only" in model["summary_line"] and "decision_append_allowed=false" in model["summary_line"],
        "default_build_safe": model_without_inputs["visibility_packet_available"] is True and model_without_inputs["stub_policy_gate_available"] is True,
        "json_safe": encoded["section_key"] == "decision_policy_gate_static_read_only_section" and encoded["row_count"] == model["row_count"],
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty_lines = [line for line in proc.stdout.splitlines() if line.strip()]
    allowed_dirty_markers = (
        "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_static_section_model.py",
        "tools/test_phase4a_autotrade_milestone_hl_decision_policy_gate_static_section_model_guard.py",
        "tools/test_phase4a_autotrade_milestone_hl_decision_policy_gate_static_section_model_close_guard.py",
    )
    unexpected_dirty = [line for line in dirty_lines if not any(marker in line for marker in allowed_dirty_markers)]
    failures.extend(f"unexpected dirty file during HL: {line}" for line in unexpected_dirty)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_hl_decision_policy_gate_static_section_model_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"only_expected_files_dirty": not unexpected_dirty},
        "sample": {"model": model, "row_keys": row_keys},
        "dirty_lines": dirty_lines,
        "unexpected_dirty": unexpected_dirty,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_decision_policy_gate_static_section_model_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
