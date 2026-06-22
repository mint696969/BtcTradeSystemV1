# path: ./tools/check_phase4a_prediction_system_ps_q17k_replay_outcome_calibration_adapter.py
# desc: PS-Q17K standalone replay-outcome calibration adapter. It consumes supplied replay feedback/outcome fixtures only and emits a normalized review packet; it never reads D-hot or replay history, writes artifacts, invokes refresh, renders WarRoom widgets, raises confidence, claims reliability, tunes/stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17j_replay_outcome_calibration_contract import CHECKER_VERSION as PS_Q17J_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17j_replay_outcome_calibration_contract import REQUIRED_REPLAY_FIELDS, build_report as build_ps_q17j_report

CHECKER = "ps_q17k_replay_outcome_calibration_adapter"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17k_replay_outcome_calibration_adapter.v1"
PS_Q17J_SOURCE_CHECKER_VERSION = PS_Q17J_CHECKER_VERSION
ADAPTER_VERSION = "replay_outcome_calibration_adapter.v1"
REPLAY_PACKET_VERSION = "replay_outcome_calibration_review_packet.v1"
JOIN_KEYS = ("market_uid", "family", "horizon_key", "record_id")
OUTCOME_METRIC_FIELDS = ("predicted_direction_hit", "actual_return_bps", "magnitude_error_bps")


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


def _safe_q17j_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17J_SOURCE_CHECKER_VERSION:
        failures.append("q17j_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17j_report_not_ok")
    if report.get("contract_only") is not True:
        failures.append("q17j_contract_only_missing")
    for key in (
        "warroom_widget_implementation_allowed",
        "replay_history_actual_read_allowed",
        "replay_outcome_widget_rendering_allowed",
        "confidence_increase_allowed",
        "signal_reliability_claim_allowed",
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
            failures.append(f"q17j_boundary_not_false:{key}")
    contracts = _contract_map(report)
    for required in (
        "replay_feedback_reference_contract",
        "outcome_window_contract",
        "forecast_to_outcome_join_key_contract",
        "replay_calibration_release_gate_contract",
    ):
        row = contracts.get(required, {})
        if not row:
            failures.append(f"q17j_required_contract_missing:{required}")
        elif row.get("priority") != "P0" or row.get("blocks_confidence_reliability_claim") is not True:
            failures.append(f"q17j_required_contract_not_p0_blocking:{required}")
    return not failures, failures


def _fixture_q17j_contract_report() -> dict[str, Any]:
    return build_ps_q17j_report(use_observed_fixture=True)


def _fixture_replay_feedback() -> dict[str, Any]:
    return {
        "replay_feedback": {"run_id": "fixture.replay.run", "generated_at": "2026-06-22T01:00:00Z", "source_artifact_ref": "fixture://replay/outcome.json"},
        "outcome_window": {"start_at": "2026-06-01T00:00:00Z", "end_at": "2026-06-22T00:00:00Z", "market_uid": "BTC_JPY:bitFlyer", "horizon_keys": ["short", "mid"]},
        "rows": [
            {"record_id": "trend:short", "market_uid": "BTC_JPY:bitFlyer", "family": "trend", "horizon_key": "short", "predicted_direction_hit": True, "actual_return_bps": 42.5, "magnitude_error_bps": 8.0},
            {"record_id": "mr:short", "market_uid": "BTC_JPY:bitFlyer", "family": "mean_reversion", "horizon_key": "short", "predicted_direction_hit": False, "actual_return_bps": -15.0, "magnitude_error_bps": 21.0},
        ],
    }


def _row_key(row: Mapping[str, Any]) -> dict[str, str]:
    return {key: str(row.get(key) or "") for key in JOIN_KEYS}


def adapt_replay_feedback(payload: Mapping[str, Any] | Any) -> dict[str, Any]:
    data = _as_mapping(payload)
    feedback = _as_mapping(data.get("replay_feedback"))
    window = _as_mapping(data.get("outcome_window"))
    rows: list[dict[str, Any]] = []
    hits = 0
    total_error = 0.0
    for item in _as_list(data.get("rows")):
        row = _as_mapping(item)
        key = _row_key(row)
        if not all(key.values()):
            continue
        metrics = {field: row.get(field) for field in OUTCOME_METRIC_FIELDS}
        if metrics.get("predicted_direction_hit") is True:
            hits += 1
        try:
            total_error += float(metrics.get("magnitude_error_bps") or 0.0)
        except (TypeError, ValueError):
            pass
        rows.append({"forecast_to_outcome_key": key, "outcome_metrics": metrics, "read_only": True})
    sample_count = len(rows)
    hit_rate = (hits / sample_count) if sample_count else None
    mean_magnitude_error_bps = (total_error / sample_count) if sample_count else None
    blocking_reason_codes: list[str] = []
    if not feedback.get("run_id"):
        blocking_reason_codes.append("replay_feedback_present=false")
    if not window.get("start_at") or not window.get("end_at"):
        blocking_reason_codes.append("outcome_window_missing_or_unverified")
    if not rows:
        blocking_reason_codes.append("forecast_to_outcome_join_key_missing")
    blocking_reason_codes.append("adapter_stage_no_confidence_or_parameter_release")
    return {
        "adapter_version": ADAPTER_VERSION,
        "replay_packet_version": REPLAY_PACKET_VERSION,
        "replay_outcome_calibration": {
            "replay_feedback": {
                "run_id": str(feedback.get("run_id") or ""),
                "generated_at": str(feedback.get("generated_at") or ""),
                "source_artifact_ref": str(feedback.get("source_artifact_ref") or ""),
            },
            "outcome_window": {
                "start_at": str(window.get("start_at") or ""),
                "end_at": str(window.get("end_at") or ""),
                "market_uid": str(window.get("market_uid") or ""),
                "horizon_keys": [str(item) for item in _as_list(window.get("horizon_keys"))],
            },
            "outcome_rows": rows,
            "sample_count": sample_count,
            "summary_metrics": {
                "predicted_direction_hit_rate": hit_rate,
                "mean_magnitude_error_bps": mean_magnitude_error_bps,
            },
        },
        "replay_calibration_release_gate": {
            "replay_feedback_present": bool(feedback.get("run_id") and rows),
            "confidence_reliability_claim_allowed": False,
            "signal_reliability_claim_allowed": False,
            "parameter_tuning_allowed": False,
            "blocking_reason_codes": blocking_reason_codes,
        },
        "contract_completeness": {
            "required_replay_fields": list(REQUIRED_REPLAY_FIELDS),
            "has_replay_feedback": bool(feedback.get("run_id") and feedback.get("generated_at") and feedback.get("source_artifact_ref")),
            "has_outcome_window": bool(window.get("start_at") and window.get("end_at") and window.get("market_uid") and _as_list(window.get("horizon_keys"))),
            "has_join_keys": bool(rows),
            "has_outcome_metrics": bool(rows and all(row.get("outcome_metrics") for row in rows)),
            "has_release_gate": True,
        },
        "warroom_replay_outcome_widget": {
            "replay_feedback_ref_id": str(feedback.get("run_id") or ""),
            "sample_count": sample_count,
            "operator_explanation": "Replay outcomes are normalized for review only; confidence, reliability, parameter tuning, and widget rendering remain deferred.",
            "render_allowed": False,
        },
        "read_only": True,
        "write_or_apply_allowed": False,
        "replay_history_actual_read_allowed": False,
        "replay_outcome_widget_rendering_allowed": False,
    }


def _adapter_valid(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    replay = _as_mapping(packet.get("replay_outcome_calibration"))
    release = _as_mapping(packet.get("replay_calibration_release_gate"))
    completeness = _as_mapping(packet.get("contract_completeness"))
    warroom = _as_mapping(packet.get("warroom_replay_outcome_widget"))
    if int(replay.get("sample_count") or 0) < 1:
        failures.append("sample_count_missing")
    if not _as_mapping(replay.get("summary_metrics")):
        failures.append("summary_metrics_missing")
    if release.get("replay_feedback_present") is not True:
        failures.append("replay_feedback_present_not_true")
    for key in ("confidence_reliability_claim_allowed", "signal_reliability_claim_allowed", "parameter_tuning_allowed"):
        if release.get(key) is not False:
            failures.append(f"release_gate_must_stay_false:{key}")
    if warroom.get("render_allowed") is not False:
        failures.append("warroom_render_must_stay_false")
    for key in ("has_replay_feedback", "has_outcome_window", "has_join_keys", "has_outcome_metrics", "has_release_gate"):
        if completeness.get(key) is not True:
            failures.append(f"contract_completeness_false:{key}")
    return not failures, failures


def build_report(*, supplied_q17j_report: Mapping[str, Any] | Any | None = None, supplied_replay_feedback: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17j_report = _as_mapping(supplied_q17j_report)
    replay_feedback = _as_mapping(supplied_replay_feedback)
    if not q17j_report and use_observed_fixture:
        q17j_report = _fixture_q17j_contract_report()
    if not replay_feedback and use_observed_fixture:
        replay_feedback = _fixture_replay_feedback()
    safe_q17j, validation_failures = _safe_q17j_boundary(q17j_report)
    packet = adapt_replay_feedback(replay_feedback) if safe_q17j and replay_feedback else {}
    adapter_valid, adapter_failures = _adapter_valid(packet) if packet else (False, ["replay_feedback_missing_or_q17j_invalid"])
    ok = bool(safe_q17j and adapter_valid)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "stage": "replay_outcome_calibration_adapter_before_confidence_parameter_and_widget_release",
        "source_checker_version": PS_Q17J_SOURCE_CHECKER_VERSION,
        "source_q17j_report_valid": safe_q17j,
        "source_q17j_validation_failures": validation_failures,
        "adapter_valid": adapter_valid,
        "adapter_validation_failures": adapter_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "adapted_packet": packet,
        "recommended_next_slice": "PS-Q17L scenario-trace semantic mapping contract or parameter-candidate evidence contract; confidence increase, parameter apply, and WarRoom widget rendering remain deferred.",
        "human_interpretation": "PS-Q17K proves supplied replay feedback can be normalized into a review-only outcome calibration packet. It does not read replay history or D-hot, raise confidence, claim reliability, tune parameters, render widgets, write artifacts, or trigger generation.",
        "read_only": True,
        "non_executing": True,
        "adapter_only": True,
        "contract_only": True,
        "diagnostic_only": True,
        "warroom_widget_design_premise": True,
        "warroom_widget_implementation_allowed": False,
        "replay_history_actual_read_allowed": False,
        "replay_outcome_widget_rendering_allowed": False,
        "confidence_increase_allowed": False,
        "signal_reliability_claim_allowed": False,
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
    parser = argparse.ArgumentParser(description="PS-Q17K replay-outcome calibration adapter")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use static Q17J and replay feedback fixtures; no D-hot/replay-history read is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
