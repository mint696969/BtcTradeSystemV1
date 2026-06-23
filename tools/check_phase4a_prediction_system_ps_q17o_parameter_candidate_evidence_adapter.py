# path: ./tools/check_phase4a_prediction_system_ps_q17o_parameter_candidate_evidence_adapter.py
# desc: PS-Q17O standalone parameter-candidate evidence adapter. It consumes supplied baseline/candidate/rollback/evidence fixtures only and emits a normalized review packet; it never reads D-hot or parameter candidates, writes artifacts, invokes refresh, renders WarRoom widgets, stages/applies parameters, increases confidence, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17n_parameter_candidate_evidence_contract import CHECKER_VERSION as PS_Q17N_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17n_parameter_candidate_evidence_contract import REQUIRED_PARAMETER_FIELDS, build_report as build_ps_q17n_report

CHECKER = "ps_q17o_parameter_candidate_evidence_adapter"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17o_parameter_candidate_evidence_adapter.v1"
PS_Q17N_SOURCE_CHECKER_VERSION = PS_Q17N_CHECKER_VERSION
ADAPTER_VERSION = "parameter_candidate_evidence_adapter.v1"
PARAMETER_PACKET_VERSION = "parameter_candidate_evidence_review_packet.v1"
REQUIRED_EVIDENCE_REFS = ("source_quality_ref_id", "calibration_ref_id", "replay_feedback_ref_id")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _contract_map(report: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for row in _as_list(report.get("contract_rows")):
        item = _as_mapping(row)
        contract_id = str(item.get("contract_id") or "")
        if contract_id:
            result[contract_id] = item
    return result


def _safe_q17n_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17N_SOURCE_CHECKER_VERSION:
        failures.append("q17n_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17n_report_not_ok")
    if report.get("contract_only") is not True:
        failures.append("q17n_contract_only_missing")
    for key in (
        "warroom_widget_implementation_allowed",
        "parameter_candidate_actual_read_allowed",
        "parameter_candidate_widget_rendering_allowed",
        "parameter_candidate_reliability_claim_allowed",
        "confidence_increase_allowed",
        "parameter_tuning_allowed",
        "d_hot_actual_read_allowed",
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
            failures.append(f"q17n_boundary_not_false:{key}")
    contracts = _contract_map(report)
    for required in (
        "parameter_candidate_source_contract",
        "baseline_parameter_reference_contract",
        "candidate_parameter_diff_contract",
        "rollback_threshold_contract",
        "parameter_evidence_completeness_release_gate_contract",
    ):
        row = contracts.get(required, {})
        if not row:
            failures.append(f"q17n_required_contract_missing:{required}")
        elif row.get("priority") != "P0" or row.get("blocks_parameter_staging") is not True or row.get("blocks_parameter_apply") is not True:
            failures.append(f"q17n_required_contract_not_p0_blocking:{required}")
    return not failures, failures


def _fixture_q17n_contract_report() -> dict[str, Any]:
    return build_ps_q17n_report(use_observed_fixture=True)


def _fixture_parameter_candidate() -> dict[str, Any]:
    return {
        "source_artifact_ref": "fixture://parameter/candidate.json",
        "generated_at": "2026-06-22T02:00:00Z",
        "baseline": {"ref_id": "baseline.ref.fixture", "parameter_set_id": "params.v1", "effective_at": "2026-06-01T00:00:00Z"},
        "candidate": {
            "candidate_id": "candidate.fixture.tighten_signal_floor",
            "changed_parameter_keys": ["signal_strength_floor", "source_quality_min_count"],
            "diff_summary": "Review-only candidate raises signal floor and minimum source quality count.",
            "expected_effect_summary": "Expected to reduce weak-confidence candidates; no live parameter change is allowed in this slice.",
        },
        "evidence": {
            "source_quality_ref_id": "source_quality.ps_q17e.fixture",
            "calibration_ref_id": "calibration.ps_q17g.fixture",
            "replay_feedback_ref_id": "replay.ps_q17k.fixture",
        },
        "rollback": {
            "rollback_threshold_ref_id": "rollback.threshold.fixture",
            "rollback_condition_summary": "Rollback if replay hit-rate or source-quality coverage degrades in later verified review.",
            "abort_condition_summary": "Abort before staging if any evidence ref is missing or stale.",
        },
    }


def adapt_parameter_candidate(payload: Mapping[str, Any] | Any) -> dict[str, Any]:
    data = _as_mapping(payload)
    baseline = _as_mapping(data.get("baseline"))
    candidate = _as_mapping(data.get("candidate"))
    evidence = _as_mapping(data.get("evidence"))
    rollback = _as_mapping(data.get("rollback"))
    changed_keys = [str(item) for item in _as_list(candidate.get("changed_parameter_keys"))]
    missing: list[str] = []
    if not data.get("source_artifact_ref"):
        missing.append("parameter_candidate_source_missing")
    if not baseline.get("ref_id") or not baseline.get("parameter_set_id"):
        missing.append("baseline_parameter_reference_missing_or_unverified")
    if not candidate.get("candidate_id") or not changed_keys:
        missing.append("candidate_parameter_diff_missing_or_unverified")
    if not rollback.get("rollback_threshold_ref_id") or not rollback.get("rollback_condition_summary"):
        missing.append("rollback_threshold_missing_or_unverified")
    for ref in REQUIRED_EVIDENCE_REFS:
        if not evidence.get(ref):
            missing.append(f"{ref}_missing")
    evidence_complete = not missing
    blocking_reason_codes = missing + ["adapter_stage_no_parameter_staging_or_apply"]
    return {
        "adapter_version": ADAPTER_VERSION,
        "parameter_packet_version": PARAMETER_PACKET_VERSION,
        "parameter_candidate": {
            "source_artifact_ref": str(data.get("source_artifact_ref") or ""),
            "generated_at": str(data.get("generated_at") or ""),
            "baseline": {
                "ref_id": str(baseline.get("ref_id") or ""),
                "parameter_set_id": str(baseline.get("parameter_set_id") or ""),
                "effective_at": str(baseline.get("effective_at") or ""),
            },
            "candidate": {
                "candidate_id": str(candidate.get("candidate_id") or ""),
                "changed_parameter_keys": changed_keys,
                "diff_summary": str(candidate.get("diff_summary") or ""),
                "expected_effect_summary": str(candidate.get("expected_effect_summary") or ""),
            },
            "evidence": {ref: str(evidence.get(ref) or "") for ref in REQUIRED_EVIDENCE_REFS},
            "rollback": {
                "rollback_threshold_ref_id": str(rollback.get("rollback_threshold_ref_id") or ""),
                "rollback_condition_summary": str(rollback.get("rollback_condition_summary") or ""),
                "abort_condition_summary": str(rollback.get("abort_condition_summary") or ""),
            },
        },
        "parameter_candidate_release_gate": {
            "evidence_complete": evidence_complete,
            "parameter_staging_allowed": False,
            "parameter_apply_allowed": False,
            "confidence_increase_allowed": False,
            "parameter_tuning_allowed": False,
            "blocking_reason_codes": blocking_reason_codes,
        },
        "contract_completeness": {
            "required_parameter_fields": list(REQUIRED_PARAMETER_FIELDS),
            "has_source_artifact_ref": bool(data.get("source_artifact_ref")),
            "has_baseline_reference": bool(baseline.get("ref_id") and baseline.get("parameter_set_id")),
            "has_candidate_diff": bool(candidate.get("candidate_id") and changed_keys),
            "has_source_quality_ref": bool(evidence.get("source_quality_ref_id")),
            "has_calibration_ref": bool(evidence.get("calibration_ref_id")),
            "has_replay_feedback_ref": bool(evidence.get("replay_feedback_ref_id")),
            "has_rollback_threshold": bool(rollback.get("rollback_threshold_ref_id") and rollback.get("rollback_condition_summary")),
            "has_release_gate": True,
        },
        "warroom_parameter_candidate_widget": {
            "candidate_id": str(candidate.get("candidate_id") or ""),
            "baseline_ref_id": str(baseline.get("ref_id") or ""),
            "operator_explanation": "Parameter candidate evidence is normalized for review only; staging, apply, confidence increase, and widget rendering remain deferred.",
            "render_allowed": False,
        },
        "read_only": True,
        "write_or_apply_allowed": False,
        "parameter_candidate_actual_read_allowed": False,
        "parameter_candidate_widget_rendering_allowed": False,
    }


def _adapter_valid(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    release = _as_mapping(packet.get("parameter_candidate_release_gate"))
    completeness = _as_mapping(packet.get("contract_completeness"))
    widget = _as_mapping(packet.get("warroom_parameter_candidate_widget"))
    if release.get("evidence_complete") is not True:
        failures.append("evidence_complete_not_true")
    for key in ("parameter_staging_allowed", "parameter_apply_allowed", "confidence_increase_allowed", "parameter_tuning_allowed"):
        if release.get(key) is not False:
            failures.append(f"release_gate_must_stay_false:{key}")
    if widget.get("render_allowed") is not False:
        failures.append("warroom_render_must_stay_false")
    for key in ("has_source_artifact_ref", "has_baseline_reference", "has_candidate_diff", "has_source_quality_ref", "has_calibration_ref", "has_replay_feedback_ref", "has_rollback_threshold", "has_release_gate"):
        if completeness.get(key) is not True:
            failures.append(f"contract_completeness_false:{key}")
    return not failures, failures


def build_report(*, supplied_q17n_report: Mapping[str, Any] | Any | None = None, supplied_parameter_candidate: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17n_report = _as_mapping(supplied_q17n_report)
    parameter_candidate = _as_mapping(supplied_parameter_candidate)
    if not q17n_report and use_observed_fixture:
        q17n_report = _fixture_q17n_contract_report()
    if not parameter_candidate and use_observed_fixture:
        parameter_candidate = _fixture_parameter_candidate()
    safe_q17n, validation_failures = _safe_q17n_boundary(q17n_report)
    packet = adapt_parameter_candidate(parameter_candidate) if safe_q17n and parameter_candidate else {}
    adapter_valid, adapter_failures = _adapter_valid(packet) if packet else (False, ["parameter_candidate_missing_or_q17n_invalid"])
    ok = bool(safe_q17n and adapter_valid)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "stage": "parameter_candidate_evidence_adapter_before_staging_apply_confidence_and_widget_release",
        "source_checker_version": PS_Q17N_SOURCE_CHECKER_VERSION,
        "source_q17n_report_valid": safe_q17n,
        "source_q17n_validation_failures": validation_failures,
        "adapter_valid": adapter_valid,
        "adapter_validation_failures": adapter_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "adapted_packet": packet,
        "recommended_next_slice": "PS-Q17P WarRoom prediction widget integration design checkpoint or parameter-candidate evidence adapter actual-source preflight; confidence increase, parameter staging/apply, and WarRoom widget rendering remain deferred.",
        "human_interpretation": "PS-Q17O proves supplied parameter-candidate evidence can be normalized into a review-only packet. It does not read D-hot or live parameter candidates, stage/apply parameters, increase confidence, render widgets, write artifacts, or trigger generation.",
        "read_only": True,
        "non_executing": True,
        "adapter_only": True,
        "contract_only": True,
        "diagnostic_only": True,
        "warroom_widget_design_premise": True,
        "warroom_widget_implementation_allowed": False,
        "parameter_candidate_actual_read_allowed": False,
        "parameter_candidate_widget_rendering_allowed": False,
        "parameter_candidate_reliability_claim_allowed": False,
        "confidence_increase_allowed": False,
        "parameter_tuning_allowed": False,
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
    parser = argparse.ArgumentParser(description="PS-Q17O parameter-candidate evidence adapter")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use static Q17N and parameter-candidate fixtures; no D-hot/parameter-candidate read is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
