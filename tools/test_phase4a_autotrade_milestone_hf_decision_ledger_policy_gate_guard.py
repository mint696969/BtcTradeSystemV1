# path: ./tools/test_phase4a_autotrade_milestone_hf_decision_ledger_policy_gate_guard.py
# desc: Guard S143 decision ledger integration policy gate remains read-only/status-only and does not authorize decision append, live_shadow changes, persist=True path, mode apply, grants, or broker behavior.

from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.autotrade.decision_ledger_policy_gate import (
    AutoTradeDecisionLedgerIntegrationPolicyGate,
    build_decision_ledger_integration_policy_gate,
)
from btcts.autotrade.prediction_preview_artifact_preflight import build_prediction_preview_artifact_preflight
from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus
from btcts.autotrade.shadow_prediction_context import build_autotrade_shadow_prediction_context

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/autotrade/decision_ledger_policy_gate.py"
INIT_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/__init__.py"
LIVE_SHADOW = REPO_ROOT / "btcts_next/src/btcts/autotrade/live_shadow.py"
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.autotrade.live_shadow",
    "btcts.autotrade.ledger",
    "btcts.autotrade.execution",
    "btcts.autotrade.runtime_paths",
    "btcts.autotrade.strategy",
    "btcts.autotrade.risk",
    "btcts.collector_vnext",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
    "websocket",
    "streamlit",
)
FORBIDDEN_TOKENS = (
    "append_decision_jsonl(",
    "run_shadow_decision_from_snapshot(",
    "run_latest_market_state_shadow_decision(",
    "build_action_candidate(",
    "build_shadow_decision_record(",
    "decision_ledger_path(",
    "default_shadow_decision_ledger_path(",
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
    "decision_ledger_integration_allowed=True",
    "decision_append_allowed=True",
    "live_shadow_behavior_change_allowed=True",
    "persist_true_allowed=True",
    "would_append_shadow_decision=True",
    "would_apply_mode=True",
    "would_execute_prearmed_grant=True",
    "would_write_runtime_artifact=True",
    "would_write_preview_status_artifact=True",
    "would_send_to_broker=True",
    "broker_execution_requested=True",
    "mode_apply_requested=True",
    "command_ledger_append_requested=True",
    "approval_append_requested=True",
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


def _status(*, state="ok") -> AutoTradePredictionPreviewStatus:
    return AutoTradePredictionPreviewStatus(
        status_id="status_s143_unit",
        generated_at="2026-06-18T00:00:00Z",
        status_state=state,
        preview_id="preview_s143_unit",
        readiness_id="readiness_s143_unit",
        readiness_state="ready" if state == "ok" else state,
        intended_mode="ARMED_DRY_RUN",
        preview_action="WATCH_LONG",
        preview_bias="long",
        preview_confidence="medium",
        validation_state="ok",
        average_score=0.9,
        label_hit_rate=0.83,
    )


def _ready_preflight(now: datetime):
    status = _status()
    context = build_autotrade_shadow_prediction_context(status, now=now)
    preflight = build_prediction_preview_artifact_preflight(status, context, artifact_path="artifacts/s143_preflight.json", now=now)
    return status, context, preflight


def _all_false(payload: dict[str, object]) -> bool:
    return all(payload.get(name) is False for name in EXPECTED_FALSE_FLAGS)


def main() -> int:
    failures: list[str] = []
    if not MODULE.exists():
        failures.append("missing decision_ledger_policy_gate module")
    text = MODULE.read_text(encoding="utf-8") if MODULE.exists() else ""
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

    now = datetime(2026, 6, 18, 0, 5, 0, tzinfo=timezone.utc)
    _status_obj, context, preflight = _ready_preflight(now)
    default_gate = build_decision_ledger_integration_policy_gate(preflight, context, now=now)
    acknowledged_gate = build_decision_ledger_integration_policy_gate(
        preflight,
        context,
        operator_policy_acknowledged=True,
        explicit_operator_approval=True,
        now=now,
    )
    missing_gate = build_decision_ledger_integration_policy_gate(None, None, now=now)
    blocked_preflight = build_prediction_preview_artifact_preflight(_status(state="blocked"), context, artifact_path="artifacts/blocked.json", now=now)
    blocked_gate = build_decision_ledger_integration_policy_gate(blocked_preflight, context, now=now)
    dict_gate = build_decision_ledger_integration_policy_gate(preflight.to_dict(), context.to_dict(), now=now)

    default_payload = default_gate.to_dict()
    acknowledged_payload = acknowledged_gate.to_dict()
    missing_payload = missing_gate.to_dict()
    blocked_payload = blocked_gate.to_dict()
    dict_payload = dict_gate.to_dict()
    encoded = json.loads(json.dumps(default_payload, ensure_ascii=False, sort_keys=True))

    live_shadow_text = LIVE_SHADOW.read_text(encoding="utf-8") if LIVE_SHADOW.exists() else ""
    checks = {
        "module_present_and_exported": "AutoTradeDecisionLedgerIntegrationPolicyGate" in text and "build_decision_ledger_integration_policy_gate" in text and "decision_ledger_policy_gate" in INIT_FILE.read_text(encoding="utf-8"),
        "exports_available": AutoTradeDecisionLedgerIntegrationPolicyGate is not None and build_decision_ledger_integration_policy_gate is not None,
        "default_gate_blocks_without_operator_approval": default_gate.gate_state == "blocked" and "operator_policy_acknowledgement_missing" in default_gate.blockers and "explicit_operator_approval_missing" in default_gate.blockers,
        "acknowledged_gate_still_policy_only": acknowledged_gate.gate_state == "blocked" and acknowledged_payload["policy_gate_only"] is True and acknowledged_payload["decision_append_allowed"] is False,
        "missing_preflight_blocks": missing_gate.gate_state == "blocked" and "artifact_preflight_missing" in missing_gate.blockers,
        "blocked_preflight_blocks": blocked_gate.gate_state == "blocked" and "artifact_preflight_not_ready" in blocked_gate.blockers,
        "mapping_input_supported": dict_gate.gate_state == "blocked" and dict_payload["source_preflight_id"] == preflight.preflight_id,
        "required_approvals_visible": "operator_explicit_policy_rescope" in default_gate.required_approvals and "explicit_diff_review_guard" in default_gate.required_guards,
        "non_permissions_visible": "no_decision_append_in_s143" in default_gate.non_permissions and "no_persist_true_path_in_s143" in default_gate.non_permissions,
        "json_safe": encoded["logic_version"] == "autotrade_decision_ledger_policy_gate.s143.v1" and encoded["closed"] is True,
        "execution_flags_false_default": _all_false(default_payload),
        "execution_flags_false_acknowledged": _all_false(acknowledged_payload),
        "execution_flags_false_missing": _all_false(missing_payload),
        "execution_flags_false_blocked": _all_false(blocked_payload),
        "read_only_non_executing": default_payload["read_only"] is True and default_payload["non_executing"] is True,
        "live_shadow_existing_append_path_only": "append_decision_jsonl" in live_shadow_text and "run_shadow_decision_from_snapshot" in live_shadow_text,
        "new_module_does_not_import_live_shadow": "btcts.autotrade.live_shadow" not in text,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty_lines = [line for line in proc.stdout.splitlines() if line.strip()]
    allowed_dirty_markers = (
        "btcts_next/src/btcts/autotrade/__init__.py",
        "btcts_next/src/btcts/autotrade/decision_ledger_policy_gate.py",
        "tools/test_phase4a_autotrade_milestone_hf_decision_ledger_policy_gate_guard.py",
        "tools/test_phase4a_autotrade_milestone_hf_decision_ledger_policy_gate_close_guard.py",
    )
    unexpected_dirty = [line for line in dirty_lines if not any(marker in line for marker in allowed_dirty_markers)]
    failures.extend(f"unexpected dirty file during HF: {line}" for line in unexpected_dirty)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_hf_decision_ledger_policy_gate_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"only_expected_files_dirty": not unexpected_dirty},
        "sample": {
            "default_gate": default_payload,
            "acknowledged_gate": acknowledged_payload,
            "missing_gate": missing_payload,
            "blocked_gate": blocked_payload,
        },
        "dirty_lines": dirty_lines,
        "unexpected_dirty": unexpected_dirty,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_decision_ledger_policy_gate_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
