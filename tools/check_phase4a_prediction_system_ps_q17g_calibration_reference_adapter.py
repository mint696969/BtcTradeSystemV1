# path: ./tools/check_phase4a_prediction_system_ps_q17g_calibration_reference_adapter.py
# desc: PS-Q17G standalone calibration reference adapter. It consumes supplied calibration refs or static fixtures only and emits a normalized calibration packet; it never reads D-hot, writes artifacts, invokes refresh, renders WarRoom widgets, increases confidence, makes reliability claims, tunes/stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17f_calibration_reference_contract import CHECKER_VERSION as PS_Q17F_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17f_calibration_reference_contract import REQUIRED_CALIBRATION_FIELDS, build_report as build_ps_q17f_report

CHECKER = "ps_q17g_calibration_reference_adapter"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17g_calibration_reference_adapter.v1"
PS_Q17F_SOURCE_CHECKER_VERSION = PS_Q17F_CHECKER_VERSION
ADAPTER_VERSION = "calibration_reference_adapter.v1"
SIGNAL_BANDS = ("very_low", "low", "medium", "high", "unknown")
REFERENCE_HIT_RATE_BANDS = ("very_low", "low", "medium", "high", "unknown")
REQUIRED_REF_SECTIONS = ("signal_strength", "reference_hit_rate", "sample_window")


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


def _safe_q17f_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17F_SOURCE_CHECKER_VERSION:
        failures.append("q17f_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17f_report_not_ok")
    if report.get("contract_only") is not True:
        failures.append("q17f_contract_only_missing")
    if report.get("confidence_increase_allowed") is not False:
        failures.append("q17f_confidence_boundary_not_false")
    if report.get("signal_reliability_claim_allowed") is not False:
        failures.append("q17f_signal_reliability_boundary_not_false")
    if report.get("parameter_tuning_allowed") is not False:
        failures.append("q17f_parameter_tuning_boundary_not_false")
    if report.get("d_hot_actual_read_allowed") is not False:
        failures.append("q17f_d_hot_boundary_not_false")
    if report.get("warroom_widget_implementation_allowed") is not False:
        failures.append("q17f_widget_implementation_boundary_not_false")
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
            failures.append(f"q17f_boundary_not_false:{key}")
    contracts = _contract_map(report)
    for required in (
        "signal_strength_calibration_reference_contract",
        "reference_hit_rate_calibration_reference_contract",
        "calibration_sample_window_contract",
        "confidence_band_release_contract",
    ):
        row = contracts.get(required, {})
        if not row:
            failures.append(f"q17f_required_contract_missing:{required}")
        elif row.get("priority") != "P0" or row.get("blocks_confidence_increase") is not True:
            failures.append(f"q17f_required_contract_not_p0_blocking:{required}")
    return not failures, failures


def _fixture_q17f_contract_report() -> dict[str, Any]:
    return build_ps_q17f_report(use_observed_fixture=True)


def _fixture_calibration_refs() -> dict[str, Any]:
    return {
        "calibration_ref_id": "fixture.calibration.ps_q17g",
        "market_uid": "BTC_JPY:bitFlyer",
        "sample_window": {
            "start_at": "2026-06-01T00:00:00Z",
            "end_at": "2026-06-22T00:00:00Z",
            "market_uid": "BTC_JPY:bitFlyer",
            "horizon_keys": ["short", "mid"],
        },
        "signal_strength": {
            "model_version": "fixture.signal_strength.v1",
            "sample_window": {"start_at": "2026-06-01T00:00:00Z", "end_at": "2026-06-22T00:00:00Z"},
            "sample_count": 110,
            "bucket_metrics": {
                "very_low": {"min_percent": 0, "max_percent": 24, "observed_hit_rate": 0.31, "record_count": 12},
                "low": {"min_percent": 25, "max_percent": 49, "observed_hit_rate": 0.42, "record_count": 98},
                "medium": {"min_percent": 50, "max_percent": 74, "observed_hit_rate": None, "record_count": 0},
                "high": {"min_percent": 75, "max_percent": 100, "observed_hit_rate": None, "record_count": 0},
            },
        },
        "reference_hit_rate": {
            "model_version": "fixture.reference_hit_rate.v1",
            "sample_window": {"start_at": "2026-06-01T00:00:00Z", "end_at": "2026-06-22T00:00:00Z"},
            "sample_count": 110,
            "bucket_metrics": {
                "very_low": {"min_percent": 0, "max_percent": 24, "observed_reference_hit_rate": 0.29, "record_count": 12},
                "low": {"min_percent": 25, "max_percent": 49, "observed_reference_hit_rate": 0.40, "record_count": 98},
                "medium": {"min_percent": 50, "max_percent": 74, "observed_reference_hit_rate": None, "record_count": 0},
                "high": {"min_percent": 75, "max_percent": 100, "observed_reference_hit_rate": None, "record_count": 0},
            },
        },
        "staleness_state": "fixture_only_not_live",
    }


def _normalize_bucket_metrics(metrics: Mapping[str, Any], bands: tuple[str, ...]) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for band in bands:
        result[band] = _as_mapping(metrics.get(band))
    return result


def _section_present(section: Mapping[str, Any], metric_key: str) -> bool:
    buckets = _as_mapping(section.get("bucket_metrics"))
    return bool(section.get("model_version") and int(section.get("sample_count") or 0) > 0 and _as_mapping(buckets.get(metric_key)))


def adapt_calibration_refs(refs: Mapping[str, Any] | Any) -> dict[str, Any]:
    data = _as_mapping(refs)
    signal = _as_mapping(data.get("signal_strength"))
    hit_rate = _as_mapping(data.get("reference_hit_rate"))
    sample_window = _as_mapping(data.get("sample_window"))
    signal_present = _section_present(signal, "low")
    hit_rate_present = _section_present(hit_rate, "low")
    window_present = bool(sample_window.get("start_at") and sample_window.get("end_at") and sample_window.get("market_uid"))
    calibration_refs_present = bool(signal_present and hit_rate_present and window_present)
    blocking_reason_codes: list[str] = []
    if not signal_present:
        blocking_reason_codes.append("signal_strength_calibration_ref_missing_or_incomplete")
    if not hit_rate_present:
        blocking_reason_codes.append("reference_hit_rate_calibration_ref_missing_or_incomplete")
    if not window_present:
        blocking_reason_codes.append("calibration_sample_window_missing_or_incomplete")
    blocking_reason_codes.append("adapter_stage_no_confidence_or_parameter_release")
    return {
        "adapter_version": ADAPTER_VERSION,
        "calibration_ref_id": str(data.get("calibration_ref_id") or ""),
        "market_uid": str(data.get("market_uid") or sample_window.get("market_uid") or ""),
        "sample_window": {
            "start_at": str(sample_window.get("start_at") or ""),
            "end_at": str(sample_window.get("end_at") or ""),
            "market_uid": str(sample_window.get("market_uid") or data.get("market_uid") or ""),
            "horizon_keys": [str(item) for item in _as_list(sample_window.get("horizon_keys"))],
        },
        "calibration_refs": {
            "signal_strength": {
                "model_version": str(signal.get("model_version") or ""),
                "sample_window": _as_mapping(signal.get("sample_window")),
                "sample_count": int(signal.get("sample_count") or 0),
                "bucket_metrics": _normalize_bucket_metrics(_as_mapping(signal.get("bucket_metrics")), SIGNAL_BANDS),
            },
            "reference_hit_rate": {
                "model_version": str(hit_rate.get("model_version") or ""),
                "sample_window": _as_mapping(hit_rate.get("sample_window")),
                "sample_count": int(hit_rate.get("sample_count") or 0),
                "bucket_metrics": _normalize_bucket_metrics(_as_mapping(hit_rate.get("bucket_metrics")), REFERENCE_HIT_RATE_BANDS),
            },
        },
        "calibration_release_gate": {
            "calibration_refs_present": calibration_refs_present,
            "confidence_band_claim_allowed": False,
            "signal_reliability_claim_allowed": False,
            "parameter_tuning_allowed": False,
            "blocking_reason_codes": blocking_reason_codes,
        },
        "warroom_calibration_explanation_packet": {
            "calibration_ref_id": str(data.get("calibration_ref_id") or ""),
            "sample_count": min(int(signal.get("sample_count") or 0), int(hit_rate.get("sample_count") or 0)),
            "staleness_state": str(data.get("staleness_state") or "unknown"),
            "operator_explanation": "Calibration refs are normalized for review only; confidence, reliability, parameter tuning, and widget rendering remain deferred.",
            "render_allowed": False,
        },
        "contract_completeness": {
            "required_calibration_fields": list(REQUIRED_CALIBRATION_FIELDS),
            "has_signal_strength_ref": signal_present,
            "has_reference_hit_rate_ref": hit_rate_present,
            "has_sample_window": window_present,
            "has_release_gate": True,
        },
        "read_only": True,
        "write_or_apply_allowed": False,
        "confidence_increase_allowed": False,
        "signal_reliability_claim_allowed": False,
        "parameter_tuning_allowed": False,
    }


def _adapter_valid(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    refs = _as_mapping(packet.get("calibration_refs"))
    signal = _as_mapping(refs.get("signal_strength"))
    hit_rate = _as_mapping(refs.get("reference_hit_rate"))
    release = _as_mapping(packet.get("calibration_release_gate"))
    completeness = _as_mapping(packet.get("contract_completeness"))
    warroom = _as_mapping(packet.get("warroom_calibration_explanation_packet"))
    if not packet.get("calibration_ref_id"):
        failures.append("calibration_ref_id_missing")
    if not _section_present(signal, "low"):
        failures.append("signal_strength_ref_incomplete")
    if not _section_present(hit_rate, "low"):
        failures.append("reference_hit_rate_ref_incomplete")
    if release.get("calibration_refs_present") is not True:
        failures.append("calibration_refs_present_not_true")
    for key in ("confidence_band_claim_allowed", "signal_reliability_claim_allowed", "parameter_tuning_allowed"):
        if release.get(key) is not False:
            failures.append(f"release_gate_must_stay_false:{key}")
    if warroom.get("render_allowed") is not False:
        failures.append("warroom_render_must_stay_false")
    for key in ("has_signal_strength_ref", "has_reference_hit_rate_ref", "has_sample_window", "has_release_gate"):
        if completeness.get(key) is not True:
            failures.append(f"contract_completeness_false:{key}")
    return not failures, failures


def build_report(*, supplied_q17f_report: Mapping[str, Any] | Any | None = None, supplied_calibration_refs: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17f_report = _as_mapping(supplied_q17f_report)
    refs = _as_mapping(supplied_calibration_refs)
    if not q17f_report and use_observed_fixture:
        q17f_report = _fixture_q17f_contract_report()
    if not refs and use_observed_fixture:
        refs = _fixture_calibration_refs()
    safe_q17f, validation_failures = _safe_q17f_boundary(q17f_report)
    packet = adapt_calibration_refs(refs) if safe_q17f and refs else {}
    adapter_valid, adapter_failures = _adapter_valid(packet) if packet else (False, ["calibration_refs_missing_or_q17f_invalid"])
    ok = bool(safe_q17f and adapter_valid)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "stage": "calibration_reference_adapter_before_confidence_parameter_and_widget_release",
        "source_checker_version": PS_Q17F_SOURCE_CHECKER_VERSION,
        "source_q17f_report_valid": safe_q17f,
        "source_q17f_validation_failures": validation_failures,
        "adapter_valid": adapter_valid,
        "adapter_validation_failures": adapter_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "adapted_packet": packet,
        "recommended_next_slice": "PS-Q17H prediction-delta history contract or calibration adapter integration design; confidence increase, parameter apply, and WarRoom widget rendering remain deferred.",
        "human_interpretation": "PS-Q17G proves supplied calibration refs can be normalized into a review packet. It does not read D-hot, write artifacts, raise confidence, make signal reliability claims, tune parameters, render widgets, trigger AutoTrade, or call broker APIs.",
        "read_only": True,
        "non_executing": True,
        "adapter_only": True,
        "contract_only": True,
        "diagnostic_only": True,
        "warroom_widget_design_premise": True,
        "warroom_widget_implementation_allowed": False,
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
    parser = argparse.ArgumentParser(description="PS-Q17G calibration reference adapter")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use static Q17F and calibration ref fixtures; no D-hot read is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
