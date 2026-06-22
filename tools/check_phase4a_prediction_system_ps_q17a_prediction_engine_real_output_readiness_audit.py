# path: ./tools/check_phase4a_prediction_system_ps_q17a_prediction_engine_real_output_readiness_audit.py
# desc: PS-Q17A read-only audit for real Prediction Engine output readiness. It can read the D-hot latest prediction artifact only under explicit operator acknowledgement and allow_actual_read; it never writes runtime artifacts, stages/applies parameters, appends ledgers, triggers WarRoom UI, invokes refresh, schedules jobs, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

CHECKER = "ps_q17a_prediction_engine_real_output_readiness_audit"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17a_prediction_engine_real_output_readiness_audit.v1"
DEFAULT_HOT_ROOT = r"D:\btc_ts_hot"
LATEST_RELATIVE_PATH = "prediction/latest_prediction_system_result.json"
PRODUCER_STATUS_RELATIVE_PATH = "prediction/status/non_ui_scheduled_producer_status.json"
MAX_LATEST_BYTES = 8_000_000

WIDGET_FAMILIES = (
    "latest_prediction_summary_widget",
    "prediction_delta_widget",
    "scenario_trace_widget",
    "evidence_weighting_widget",
    "invalidation_rewrite_widget",
    "source_quality_freshness_widget",
    "warning_blocker_widget",
    "signal_strength_calibration_widget",
    "parameter_candidate_comparison_widget",
    "replay_outcome_calibration_widget",
    "producer_freshness_status_widget",
    "runtime_boundary_safety_widget",
)

FORBIDDEN_FALSE_BOUNDARIES = (
    "approval_append_requested",
    "broker_execution_requested",
    "command_ledger_append_requested",
    "mode_apply_requested",
    "would_append_ledger",
    "would_send_to_broker",
    "would_write_runtime_artifact",
    "approval_or_authorization_allowed",
    "ledger_append_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
    "parameter_apply_allowed",
    "parameter_staging_write_allowed",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _nested(mapping: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = mapping.get(key)
    return value if isinstance(value, Mapping) else {}


def _read_json(path: Path, *, max_bytes: int = MAX_LATEST_BYTES) -> tuple[dict[str, Any], dict[str, Any]]:
    meta = {
        "path": str(path),
        "path_exists": path.exists(),
        "file_size_bytes": None,
        "actual_file_read_attempted": False,
        "actual_file_read_succeeded": False,
        "payload_decode_attempted": False,
        "payload_decode_succeeded": False,
        "exception_class": "",
        "exception_message": "",
    }
    if not path.exists():
        return {}, meta
    try:
        size = path.stat().st_size
        meta["file_size_bytes"] = size
        if size > max_bytes:
            meta["exception_class"] = "FileTooLarge"
            meta["exception_message"] = f"{size} > {max_bytes}"
            return {}, meta
        meta["actual_file_read_attempted"] = True
        text = path.read_text(encoding="utf-8-sig")
        meta["actual_file_read_succeeded"] = True
        meta["payload_decode_attempted"] = True
        data = json.loads(text)
        meta["payload_decode_succeeded"] = isinstance(data, dict)
        return (data if isinstance(data, dict) else {}), meta
    except Exception as exc:  # noqa: BLE001 - audit report should capture any read/decode failure.
        meta["exception_class"] = type(exc).__name__
        meta["exception_message"] = str(exc)
        return {}, meta


def _extract_records(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    forecast_batch = _nested(payload, "forecast_batch")
    records = _as_list(forecast_batch.get("records"))
    return [item for item in records if isinstance(item, Mapping)]


def _extract_prediction_run_id(payload: Mapping[str, Any]) -> str:
    for key in ("prediction_run_id", "run_id"):
        value = payload.get(key)
        if value:
            return str(value)
    forecast_batch = _nested(payload, "forecast_batch")
    return str(forecast_batch.get("batch_id") or "")


def _extract_generated_at(payload: Mapping[str, Any]) -> str:
    for key in ("generated_at", "exported_at", "created_at"):
        value = payload.get(key)
        if value:
            return str(value)
    forecast_batch = _nested(payload, "forecast_batch")
    return str(forecast_batch.get("generated_at") or "")


def _extract_market_uid(payload: Mapping[str, Any]) -> str:
    for key in ("market_uid", "symbol", "instrument"):
        value = payload.get(key)
        if value:
            return str(value)
    for record in _extract_records(payload):
        value = record.get("market_uid")
        if value:
            return str(value)
    return ""


def _unique_nonempty(values: list[Any]) -> list[str]:
    return sorted({str(item) for item in values if str(item or "").strip()})


def _record_summary(records: list[Mapping[str, Any]]) -> dict[str, Any]:
    families = _unique_nonempty([record.get("family") for record in records])
    horizons = _unique_nonempty([record.get("horizon_key") or record.get("horizon_label") for record in records])
    parameter_sets = _unique_nonempty([record.get("parameter_set_id") for record in records])
    logic_versions = _unique_nonempty([record.get("logic_version") for record in records])
    warnings: list[str] = []
    blockers: list[str] = []
    signal_values: list[int] = []
    reference_values: list[int] = []
    source_quality_warning_count = 0
    for record in records:
        warnings.extend(str(item) for item in _as_list(record.get("warnings")))
        blockers.extend(str(item) for item in _as_list(record.get("blockers")))
        values = _nested(record, "values_snapshot")
        for key, target in (
            ("estimated_signal_strength_percent", signal_values),
            ("estimated_reference_hit_rate_percent", reference_values),
        ):
            try:
                if values.get(key) is not None:
                    target.append(int(values.get(key)))
            except (TypeError, ValueError):
                pass
        if any("source_quality" in str(item) for item in _as_list(record.get("warnings"))):
            source_quality_warning_count += 1
    return {
        "record_count": len(records),
        "usable_record_count": sum(1 for record in records if record.get("usable") is True),
        "family_count": len(families),
        "families": families,
        "horizon_count": len(horizons),
        "horizons": horizons,
        "parameter_set_count": len(parameter_sets),
        "parameter_set_ids_sample": parameter_sets[:12],
        "logic_versions": logic_versions,
        "warning_count": len(warnings),
        "unique_warning_count": len(set(warnings)),
        "warning_samples": sorted(set(warnings))[:12],
        "blocker_count": len(blockers),
        "unique_blocker_count": len(set(blockers)),
        "blocker_samples": sorted(set(blockers))[:12],
        "source_quality_warning_record_count": source_quality_warning_count,
        "signal_strength_min": min(signal_values) if signal_values else None,
        "signal_strength_max": max(signal_values) if signal_values else None,
        "reference_hit_rate_min": min(reference_values) if reference_values else None,
        "reference_hit_rate_max": max(reference_values) if reference_values else None,
        "record_sample": [
            {
                "family": record.get("family"),
                "horizon": record.get("horizon_key"),
                "primary_label": record.get("primary_label"),
                "score": record.get("score"),
                "confidence": record.get("confidence"),
                "warnings": _as_list(record.get("warnings"))[:4],
            }
            for record in records[:5]
        ],
    }


def _scenario_trace_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    scenario_core = _nested(payload, "scenario_core")
    scenario_trace = _nested(scenario_core, "scenario_trace") or _nested(payload, "scenario_trace")
    keys = sorted(str(key) for key in scenario_trace.keys()) if scenario_trace else []
    return {
        "scenario_core_present": bool(scenario_core),
        "scenario_trace_present": bool(scenario_trace),
        "scenario_trace_keys": keys,
        "evidence_weighting_trace_present": any("evidence" in key and "weight" in key for key in keys),
        "invalidation_rewrite_trace_present": any("invalidation" in key or "rewrite" in key for key in keys),
        "scenario_switch_trace_present": any("switch" in key for key in keys),
        "gpt_review_digest_present": bool(_nested(scenario_core, "gpt_review_digest")),
    }


def _calibration_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "calibration_refs_count": len(_as_list(payload.get("calibration_refs"))),
        "calibration_refs_present": bool(_as_list(payload.get("calibration_refs"))),
        "replay_feedback_present": bool(payload.get("replay_feedback") or payload.get("replay_feedback_summary")),
        "forecast_batch_present": bool(_nested(payload, "forecast_batch")),
    }


def _producer_summary(status: Mapping[str, Any]) -> dict[str, Any]:
    safe_flags = _nested(status, "safe_flags")
    return {
        "status_present": bool(status),
        "producer_state": status.get("producer_state", ""),
        "producer_enabled": status.get("producer_enabled"),
        "scheduler_enabled": status.get("scheduler_enabled"),
        "last_success_generated_at": status.get("last_success_generated_at", ""),
        "freshness_max_age_sec": status.get("freshness_max_age_sec"),
        "recommended_cadence_sec": status.get("recommended_cadence_sec"),
        "last_warning_count": status.get("last_warning_count"),
        "safe_flag_count": len(safe_flags),
        "safe_flags_false_boundaries_ok": all(bool(value) for value in safe_flags.values()) if safe_flags else False,
    }


def _safe_boundary_summary(payload: Mapping[str, Any], records: list[Mapping[str, Any]]) -> dict[str, Any]:
    unsafe: list[str] = []
    for key in FORBIDDEN_FALSE_BOUNDARIES:
        if payload.get(key) is True:
            unsafe.append(f"payload.{key}=true")
    for index, record in enumerate(records[:20]):
        for key in ("would_append_ledger", "would_send_to_broker", "would_write_runtime_artifact", "broker_execution_requested", "mode_apply_requested", "command_ledger_append_requested"):
            if record.get(key) is True:
                unsafe.append(f"records[{index}].{key}=true")
    return {
        "unsafe_boundary_count": len(unsafe),
        "unsafe_boundary_samples": unsafe[:20],
        "read_only_output": payload.get("read_only") is True or all(record.get("read_only") is True for record in records[:20]),
        "non_executing_output": payload.get("non_executing") is True or all(record.get("non_executing") is True for record in records[:20]),
        "no_broker_or_ledger_or_runtime_write_flags_detected": not unsafe,
    }


def _widget_row(widget_id: str, state: str, confidence: str, blockers: list[str], warnings: list[str], source_fields: list[str]) -> dict[str, Any]:
    return {
        "widget_id": widget_id,
        "state": state,
        "confidence": confidence,
        "blockers": blockers,
        "warnings": warnings,
        "source_fields": source_fields,
        "read_only": True,
        "realtime_widget_design_premise": True,
        "write_or_apply_allowed": False,
    }


def _build_widget_readiness(
    *,
    payload: Mapping[str, Any],
    previous_payload: Mapping[str, Any],
    records: list[Mapping[str, Any]],
    record_summary: Mapping[str, Any],
    scenario_summary: Mapping[str, Any],
    calibration_summary: Mapping[str, Any],
    producer_summary: Mapping[str, Any],
    safe_summary: Mapping[str, Any],
) -> list[dict[str, Any]]:
    prediction_run_id = _extract_prediction_run_id(payload)
    generated_at = _extract_generated_at(payload)
    rows: list[dict[str, Any]] = []
    rows.append(_widget_row(
        "latest_prediction_summary_widget",
        "ready" if prediction_run_id and generated_at and records else "gap",
        "medium" if records else "low",
        [] if records else ["latest_prediction_records_missing"],
        [] if prediction_run_id and generated_at else ["prediction_run_id_or_generated_at_missing"],
        ["prediction_run_id", "generated_at", "market_uid", "forecast_batch.records"],
    ))
    rows.append(_widget_row(
        "prediction_delta_widget",
        "ready" if previous_payload else "gap",
        "low" if not previous_payload else "medium",
        ["previous_prediction_payload_not_supplied"] if not previous_payload else [],
        ["delta_widget_requires_previous_latest_snapshot_or_history"] if not previous_payload else [],
        ["current.prediction_run_id", "previous.prediction_run_id", "records.primary_label", "records.score"],
    ))
    rows.append(_widget_row(
        "scenario_trace_widget",
        "ready" if scenario_summary.get("scenario_trace_present") else "partial" if records else "gap",
        "medium" if scenario_summary.get("scenario_trace_present") else "low",
        [] if records else ["forecast_records_missing"],
        [] if scenario_summary.get("scenario_trace_present") else ["scenario_trace_missing_or_not_top_level_visible"],
        ["scenario_core.scenario_trace", "forecast_batch.records.family", "forecast_batch.records.primary_label"],
    ))
    rows.append(_widget_row(
        "evidence_weighting_widget",
        "ready" if scenario_summary.get("evidence_weighting_trace_present") else "partial" if record_summary.get("source_quality_warning_record_count", 0) >= 0 and records else "gap",
        "medium" if scenario_summary.get("evidence_weighting_trace_present") else "low",
        [] if records else ["records_missing"],
        [] if scenario_summary.get("evidence_weighting_trace_present") else ["evidence_weighting_trace_not_confirmed_in_payload"],
        ["scenario_trace.evidence_weighting_trace", "records.values_snapshot.source_contribution_ledger"],
    ))
    rows.append(_widget_row(
        "invalidation_rewrite_widget",
        "ready" if scenario_summary.get("invalidation_rewrite_trace_present") else "partial" if records else "gap",
        "medium" if scenario_summary.get("invalidation_rewrite_trace_present") else "low",
        [] if records else ["records_missing"],
        [] if scenario_summary.get("invalidation_rewrite_trace_present") else ["invalidation_rewrite_trace_not_confirmed_in_payload"],
        ["scenario_trace.invalidation_rewrite_trace", "records.warnings", "records.primary_label"],
    ))
    rows.append(_widget_row(
        "source_quality_freshness_widget",
        "ready" if record_summary.get("source_quality_warning_record_count", 0) or producer_summary.get("status_present") else "partial",
        "medium",
        [],
        ["source_quality_warning_records_present"] if record_summary.get("source_quality_warning_record_count", 0) else ["source_quality_gate_state_not_observed"],
        ["records.warnings", "records.values_snapshot.source_quality_gate_state", "producer_status.last_success_generated_at"],
    ))
    rows.append(_widget_row(
        "warning_blocker_widget",
        "ready" if records else "gap",
        "medium" if records else "low",
        [] if records else ["records_missing"],
        list(record_summary.get("warning_samples", []))[:5],
        ["payload.blockers", "records.blockers", "records.warnings"],
    ))
    rows.append(_widget_row(
        "signal_strength_calibration_widget",
        "partial" if record_summary.get("signal_strength_min") is not None else "gap",
        "low" if not calibration_summary.get("calibration_refs_present") else "medium",
        [] if record_summary.get("signal_strength_min") is not None else ["signal_strength_values_missing"],
        ["calibration_refs_missing"] if not calibration_summary.get("calibration_refs_present") else [],
        ["records.values_snapshot.estimated_signal_strength_percent", "records.values_snapshot.estimated_reference_hit_rate_percent", "calibration_refs"],
    ))
    rows.append(_widget_row(
        "parameter_candidate_comparison_widget",
        "partial" if record_summary.get("parameter_set_count", 0) else "gap",
        "low",
        [] if record_summary.get("parameter_set_count", 0) else ["parameter_set_ids_missing"],
        ["baseline_candidate_rollback_comparison_not_confirmed"],
        ["records.parameter_set_id", "tactic_proposal_outputs", "parameter_trace", "rollback_target_ref"],
    ))
    rows.append(_widget_row(
        "replay_outcome_calibration_widget",
        "ready" if calibration_summary.get("replay_feedback_present") or calibration_summary.get("calibration_refs_present") else "gap",
        "low" if not calibration_summary.get("calibration_refs_present") else "medium",
        ["replay_or_calibration_refs_missing"] if not calibration_summary.get("calibration_refs_present") else [],
        [],
        ["calibration_refs", "replay_feedback", "prediction_evaluation_entries"],
    ))
    rows.append(_widget_row(
        "producer_freshness_status_widget",
        "ready" if producer_summary.get("status_present") else "gap",
        "medium" if producer_summary.get("status_present") else "low",
        [] if producer_summary.get("status_present") else ["producer_status_not_supplied_or_not_read"],
        [],
        ["prediction/status/non_ui_scheduled_producer_status.json"],
    ))
    rows.append(_widget_row(
        "runtime_boundary_safety_widget",
        "ready" if safe_summary.get("no_broker_or_ledger_or_runtime_write_flags_detected") else "blocked",
        "high" if safe_summary.get("no_broker_or_ledger_or_runtime_write_flags_detected") else "low",
        list(safe_summary.get("unsafe_boundary_samples", [])),
        [],
        ["payload false-boundary flags", "records false-boundary flags", "producer_status.safe_flags"],
    ))
    return rows


def _readiness_state(widget_rows: list[Mapping[str, Any]]) -> str:
    if any(row.get("state") == "blocked" for row in widget_rows):
        return "blocked_unsafe_boundary"
    ready_count = sum(1 for row in widget_rows if row.get("state") == "ready")
    partial_count = sum(1 for row in widget_rows if row.get("state") == "partial")
    gap_count = sum(1 for row in widget_rows if row.get("state") == "gap")
    if ready_count >= 5 and partial_count >= 3 and gap_count <= 3:
        return "real_output_audit_ready_with_inference_quality_gaps"
    if ready_count >= 3:
        return "real_output_present_but_widget_input_gaps"
    return "real_output_not_ready_for_widget_mapping"


def build_report(
    *,
    supplied_payload: Mapping[str, Any] | Any | None = None,
    supplied_previous_payload: Mapping[str, Any] | Any | None = None,
    supplied_producer_status: Mapping[str, Any] | Any | None = None,
    hot_root: str = DEFAULT_HOT_ROOT,
    operator_acknowledged: bool = False,
    allow_actual_read: bool = False,
    allow_missing_status: bool = True,
) -> dict[str, Any]:
    payload = _as_mapping(supplied_payload)
    previous_payload = _as_mapping(supplied_previous_payload)
    producer_status = _as_mapping(supplied_producer_status)
    latest_read_meta: Mapping[str, Any] = {}
    status_read_meta: Mapping[str, Any] = {}
    blocked_reasons: list[str] = []
    warning_reasons: list[str] = []

    if not payload:
        if not operator_acknowledged:
            blocked_reasons.append("operator_acknowledgement_required_before_d_hot_actual_read")
        if not allow_actual_read:
            blocked_reasons.append("allow_actual_read_required_before_d_hot_actual_read")
        if operator_acknowledged and allow_actual_read:
            root = Path(hot_root)
            payload, latest_read_meta = _read_json(root / LATEST_RELATIVE_PATH)
            if not payload:
                blocked_reasons.append("latest_prediction_payload_read_or_decode_failed")
            if not producer_status:
                producer_status, status_read_meta = _read_json(root / PRODUCER_STATUS_RELATIVE_PATH, max_bytes=500_000)
                if not producer_status and not allow_missing_status:
                    blocked_reasons.append("producer_status_payload_read_or_decode_failed")
    else:
        latest_read_meta = {
            "path": "supplied_payload",
            "path_exists": True,
            "actual_file_read_attempted": False,
            "actual_file_read_succeeded": False,
            "payload_decode_attempted": False,
            "payload_decode_succeeded": True,
        }
        if producer_status:
            status_read_meta = {"path": "supplied_producer_status", "payload_decode_succeeded": True}

    records = _extract_records(payload)
    record_summary = _record_summary(records)
    scenario_summary = _scenario_trace_summary(payload)
    calibration = _calibration_summary(payload)
    producer = _producer_summary(producer_status)
    safe_summary = _safe_boundary_summary(payload, records)
    widget_rows = _build_widget_readiness(
        payload=payload,
        previous_payload=previous_payload,
        records=records,
        record_summary=record_summary,
        scenario_summary=scenario_summary,
        calibration_summary=calibration,
        producer_summary=producer,
        safe_summary=safe_summary,
    )
    if not records:
        blocked_reasons.append("forecast_batch_records_missing")
    if record_summary.get("source_quality_warning_record_count", 0):
        warning_reasons.append("source_quality_warnings_present_in_records")
    if not calibration.get("calibration_refs_present"):
        warning_reasons.append("calibration_refs_missing")
    if not previous_payload:
        warning_reasons.append("previous_payload_missing_delta_widget_gap")
    readiness_state = _readiness_state(widget_rows)
    ok = bool(payload and records and not safe_summary.get("unsafe_boundary_count") and not [item for item in blocked_reasons if item != "forecast_batch_records_missing"])
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "stage": "prediction_engine_real_output_readiness_audit",
        "generated_at": _utc_now(),
        "hot_root": str(hot_root),
        "latest_relative_path": LATEST_RELATIVE_PATH,
        "producer_status_relative_path": PRODUCER_STATUS_RELATIVE_PATH,
        "operator_acknowledged": bool(operator_acknowledged),
        "allow_actual_read_requested": bool(allow_actual_read),
        "latest_read_meta": dict(latest_read_meta),
        "producer_status_read_meta": dict(status_read_meta),
        "prediction_run_id": _extract_prediction_run_id(payload),
        "prediction_generated_at": _extract_generated_at(payload),
        "market_uid": _extract_market_uid(payload),
        "readiness_state": readiness_state,
        "record_summary": dict(record_summary),
        "scenario_trace_summary": dict(scenario_summary),
        "calibration_summary": dict(calibration),
        "producer_status_summary": dict(producer),
        "safe_boundary_summary": dict(safe_summary),
        "widget_readiness_rows": widget_rows,
        "widget_ready_count": sum(1 for row in widget_rows if row.get("state") == "ready"),
        "widget_partial_count": sum(1 for row in widget_rows if row.get("state") == "partial"),
        "widget_gap_count": sum(1 for row in widget_rows if row.get("state") == "gap"),
        "blocked_reasons": list(dict.fromkeys(blocked_reasons)),
        "warning_reasons": list(dict.fromkeys(warning_reasons)),
        "human_interpretation": "This audit checks whether the real latest Prediction System output is ready to feed future content-specific realtime WarRoom widgets. It is not a UI cleanup, not parameter staging/apply, and not execution approval.",
        "recommended_next_slice": "PS-Q17B inference quality gap plan: source-quality cap, calibration refs, delta history, scenario trace confirmation, and parameter candidate evidence.",
        "read_only": True,
        "non_executing": True,
        "actual_read_audit_only": True,
        "warroom_widget_design_premise": True,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
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
    parser = argparse.ArgumentParser(description="PS-Q17A Prediction Engine real-output readiness audit")
    parser.add_argument("--hot-root", default=DEFAULT_HOT_ROOT)
    parser.add_argument("--operator-ack", action="store_true")
    parser.add_argument("--allow-actual-read", action="store_true")
    parser.add_argument("--require-producer-status", action="store_true")
    args = parser.parse_args(argv)
    payload = build_report(
        hot_root=args.hot_root,
        operator_acknowledged=args.operator_ack,
        allow_actual_read=args.allow_actual_read,
        allow_missing_status=not args.require_producer_status,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
