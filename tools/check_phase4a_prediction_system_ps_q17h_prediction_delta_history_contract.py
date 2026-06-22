# path: ./tools/check_phase4a_prediction_system_ps_q17h_prediction_delta_history_contract.py
# desc: PS-Q17H non-executing prediction-delta history contract. It consumes a PS-Q17B gap plan report or its observed fixture and emits required previous/latest lineage and delta contracts before realtime delta widgets. It never reads D-hot, writes artifacts, invokes refresh, renders WarRoom widgets, increases confidence, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan import CHECKER_VERSION as PS_Q17B_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan import build_report as build_ps_q17b_report

CHECKER = "ps_q17h_prediction_delta_history_contract"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17h_prediction_delta_history_contract.v1"
PS_Q17B_SOURCE_CHECKER_VERSION = PS_Q17B_CHECKER_VERSION
SOURCE_GAP_ID = "prediction_delta_history"

CONTRACT_ORDER = (
    "previous_latest_snapshot_reference_contract",
    "latest_snapshot_lineage_contract",
    "delta_computation_key_contract",
    "delta_reason_taxonomy_contract",
    "warroom_delta_widget_release_contract",
    "history_retention_and_freshness_contract",
)

REQUIRED_DELTA_FIELDS = (
    "prediction_delta_history.previous_snapshot.run_id",
    "prediction_delta_history.previous_snapshot.generated_at",
    "prediction_delta_history.previous_snapshot.source_artifact_ref",
    "prediction_delta_history.latest_snapshot.run_id",
    "prediction_delta_history.latest_snapshot.generated_at",
    "prediction_delta_history.latest_snapshot.source_artifact_ref",
    "prediction_delta_history.delta_key.market_uid",
    "prediction_delta_history.delta_key.family",
    "prediction_delta_history.delta_key.horizon_key",
    "prediction_delta_history.changed_fields",
    "prediction_delta_history.delta_reason_codes",
    "prediction_delta_release_gate.history_available",
    "prediction_delta_release_gate.widget_reliability_claim_allowed",
)

DELTA_REASON_CODES = (
    "previous_payload_missing_delta_widget_gap",
    "latest_snapshot_missing_or_invalid",
    "snapshot_lineage_mismatch",
    "market_or_horizon_key_mismatch",
    "changed_signal_strength",
    "changed_source_quality_state",
    "changed_scenario_trace",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _gap_map(report: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for row in _as_list(report.get("plan_rows")):
        item = _as_mapping(row)
        gap_id = str(item.get("gap_id") or "")
        if gap_id:
            result[gap_id] = item
    return result


def _safe_q17b_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17B_SOURCE_CHECKER_VERSION:
        failures.append("q17b_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17b_report_not_ok")
    if report.get("plan_only") is not True:
        failures.append("q17b_plan_only_missing")
    if report.get("warroom_widget_design_premise") is not True:
        failures.append("q17b_warroom_widget_design_premise_missing")
    if report.get("warroom_widget_implementation_allowed") is not False:
        failures.append("q17b_widget_implementation_boundary_not_false")
    for key in (
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
        "warroom_ui_trigger_enabled",
        "refresh_invocation_allowed",
        "scheduler_enabled",
    ):
        if report.get(key) is not False:
            failures.append(f"q17b_boundary_not_false:{key}")
    gap = _gap_map(report).get(SOURCE_GAP_ID, {})
    if not gap:
        failures.append("prediction_delta_history_gap_missing")
    elif gap.get("priority") != "P0":
        failures.append("prediction_delta_history_gap_not_p0")
    elif gap.get("blocks_before_warroom_widget_implementation") is not True:
        failures.append("prediction_delta_history_gap_not_blocking_widgets")
    return not failures, failures


def _contract_row(contract_id: str, priority: str, required_fields: list[str], validation_rule: str) -> dict[str, Any]:
    return {
        "contract_id": contract_id,
        "priority": priority,
        "state": "required",
        "required_fields": required_fields,
        "validation_rule": validation_rule,
        "blocks_realtime_delta_widget": True,
        "blocks_warroom_widget_reliability_claim": True,
        "next_validation": f"{contract_id}_guard",
        "read_only": True,
        "write_or_apply_allowed": False,
    }


def _build_contract_rows(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    gap = _gap_map(report).get(SOURCE_GAP_ID, {})
    reasons = [str(item) for item in _as_list(gap.get("reasons"))]
    rows = [
        _contract_row(
            "previous_latest_snapshot_reference_contract",
            "P0",
            [
                "prediction_delta_history.previous_snapshot.run_id",
                "prediction_delta_history.previous_snapshot.generated_at",
                "prediction_delta_history.previous_snapshot.source_artifact_ref",
            ],
            "previous snapshot reference must exist before any realtime delta claim",
        ),
        _contract_row(
            "latest_snapshot_lineage_contract",
            "P0",
            [
                "prediction_delta_history.latest_snapshot.run_id",
                "prediction_delta_history.latest_snapshot.generated_at",
                "prediction_delta_history.latest_snapshot.source_artifact_ref",
            ],
            "latest snapshot must expose stable lineage so deltas are not computed from UI-triggered generation",
        ),
        _contract_row(
            "delta_computation_key_contract",
            "P0",
            [
                "prediction_delta_history.delta_key.market_uid",
                "prediction_delta_history.delta_key.family",
                "prediction_delta_history.delta_key.horizon_key",
                "prediction_delta_history.delta_key.record_id",
            ],
            "previous and latest rows must be joined by market/family/horizon/record identity before comparing values",
        ),
        _contract_row(
            "delta_reason_taxonomy_contract",
            "P1",
            [
                "prediction_delta_history.changed_fields",
                "prediction_delta_history.delta_reason_codes",
                "prediction_delta_history.operator_explanation",
            ],
            "changed fields must map to reason codes and operator explanation before WarRoom presentation",
        ),
        _contract_row(
            "warroom_delta_widget_release_contract",
            "P0",
            [
                "prediction_delta_release_gate.history_available",
                "prediction_delta_release_gate.widget_reliability_claim_allowed",
                "prediction_delta_release_gate.blocking_reason_codes",
            ],
            "WarRoom delta widget reliability claims remain false while previous/latest history is missing or unverified",
        ),
        _contract_row(
            "history_retention_and_freshness_contract",
            "P1",
            [
                "prediction_delta_history.retention_policy.max_snapshot_count",
                "prediction_delta_history.freshness.max_age_seconds",
                "prediction_delta_history.history_source_kind",
            ],
            "history retention and freshness limits must be declared before realtime widget refresh design",
        ),
    ]
    if reasons:
        rows[0]["source_gap_reasons"] = reasons
    return sorted(rows, key=lambda row: ({"P0": 0, "P1": 1, "P2": 2}.get(str(row["priority"]), 9), CONTRACT_ORDER.index(str(row["contract_id"]))))


def build_report(*, supplied_q17b_report: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17b_report = _as_mapping(supplied_q17b_report)
    if not q17b_report and use_observed_fixture:
        q17b_report = build_ps_q17b_report(use_observed_fixture=True)
    safe_q17b, validation_failures = _safe_q17b_boundary(q17b_report)
    contract_rows = _build_contract_rows(q17b_report) if safe_q17b else []
    p0_count = sum(1 for row in contract_rows if row.get("priority") == "P0")
    p1_count = sum(1 for row in contract_rows if row.get("priority") == "P1")
    widget_blockers = [row["contract_id"] for row in contract_rows if row.get("blocks_realtime_delta_widget")]
    ok = bool(safe_q17b and contract_rows and p0_count == 4 and widget_blockers)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "stage": "prediction_delta_history_contract_before_realtime_widget_rendering",
        "source_checker_version": PS_Q17B_SOURCE_CHECKER_VERSION,
        "source_q17b_report_valid": safe_q17b,
        "source_q17b_validation_failures": validation_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "source_gap_id": SOURCE_GAP_ID,
        "contract_rows": contract_rows,
        "contract_count": len(contract_rows),
        "p0_contract_count": p0_count,
        "p1_contract_count": p1_count,
        "required_delta_fields": list(REQUIRED_DELTA_FIELDS),
        "delta_reason_codes": list(DELTA_REASON_CODES),
        "blocks_realtime_delta_widget": widget_blockers,
        "history_required_before_delta_claim": True,
        "recommended_first_validation": widget_blockers[0] if widget_blockers else "",
        "recommended_next_slice": "PS-Q17I prediction-delta history adapter or replay-outcome calibration contract; confidence increase, parameter apply, and WarRoom widget rendering remain deferred.",
        "human_interpretation": "PS-Q17H turns the missing previous-payload/delta-widget P0 gap into explicit previous/latest lineage and delta contracts. It does not read history, compute live deltas, render widgets, write artifacts, or trigger generation.",
        "read_only": True,
        "non_executing": True,
        "contract_only": True,
        "diagnostic_only": True,
        "plan_only": True,
        "warroom_widget_design_premise": True,
        "warroom_widget_implementation_allowed": False,
        "delta_widget_rendering_allowed": False,
        "history_actual_read_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "d_hot_actual_read_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
        "warroom_ui_trigger_enabled": False,
        "refresh_invocation_allowed": False,
        "scheduler_enabled": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q17H prediction-delta history contract")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use the static PS-Q17B observed fixture path; no D-hot or history read is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
