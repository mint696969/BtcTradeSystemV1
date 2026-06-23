# path: ./tools/check_phase4a_prediction_system_ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe.py
# desc: PS-Q18B checker for one explicitly allowed bounded read-only JSON actual-source probe. Observed fixture uses a temporary JSON fixture; no WarRoom page mutation, D-hot discovery, refresh, writes, AutoTrade, or broker behavior.

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping

BTCTS_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "btcts_next", "src")
if BTCTS_SRC not in sys.path:
    sys.path.insert(0, BTCTS_SRC)

from check_phase4a_prediction_system_ps_q18a_warroom_prediction_widget_source_artifact_resolution_preflight import CHECKER_VERSION as PS_Q18A_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q18a_warroom_prediction_widget_source_artifact_resolution_preflight import build_report as build_ps_q18a_report
from btcts.apps.operator_ui.components.prediction_warroom_prediction_widget_bounded_actual_source_read_probe import ALLOW_ACK, BOUNDED_ACTUAL_SOURCE_READ_PROBE_VERSION, build_prediction_warroom_prediction_widget_bounded_actual_source_read_probe_packet

CHECKER = "ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe.v1"
BOUNDED_ACTUAL_SOURCE_READ_PROBE_CHECK_VERSION = "warroom_prediction_widget_bounded_actual_source_read_probe.v1"
PS_Q18A_SOURCE_CHECKER_VERSION = PS_Q18A_CHECKER_VERSION
DEFAULT_PROBE_SOURCE_PACKET_ID = "latest_prediction_source_review_packet"
DEFAULT_PROBE_SOURCE_ARTIFACT_REF_FIELD = "latest_prediction.source_artifact_ref"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _safe_q18a_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q18A_SOURCE_CHECKER_VERSION:
        failures.append("q18a_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q18a_report_not_ok")
    if report.get("artifact_resolution_row_count") != 12:
        failures.append("q18a_artifact_resolution_row_count_mismatch")
    if report.get("unique_artifact_resolution_key_count") != 9:
        failures.append("q18a_unique_resolution_key_count_mismatch")
    if report.get("source_artifact_resolution_preflight_ready") is not True:
        failures.append("q18a_preflight_not_ready")
    for key in (
        "source_artifact_resolution_allowed",
        "source_artifact_resolved",
        "source_artifact_path_materialized",
        "source_artifact_exists_checked",
        "source_artifact_schema_checked",
        "actual_source_bound",
        "actual_source_read_allowed",
        "d_hot_actual_read_allowed",
        "freshness_checked_against_d_hot",
        "real_prediction_widget_rendering_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_page_mutation_allowed",
        "warroom_ui_trigger_enabled",
        "refresh_invocation_allowed",
        "scheduler_enabled",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "confidence_increase_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
    ):
        if report.get(key) is not False:
            failures.append(f"q18a_boundary_not_false:{key}")
    return not failures, failures


def _safe_probe_packet(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if packet.get("probe_version") != BOUNDED_ACTUAL_SOURCE_READ_PROBE_VERSION:
        failures.append("probe_version_mismatch")
    if packet.get("ok") is not True:
        failures.append("probe_packet_not_ok")
    for key in (
        "explicit_source_path_supplied",
        "explicit_ack_matched",
        "allow_actual_read_requested",
        "path_exists_checked",
        "path_exists",
        "actual_file_read_attempted",
        "actual_file_read_succeeded",
        "payload_decode_attempted",
        "payload_decode_succeeded",
        "schema_probe_checked",
        "schema_probe_ok",
        "read_only",
        "non_executing",
        "bounded_actual_source_read_probe_only",
        "single_file_probe_only",
    ):
        if packet.get(key) is not True:
            failures.append(f"probe_true_boundary_missing:{key}")
    for key in (
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "warroom_page_mutation_allowed",
        "warroom_widget_rendering_allowed",
        "real_prediction_widget_rendering_allowed",
        "refresh_invocation_allowed",
        "scheduler_enabled",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "confidence_increase_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
    ):
        if packet.get(key) is not False:
            failures.append(f"probe_false_boundary_not_false:{key}")
    if packet.get("payload_preview_key_count", 0) <= 0:
        failures.append("payload_preview_keys_missing")
    if packet.get("blocker_reasons"):
        failures.append("probe_blockers_present")
    return not failures, failures


def _fixture_probe_path() -> str:
    fixture = {
        "prediction_run_id": "ps_q18b_fixture_run",
        "generated_at": "2026-06-22T00:00:00Z",
        "market_uid": "BTC-USD",
        "source_artifact_ref": "fixture://ps_q18b/latest_prediction.json",
        "read_only_fixture": True,
    }
    tmp = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False)
    with tmp:
        json.dump(fixture, tmp, ensure_ascii=False, sort_keys=True)
    return tmp.name


def _fixture_probe_packet() -> dict[str, Any]:
    path = _fixture_probe_path()
    try:
        return build_prediction_warroom_prediction_widget_bounded_actual_source_read_probe_packet(
            source_packet_id=DEFAULT_PROBE_SOURCE_PACKET_ID,
            source_artifact_ref_field=DEFAULT_PROBE_SOURCE_ARTIFACT_REF_FIELD,
            explicit_source_path=path,
            allow_actual_read=True,
            explicit_ack=ALLOW_ACK,
        )
    finally:
        try:
            Path(path).unlink(missing_ok=True)
        except Exception:
            pass


def build_report(*, supplied_q18a_report: Mapping[str, Any] | Any | None = None, supplied_probe_packet: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q18a_report = _as_mapping(supplied_q18a_report)
    probe_packet = _as_mapping(supplied_probe_packet)
    if use_observed_fixture:
        if not q18a_report:
            q18a_report = build_ps_q18a_report(use_observed_fixture=True)
        if not probe_packet:
            probe_packet = _fixture_probe_packet()
    safe_q18a, q18a_failures = _safe_q18a_boundary(q18a_report)
    safe_probe, probe_failures = _safe_probe_packet(probe_packet) if safe_q18a and probe_packet else (False, [] if probe_packet else ["probe_packet_missing"])
    ok = bool(safe_q18a and safe_probe)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "bounded_actual_source_read_probe_check_version": BOUNDED_ACTUAL_SOURCE_READ_PROBE_CHECK_VERSION,
        "stage": "warroom_prediction_widget_bounded_actual_source_read_probe_before_warroom_binding_real_widget_rendering_and_refresh",
        "source_q18a_checker_version": PS_Q18A_SOURCE_CHECKER_VERSION,
        "source_q18a_report_valid": safe_q18a,
        "source_q18a_validation_failures": q18a_failures,
        "probe_packet_valid": safe_probe,
        "probe_validation_failures": probe_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "probe_version": BOUNDED_ACTUAL_SOURCE_READ_PROBE_VERSION,
        "probe_source_packet_id": probe_packet.get("source_packet_id") if probe_packet else "",
        "probe_source_artifact_ref_field": probe_packet.get("source_artifact_ref_field") if probe_packet else "",
        "payload_preview_key_count": int(probe_packet.get("payload_preview_key_count") or 0) if probe_packet else 0,
        "recommended_first_validation": "latest_prediction_summary_widget_bounded_actual_source_read_probe_guard" if ok else "",
        "recommended_next_slice": "PS-Q18C WarRoom source read probe status row mount or bounded schema-specific probe; real widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q18B proves a single explicitly supplied JSON source can be read/decode-probed through a bounded read-only path with explicit ack. It does not discover D-hot files, mutate WarRoom, render real widgets, refresh, write artifacts, stage/apply parameters, append ledgers, trigger AutoTrade, or call broker/private APIs.",
        "read_only": True,
        "non_executing": True,
        "bounded_actual_source_read_probe_only": True,
        "single_file_probe_only": True,
        "actual_source_read_allowed": ok,
        "actual_file_read_attempted": bool(probe_packet.get("actual_file_read_attempted")) if probe_packet else False,
        "actual_file_read_succeeded": bool(probe_packet.get("actual_file_read_succeeded")) if probe_packet else False,
        "payload_decode_attempted": bool(probe_packet.get("payload_decode_attempted")) if probe_packet else False,
        "payload_decode_succeeded": bool(probe_packet.get("payload_decode_succeeded")) if probe_packet else False,
        "schema_probe_checked": bool(probe_packet.get("schema_probe_checked")) if probe_packet else False,
        "schema_probe_ok": bool(probe_packet.get("schema_probe_ok")) if probe_packet else False,
        "source_discovery_allowed": False,
        "d_hot_directory_scan_allowed": False,
        "d_hot_actual_read_allowed": False,
        "freshness_checked_against_d_hot": False,
        "warroom_page_mutation_allowed": False,
        "warroom_widget_rendering_allowed": False,
        "real_prediction_widget_rendering_allowed": False,
        "warroom_ui_trigger_enabled": False,
        "refresh_invocation_allowed": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "confidence_increase_allowed": False,
        "signal_reliability_claim_allowed": False,
        "parameter_candidate_reliability_claim_allowed": False,
        "parameter_tuning_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q18B bounded actual-source read probe")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use a temporary JSON fixture; no D-hot discovery, WarRoom mutation, refresh, or write is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
