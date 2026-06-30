# path: ./tools/diagnose_phase4a_prediction_system_ps_q25k_warroom_prediction_producer_cadence_gap_planning.py
# desc: Read-only diagnostic for PS-Q25K WarRoom prediction producer cadence/freshness gap planning.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_contract import (  # noqa: E402
    PREDICTION_WARROOM_PRODUCER_CADENCE_GAP_PLAN_VERSION,
    RECOMMENDED_CADENCE_SEC,
    build_prediction_warroom_producer_cadence_gap_plan,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q25k_warroom_prediction_producer_cadence_gap_planning.v1"
CONTRACT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_contract.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q25K_WARROOM_PREDICTION_PRODUCER_CADENCE_GAP_PLANNING_2026-06-30.md"


def run_warroom_prediction_producer_cadence_gap_planning_diagnostic() -> dict:
    plan = build_prediction_warroom_producer_cadence_gap_plan()
    blocked = build_prediction_warroom_producer_cadence_gap_plan(request_producer_cadence_change=True)
    contract_text = CONTRACT.read_text(encoding="utf-8-sig")
    doc_text = DOC.read_text(encoding="utf-8-sig") if DOC.exists() else ""
    blockers: list[str] = []
    if plan.get("cadence_gap_plan_version") != PREDICTION_WARROOM_PRODUCER_CADENCE_GAP_PLAN_VERSION:
        blockers.append("cadence_gap_plan_version_required")
    if plan.get("current_contract_recommended_cadence_sec") != RECOMMENDED_CADENCE_SEC:
        blockers.append("recommended_cadence_mismatch")
    if plan.get("horizon_cadence_gap_row_count") != 6:
        blockers.append("six_horizon_rows_required")
    rows = plan.get("horizon_cadence_gap_rows") or []
    by_label = {row.get("horizon_label"): row for row in rows if isinstance(row, dict)}
    for label in ("15s", "60s", "300s", "900s", "1800s", "3600s"):
        if label not in by_label:
            blockers.append(f"horizon_row_required:{label}")
    for label in ("15s", "60s", "300s"):
        if by_label.get(label, {}).get("needs_faster_than_current_contract") is not True:
            blockers.append(f"short_horizon_gap_required:{label}")
    if by_label.get("900s", {}).get("baseline_supports_horizon_freshness") is not True:
        blockers.append("900s_baseline_support_required")
    if plan.get("short_horizon_freshness_gap_present") is not True:
        blockers.append("short_horizon_gap_present_required")
    if blocked.get("planning_state") != "blocked_dangerous_request_without_explicit_gate":
        blockers.append("dangerous_request_must_block_without_gate")
    if blocked.get("blocker_count") < 1:
        blockers.append("dangerous_request_blocker_required")
    for marker in ("PREDICTION_WARROOM_PRODUCER_CADENCE_GAP_PLAN_VERSION", "HORIZON_CADENCE_PLANNING_TARGETS", "build_prediction_warroom_producer_cadence_gap_plan", "producer_cadence_changed"):
        if marker not in contract_text:
            blockers.append(f"contract_marker_required:{marker}")
    for marker in ("cadence_gap_plan_added=true", "planning_only=true", "human_gate_required_before_any_change=true", "producer_cadence_changed=false", "scheduler_action_changed=false"):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for key in ("planning_only", "read_only", "non_executing", "contract_only", "display_only", "human_gate_required_before_any_change"):
        if plan.get(key) is not True:
            blockers.append(f"plan_true_required:{key}")
    for key in ("producer_cadence_changed", "scheduler_action_changed", "scheduler_enabled", "producer_enabled", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "latest_manifest_written", "run_sidecars_written", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "parameter_staging_write_allowed", "would_send_to_broker"):
        if plan.get(key) is not False:
            blockers.append(f"plan_false_required:{key}")
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "plan": plan,
        "blocked_request_plan": blocked,
        "safety": {
            "planning_only": True,
            "contract_only": True,
            "producer_cadence_changed": False,
            "scheduler_action_changed": False,
            "scheduler_enabled": False,
            "producer_enabled": False,
            "runtime_artifact_write_allowed": False,
            "status_artifact_write_allowed": False,
            "prediction_artifact_write_allowed": False,
            "view_artifact_write_allowed": False,
            "latest_manifest_written": False,
            "run_sidecars_written": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "ledger_append_allowed": False,
            "mode_apply_allowed": False,
            "parameter_apply_allowed": False,
            "would_send_to_broker": False,
        },
    }


def main() -> int:
    result = run_warroom_prediction_producer_cadence_gap_planning_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
