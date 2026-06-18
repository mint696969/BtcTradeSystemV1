# path: ./tools/test_phase4a_autotrade_milestone_hg_decision_ledger_policy_gate_display_guard.py
# desc: Guard S144 Operator/UI decision ledger policy gate display packet remains read-only/display-only with no rendering, commands, runtime wiring, decision append, mode apply, grants, writes, or broker behavior.

from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.autotrade_decision_ledger_policy_gate_display import (
    AUTOTRADE_DECISION_LEDGER_POLICY_GATE_DISPLAY_CONTRACT,
    build_autotrade_decision_ledger_policy_gate_display_packet,
    decision_ledger_policy_gate_compact_line,
    decision_ledger_policy_gate_snapshot_lines,
)
from btcts.autotrade.decision_ledger_policy_gate import build_decision_ledger_integration_policy_gate
from btcts.autotrade.prediction_preview_artifact_preflight import build_prediction_preview_artifact_preflight
from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus
from btcts.autotrade.shadow_prediction_context import build_autotrade_shadow_prediction_context

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/autotrade_decision_ledger_policy_gate_display.py"
LIVE_SHADOW = REPO_ROOT / "btcts_next/src/btcts/autotrade/live_shadow.py"
FORBIDDEN_IMPORT_PREFIXES = (
    "streamlit",
    "btcts.apps.operator_ui.views",
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
    '"broker_execution_requested": True',
    '"mode_apply_requested": True',
    '"command_ledger_append_requested": True',
    '"approval_append_requested": True',
)
EXPECTED_FALSE_FLAGS = (
    "decision_ledger_integration_allowed",
    "decision_append_allowed",
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


def _status() -> AutoTradePredictionPreviewStatus:
    return AutoTradePredictionPreviewStatus(
        status_id="status_s144_unit",
        generated_at="2026-06-18T00:00:00Z",
        status_state="ok",
        preview_id="preview_s144_unit",
        readiness_id="readiness_s144_unit",
        readiness_state="ready",
        intended_mode="ARMED_DRY_RUN",
        preview_action="WATCH_LONG",
        preview_bias="long",
        preview_confidence="medium",
        validation_state="ok",
        average_score=0.9,
        label_hit_rate=0.83,
    )


def _gate(*, acknowledged: bool = False, approved: bool = False):
    now = datetime(2026, 6, 18, 0, 5, 0, tzinfo=timezone.utc)
    status = _status()
    context = build_autotrade_shadow_prediction_context(status, now=now)
    preflight = build_prediction_preview_artifact_preflight(status, context, artifact_path="artifacts/s144.json", now=now)
    return build_decision_ledger_integration_policy_gate(
        preflight,
        context,
        operator_policy_acknowledged=acknowledged,
        explicit_operator_approval=approved,
        now=now,
    )


def _all_false(payload: dict[str, object]) -> bool:
    return all(payload.get(name) is False for name in EXPECTED_FALSE_FLAGS)


def main() -> int:
    failures: list[str] = []
    text = MODULE.read_text(encoding="utf-8") if MODULE.exists() else ""
    if not MODULE.exists():
        failures.append("missing decision ledger policy gate display module")
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

    default_gate = _gate()
    acknowledged_gate = _gate(acknowledged=True, approved=True)
    default_packet = build_autotrade_decision_ledger_policy_gate_display_packet(default_gate)
    acknowledged_packet = build_autotrade_decision_ledger_policy_gate_display_packet(acknowledged_gate.to_dict())
    unavailable_packet = build_autotrade_decision_ledger_policy_gate_display_packet(None)
    compact_line = decision_ledger_policy_gate_compact_line(default_gate)
    snapshot_lines = decision_ledger_policy_gate_snapshot_lines(default_gate)
    encoded = json.loads(json.dumps(default_packet, ensure_ascii=False, sort_keys=True))

    live_shadow_text = LIVE_SHADOW.read_text(encoding="utf-8") if LIVE_SHADOW.exists() else ""
    checks = {
        "contract_shape": AUTOTRADE_DECISION_LEDGER_POLICY_GATE_DISPLAY_CONTRACT["section_type"] == "autotrade_decision_ledger_policy_gate_display_packet" and AUTOTRADE_DECISION_LEDGER_POLICY_GATE_DISPLAY_CONTRACT["not_ui_rendering"] is True,
        "default_display_packet_visible": default_packet["gate_available"] is True and default_packet["display_state"] == "blocked" and "operator_policy_acknowledgement_missing" in default_packet["blockers"],
        "acknowledged_display_packet_visible": acknowledged_packet["gate_available"] is True and acknowledged_packet["operator_policy_acknowledged"] is True and acknowledged_packet["decision_append_allowed"] is False,
        "unavailable_packet_visible": unavailable_packet["gate_available"] is False and unavailable_packet["display_state"] == "unavailable",
        "compact_line_display_only": compact_line.endswith("display_only") and "decision_append_allowed=false" in compact_line,
        "snapshot_lines_include_safety_flags": "read_only_contract=true" in snapshot_lines and "no_command_buttons=true" in snapshot_lines and "would_append_shadow_decision=false" in snapshot_lines,
        "json_safe": encoded["section_type"] == "autotrade_decision_ledger_policy_gate_display_packet" and encoded["decision_append_allowed"] is False,
        "read_only_display_flags": default_packet["read_only_contract"] is True and default_packet["not_runtime_wiring"] is True and default_packet["not_ui_rendering"] is True and default_packet["no_command_buttons"] is True,
        "execution_flags_false_default": _all_false(default_packet),
        "execution_flags_false_acknowledged": _all_false(acknowledged_packet),
        "execution_flags_false_unavailable": _all_false(unavailable_packet),
        "policy_gate_contract_still_present": default_gate.decision_append_allowed is False and default_gate.live_shadow_behavior_change_allowed is False,
        "live_shadow_existing_append_path_only": "append_decision_jsonl" in live_shadow_text and "run_shadow_decision_from_snapshot" in live_shadow_text,
        "new_module_does_not_import_live_shadow": "btcts.autotrade.live_shadow" not in text,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty_lines = [line for line in proc.stdout.splitlines() if line.strip()]
    allowed_dirty_markers = (
        "btcts_next/src/btcts/apps/operator_ui/components/autotrade_decision_ledger_policy_gate_display.py",
        "tools/test_phase4a_autotrade_milestone_hg_decision_ledger_policy_gate_display_guard.py",
        "tools/test_phase4a_autotrade_milestone_hg_decision_ledger_policy_gate_display_close_guard.py",
    )
    unexpected_dirty = [line for line in dirty_lines if not any(marker in line for marker in allowed_dirty_markers)]
    failures.extend(f"unexpected dirty file during HG: {line}" for line in unexpected_dirty)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_hg_decision_ledger_policy_gate_display_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"only_expected_files_dirty": not unexpected_dirty},
        "sample": {
            "default_packet": default_packet,
            "acknowledged_packet": acknowledged_packet,
            "unavailable_packet": unavailable_packet,
        },
        "dirty_lines": dirty_lines,
        "unexpected_dirty": unexpected_dirty,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_decision_ledger_policy_gate_display_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
