# path: ./tools/check_phase4a_prediction_system_ps_q17i_prediction_delta_history_adapter.py
# desc: PS-Q17I standalone prediction-delta history adapter. It consumes supplied previous/latest snapshots or static fixtures only and emits a normalized review delta packet; it never reads history or D-hot, writes artifacts, invokes refresh, renders WarRoom widgets, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17h_prediction_delta_history_contract import CHECKER_VERSION as PS_Q17H_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17h_prediction_delta_history_contract import DELTA_REASON_CODES, REQUIRED_DELTA_FIELDS, build_report as build_ps_q17h_report

CHECKER = "ps_q17i_prediction_delta_history_adapter"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17i_prediction_delta_history_adapter.v1"
PS_Q17H_SOURCE_CHECKER_VERSION = PS_Q17H_CHECKER_VERSION
ADAPTER_VERSION = "prediction_delta_history_adapter.v1"
DELTA_PACKET_VERSION = "prediction_delta_review_packet.v1"
JOIN_KEYS = ("market_uid", "family", "horizon_key", "record_id")
COMPARE_FIELDS = ("estimated_signal_strength_percent", "source_quality_gate_state", "scenario_trace_state")


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


def _safe_q17h_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17H_SOURCE_CHECKER_VERSION:
        failures.append("q17h_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17h_report_not_ok")
    if report.get("contract_only") is not True:
        failures.append("q17h_contract_only_missing")
    if report.get("delta_widget_rendering_allowed") is not False:
        failures.append("q17h_delta_widget_boundary_not_false")
    if report.get("history_actual_read_allowed") is not False:
        failures.append("q17h_history_read_boundary_not_false")
    if report.get("d_hot_actual_read_allowed") is not False:
        failures.append("q17h_d_hot_boundary_not_false")
    if report.get("warroom_widget_implementation_allowed") is not False:
        failures.append("q17h_widget_implementation_boundary_not_false")
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
            failures.append(f"q17h_boundary_not_false:{key}")
    contracts = _contract_map(report)
    for required in (
        "previous_latest_snapshot_reference_contract",
        "latest_snapshot_lineage_contract",
        "delta_computation_key_contract",
        "warroom_delta_widget_release_contract",
    ):
        row = contracts.get(required, {})
        if not row:
            failures.append(f"q17h_required_contract_missing:{required}")
        elif row.get("priority") != "P0" or row.get("blocks_realtime_delta_widget") is not True:
            failures.append(f"q17h_required_contract_not_p0_blocking:{required}")
    return not failures, failures


def _fixture_q17h_contract_report() -> dict[str, Any]:
    return build_ps_q17h_report(use_observed_fixture=True)


def _fixture_snapshots() -> dict[str, Any]:
    return {
        "previous_snapshot": {
            "run_id": "fixture.previous.run",
            "generated_at": "2026-06-22T00:00:00Z",
            "source_artifact_ref": "fixture://prediction/previous.json",
            "records": [
                {"record_id": "trend:short", "market_uid": "BTC_JPY:bitFlyer", "family": "trend", "horizon_key": "short", "estimated_signal_strength_percent": 35, "source_quality_gate_state": "fail", "scenario_trace_state": "watch"},
                {"record_id": "mr:short", "market_uid": "BTC_JPY:bitFlyer", "family": "mean_reversion", "horizon_key": "short", "estimated_signal_strength_percent": 32, "source_quality_gate_state": "warn", "scenario_trace_state": "hold"},
            ],
        },
        "latest_snapshot": {
            "run_id": "fixture.latest.run",
            "generated_at": "2026-06-22T00:05:00Z",
            "source_artifact_ref": "fixture://prediction/latest.json",
            "records": [
                {"record_id": "trend:short", "market_uid": "BTC_JPY:bitFlyer", "family": "trend", "horizon_key": "short", "estimated_signal_strength_percent": 40, "source_quality_gate_state": "fail", "scenario_trace_state": "watch"},
                {"record_id": "mr:short", "market_uid": "BTC_JPY:bitFlyer", "family": "mean_reversion", "horizon_key": "short", "estimated_signal_strength_percent": 35, "source_quality_gate_state": "warn", "scenario_trace_state": "recheck"},
            ],
        },
        "history_source_kind": "supplied_fixture_only",
    }


def _record_key(record: Mapping[str, Any]) -> tuple[str, str, str, str]:
    return tuple(str(record.get(key) or "") for key in JOIN_KEYS)  # type: ignore[return-value]


def _record_map(snapshot: Mapping[str, Any]) -> dict[tuple[str, str, str, str], Mapping[str, Any]]:
    result: dict[tuple[str, str, str, str], Mapping[str, Any]] = {}
    for item in _as_list(snapshot.get("records")):
        record = _as_mapping(item)
        key = _record_key(record)
        if all(key):
            result[key] = record
    return result


def _reason_for_field(field: str) -> str:
    return {
        "estimated_signal_strength_percent": "changed_signal_strength",
        "source_quality_gate_state": "changed_source_quality_state",
        "scenario_trace_state": "changed_scenario_trace",
    }.get(field, "changed_scenario_trace")


def adapt_snapshots(payload: Mapping[str, Any] | Any) -> dict[str, Any]:
    data = _as_mapping(payload)
    previous = _as_mapping(data.get("previous_snapshot"))
    latest = _as_mapping(data.get("latest_snapshot"))
    prev_records = _record_map(previous)
    latest_records = _record_map(latest)
    changed_rows: list[dict[str, Any]] = []
    reason_codes: list[str] = []
    for key in sorted(set(prev_records) & set(latest_records)):
        prev = prev_records[key]
        curr = latest_records[key]
        changed_fields: list[dict[str, Any]] = []
        for field in COMPARE_FIELDS:
            if prev.get(field) != curr.get(field):
                reason = _reason_for_field(field)
                reason_codes.append(reason)
                changed_fields.append({"field": field, "previous": prev.get(field), "latest": curr.get(field), "reason_code": reason})
        if changed_fields:
            changed_rows.append({
                "delta_key": {name: value for name, value in zip(JOIN_KEYS, key)},
                "changed_fields": changed_fields,
                "read_only": True,
            })
    blocking_reason_codes: list[str] = []
    if not previous.get("run_id"):
        blocking_reason_codes.append("previous_payload_missing_delta_widget_gap")
    if not latest.get("run_id"):
        blocking_reason_codes.append("latest_snapshot_missing_or_invalid")
    if previous.get("run_id") == latest.get("run_id") and previous.get("run_id"):
        blocking_reason_codes.append("snapshot_lineage_mismatch")
    blocking_reason_codes.append("adapter_stage_no_delta_widget_release")
    history_available = bool(previous.get("run_id") and latest.get("run_id") and prev_records and latest_records)
    return {
        "adapter_version": ADAPTER_VERSION,
        "delta_packet_version": DELTA_PACKET_VERSION,
        "prediction_delta_history": {
            "previous_snapshot": {
                "run_id": str(previous.get("run_id") or ""),
                "generated_at": str(previous.get("generated_at") or ""),
                "source_artifact_ref": str(previous.get("source_artifact_ref") or ""),
            },
            "latest_snapshot": {
                "run_id": str(latest.get("run_id") or ""),
                "generated_at": str(latest.get("generated_at") or ""),
                "source_artifact_ref": str(latest.get("source_artifact_ref") or ""),
            },
            "changed_rows": changed_rows,
            "changed_row_count": len(changed_rows),
            "changed_fields": sorted({item["field"] for row in changed_rows for item in row["changed_fields"]}),
            "delta_reason_codes": sorted(set(reason_codes)),
            "history_source_kind": str(data.get("history_source_kind") or "supplied_only"),
        },
        "prediction_delta_release_gate": {
            "history_available": history_available,
            "widget_reliability_claim_allowed": False,
            "delta_widget_rendering_allowed": False,
            "blocking_reason_codes": blocking_reason_codes,
        },
        "contract_completeness": {
            "required_delta_fields": list(REQUIRED_DELTA_FIELDS),
            "has_previous_snapshot": bool(previous.get("run_id") and previous.get("generated_at") and previous.get("source_artifact_ref")),
            "has_latest_snapshot": bool(latest.get("run_id") and latest.get("generated_at") and latest.get("source_artifact_ref")),
            "has_delta_keys": bool(changed_rows),
            "has_release_gate": True,
        },
        "warroom_delta_review_packet": {
            "render_allowed": False,
            "operator_explanation": "Prediction delta history is normalized for review only; realtime widget rendering and reliability claims remain deferred.",
            "changed_row_count": len(changed_rows),
        },
        "read_only": True,
        "write_or_apply_allowed": False,
        "history_actual_read_allowed": False,
        "delta_widget_rendering_allowed": False,
    }


def _adapter_valid(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    history = _as_mapping(packet.get("prediction_delta_history"))
    release = _as_mapping(packet.get("prediction_delta_release_gate"))
    completeness = _as_mapping(packet.get("contract_completeness"))
    warroom = _as_mapping(packet.get("warroom_delta_review_packet"))
    if not history.get("previous_snapshot") or not history.get("latest_snapshot"):
        failures.append("snapshot_refs_missing")
    if int(history.get("changed_row_count") or 0) < 1:
        failures.append("changed_rows_missing")
    if not _as_list(history.get("delta_reason_codes")):
        failures.append("delta_reason_codes_missing")
    if release.get("history_available") is not True:
        failures.append("history_available_not_true")
    for key in ("widget_reliability_claim_allowed", "delta_widget_rendering_allowed"):
        if release.get(key) is not False:
            failures.append(f"release_gate_must_stay_false:{key}")
    if warroom.get("render_allowed") is not False:
        failures.append("warroom_render_must_stay_false")
    for key in ("has_previous_snapshot", "has_latest_snapshot", "has_delta_keys", "has_release_gate"):
        if completeness.get(key) is not True:
            failures.append(f"contract_completeness_false:{key}")
    return not failures, failures


def build_report(*, supplied_q17h_report: Mapping[str, Any] | Any | None = None, supplied_snapshots: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17h_report = _as_mapping(supplied_q17h_report)
    snapshots = _as_mapping(supplied_snapshots)
    if not q17h_report and use_observed_fixture:
        q17h_report = _fixture_q17h_contract_report()
    if not snapshots and use_observed_fixture:
        snapshots = _fixture_snapshots()
    safe_q17h, validation_failures = _safe_q17h_boundary(q17h_report)
    packet = adapt_snapshots(snapshots) if safe_q17h and snapshots else {}
    adapter_valid, adapter_failures = _adapter_valid(packet) if packet else (False, ["snapshots_missing_or_q17h_invalid"])
    ok = bool(safe_q17h and adapter_valid)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "stage": "prediction_delta_history_adapter_before_realtime_widget_rendering",
        "source_checker_version": PS_Q17H_SOURCE_CHECKER_VERSION,
        "source_q17h_report_valid": safe_q17h,
        "source_q17h_validation_failures": validation_failures,
        "adapter_valid": adapter_valid,
        "adapter_validation_failures": adapter_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "adapted_packet": packet,
        "recommended_next_slice": "PS-Q17J replay-outcome calibration contract or prediction-delta adapter integration design; confidence increase, parameter apply, and WarRoom widget rendering remain deferred.",
        "human_interpretation": "PS-Q17I proves supplied previous/latest snapshots can be normalized into a review-only delta packet. It does not read history or D-hot, compute live deltas, render widgets, write artifacts, or trigger generation.",
        "read_only": True,
        "non_executing": True,
        "adapter_only": True,
        "contract_only": True,
        "diagnostic_only": True,
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
    parser = argparse.ArgumentParser(description="PS-Q17I prediction-delta history adapter")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use static Q17H and snapshot fixtures; no D-hot/history read is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
