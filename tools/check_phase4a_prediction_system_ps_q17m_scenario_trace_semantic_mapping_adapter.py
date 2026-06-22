# path: ./tools/check_phase4a_prediction_system_ps_q17m_scenario_trace_semantic_mapping_adapter.py
# desc: PS-Q17M standalone scenario-trace semantic mapping adapter. It consumes supplied scenario trace fixtures only and emits a normalized review packet; it never reads D-hot or scenario traces, writes artifacts, invokes refresh, renders WarRoom widgets, claims trace reliability, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17l_scenario_trace_semantic_mapping_contract import CHECKER_VERSION as PS_Q17L_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17l_scenario_trace_semantic_mapping_contract import REQUIRED_TRACE_FIELDS, build_report as build_ps_q17l_report

CHECKER = "ps_q17m_scenario_trace_semantic_mapping_adapter"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17m_scenario_trace_semantic_mapping_adapter.v1"
PS_Q17L_SOURCE_CHECKER_VERSION = PS_Q17L_CHECKER_VERSION
ADAPTER_VERSION = "scenario_trace_semantic_mapping_adapter.v1"
TRACE_PACKET_VERSION = "scenario_trace_semantic_mapping_review_packet.v1"
SEMANTIC_TRACE_FIELDS = (
    "evidence_weighting",
    "invalidation_rewrite",
    "scenario_switch",
)


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


def _safe_q17l_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17L_SOURCE_CHECKER_VERSION:
        failures.append("q17l_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17l_report_not_ok")
    if report.get("contract_only") is not True:
        failures.append("q17l_contract_only_missing")
    for key in (
        "warroom_widget_implementation_allowed",
        "scenario_trace_actual_read_allowed",
        "scenario_trace_widget_rendering_allowed",
        "scenario_trace_reliability_claim_allowed",
        "evidence_weighting_reliability_claim_allowed",
        "invalidation_rewrite_reliability_claim_allowed",
        "scenario_switch_reliability_claim_allowed",
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
            failures.append(f"q17l_boundary_not_false:{key}")
    contracts = _contract_map(report)
    for required in (
        "scenario_trace_source_key_contract",
        "evidence_weighting_trace_semantic_contract",
        "invalidation_rewrite_trace_semantic_contract",
        "scenario_switch_trace_semantic_contract",
        "warroom_scenario_trace_release_gate_contract",
    ):
        row = contracts.get(required, {})
        if not row:
            failures.append(f"q17l_required_contract_missing:{required}")
        elif row.get("priority") != "P0" or row.get("blocks_scenario_trace_reliability_claim") is not True:
            failures.append(f"q17l_required_contract_not_p0_blocking:{required}")
    return not failures, failures


def _fixture_q17l_contract_report() -> dict[str, Any]:
    return build_ps_q17l_report(use_observed_fixture=True)


def _fixture_scenario_trace() -> dict[str, Any]:
    return {
        "source_artifact_ref": "fixture://prediction/scenario_trace.json",
        "scenario_core": {
            "generated_at": "2026-06-22T01:30:00Z",
            "scenario_trace_keys": [
                "context_evidence_profiles",
                "tier0_source_quality_gate",
                "what_to_watch_next",
                "invalidation_rewrite_candidates",
            ],
        },
        "semantic_mapping": {
            "evidence_weighting_trace_key": "context_evidence_profiles",
            "invalidation_rewrite_trace_key": "invalidation_rewrite_candidates",
            "scenario_switch_trace_key": "what_to_watch_next",
            "evidence_weighting_semantic_state": "mapped_review_only",
            "invalidation_rewrite_semantic_state": "mapped_review_only",
            "scenario_switch_semantic_state": "mapped_review_only",
        },
        "operator_explanation_trace_taxonomy": {
            "evidence_label": "Evidence weighting",
            "invalidation_label": "Invalidation / rewrite candidates",
            "scenario_switch_label": "Scenario switch watchlist",
        },
    }


def _semantic_key(mapping: Mapping[str, Any], name: str) -> str:
    return str(mapping.get(f"{name}_trace_key") or "")


def adapt_scenario_trace(payload: Mapping[str, Any] | Any) -> dict[str, Any]:
    data = _as_mapping(payload)
    scenario_core = _as_mapping(data.get("scenario_core"))
    mapping = _as_mapping(data.get("semantic_mapping"))
    taxonomy = _as_mapping(data.get("operator_explanation_trace_taxonomy"))
    trace_keys = [str(item) for item in _as_list(scenario_core.get("scenario_trace_keys"))]
    mapped_keys: list[str] = []
    semantic_mapping: dict[str, Any] = {}
    missing_reason_codes: list[str] = []
    for name in SEMANTIC_TRACE_FIELDS:
        key = _semantic_key(mapping, name)
        present = bool(key and key in trace_keys)
        mapped_keys.append(key) if present else None
        semantic_mapping[f"{name}_trace_key"] = key
        semantic_mapping[f"{name}_trace_present"] = present
        semantic_mapping[f"{name}_semantic_state"] = str(mapping.get(f"{name}_semantic_state") or ("mapped_review_only" if present else "missing_or_unverified"))
        if not present:
            if name == "evidence_weighting":
                missing_reason_codes.append("evidence_weighting_trace_present=false")
            elif name == "invalidation_rewrite":
                missing_reason_codes.append("invalidation_rewrite_trace_present=false")
            elif name == "scenario_switch":
                missing_reason_codes.append("scenario_switch_trace_present=false")
    unmapped = [key for key in trace_keys if key not in mapped_keys]
    all_mapped = all(bool(semantic_mapping.get(f"{name}_trace_present")) for name in SEMANTIC_TRACE_FIELDS)
    semantic_mapping["semantic_confidence_state"] = "mapped_review_only_unreleased" if all_mapped else "incomplete_review_only"
    semantic_mapping["unmapped_trace_keys"] = unmapped
    blocking_reason_codes = missing_reason_codes + ["adapter_stage_no_scenario_trace_reliability_release"]
    return {
        "adapter_version": ADAPTER_VERSION,
        "trace_packet_version": TRACE_PACKET_VERSION,
        "scenario_trace": {
            "source_artifact_ref": str(data.get("source_artifact_ref") or ""),
            "scenario_core": {
                "generated_at": str(scenario_core.get("generated_at") or ""),
                "scenario_trace_keys": trace_keys,
            },
            "semantic_mapping": semantic_mapping,
            "operator_explanation_trace_taxonomy": {
                "evidence_label": str(taxonomy.get("evidence_label") or "Evidence weighting"),
                "invalidation_label": str(taxonomy.get("invalidation_label") or "Invalidation / rewrite"),
                "scenario_switch_label": str(taxonomy.get("scenario_switch_label") or "Scenario switch"),
                "unmapped_trace_keys": unmapped,
            },
        },
        "warroom_scenario_trace_release_gate": {
            "semantic_mapping_present": all_mapped,
            "evidence_reliability_claim_allowed": False,
            "invalidation_reliability_claim_allowed": False,
            "scenario_switch_reliability_claim_allowed": False,
            "render_allowed": False,
            "blocking_reason_codes": blocking_reason_codes,
        },
        "contract_completeness": {
            "required_trace_fields": list(REQUIRED_TRACE_FIELDS),
            "has_source_artifact_ref": bool(data.get("source_artifact_ref")),
            "has_scenario_core_keys": bool(trace_keys),
            "has_evidence_mapping": bool(semantic_mapping.get("evidence_weighting_trace_present")),
            "has_invalidation_mapping": bool(semantic_mapping.get("invalidation_rewrite_trace_present")),
            "has_scenario_switch_mapping": bool(semantic_mapping.get("scenario_switch_trace_present")),
            "has_release_gate": True,
            "has_operator_taxonomy": True,
        },
        "warroom_scenario_trace_widget": {
            "source_artifact_ref": str(data.get("source_artifact_ref") or ""),
            "mapped_trace_key_count": len(mapped_keys),
            "unmapped_trace_key_count": len(unmapped),
            "operator_explanation": "Scenario trace semantics are normalized for review only; reliability claims and widget rendering remain deferred.",
            "render_allowed": False,
        },
        "read_only": True,
        "write_or_apply_allowed": False,
        "scenario_trace_actual_read_allowed": False,
        "scenario_trace_widget_rendering_allowed": False,
    }


def _adapter_valid(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    scenario_trace = _as_mapping(packet.get("scenario_trace"))
    release = _as_mapping(packet.get("warroom_scenario_trace_release_gate"))
    completeness = _as_mapping(packet.get("contract_completeness"))
    warroom = _as_mapping(packet.get("warroom_scenario_trace_widget"))
    semantic = _as_mapping(scenario_trace.get("semantic_mapping"))
    if semantic.get("semantic_confidence_state") != "mapped_review_only_unreleased":
        failures.append("semantic_confidence_state_not_review_only_unreleased")
    if release.get("semantic_mapping_present") is not True:
        failures.append("semantic_mapping_present_not_true")
    for key in ("evidence_reliability_claim_allowed", "invalidation_reliability_claim_allowed", "scenario_switch_reliability_claim_allowed", "render_allowed"):
        if release.get(key) is not False:
            failures.append(f"release_gate_must_stay_false:{key}")
    if warroom.get("render_allowed") is not False:
        failures.append("warroom_render_must_stay_false")
    for key in ("has_source_artifact_ref", "has_scenario_core_keys", "has_evidence_mapping", "has_invalidation_mapping", "has_scenario_switch_mapping", "has_release_gate", "has_operator_taxonomy"):
        if completeness.get(key) is not True:
            failures.append(f"contract_completeness_false:{key}")
    return not failures, failures


def build_report(*, supplied_q17l_report: Mapping[str, Any] | Any | None = None, supplied_scenario_trace: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17l_report = _as_mapping(supplied_q17l_report)
    scenario_trace = _as_mapping(supplied_scenario_trace)
    if not q17l_report and use_observed_fixture:
        q17l_report = _fixture_q17l_contract_report()
    if not scenario_trace and use_observed_fixture:
        scenario_trace = _fixture_scenario_trace()
    safe_q17l, validation_failures = _safe_q17l_boundary(q17l_report)
    packet = adapt_scenario_trace(scenario_trace) if safe_q17l and scenario_trace else {}
    adapter_valid, adapter_failures = _adapter_valid(packet) if packet else (False, ["scenario_trace_missing_or_q17l_invalid"])
    ok = bool(safe_q17l and adapter_valid)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "stage": "scenario_trace_semantic_mapping_adapter_before_reliability_and_widget_rendering",
        "source_checker_version": PS_Q17L_SOURCE_CHECKER_VERSION,
        "source_q17l_report_valid": safe_q17l,
        "source_q17l_validation_failures": validation_failures,
        "adapter_valid": adapter_valid,
        "adapter_validation_failures": adapter_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "adapted_packet": packet,
        "recommended_next_slice": "PS-Q17N parameter-candidate evidence contract or WarRoom prediction widget integration design checkpoint; confidence increase, parameter apply, and WarRoom widget rendering remain deferred.",
        "human_interpretation": "PS-Q17M proves supplied scenario trace semantics can be normalized into a review-only mapping packet. It does not read scenario traces or D-hot, claim reliability, render widgets, write artifacts, or trigger generation.",
        "read_only": True,
        "non_executing": True,
        "adapter_only": True,
        "contract_only": True,
        "diagnostic_only": True,
        "warroom_widget_design_premise": True,
        "warroom_widget_implementation_allowed": False,
        "scenario_trace_actual_read_allowed": False,
        "scenario_trace_widget_rendering_allowed": False,
        "scenario_trace_reliability_claim_allowed": False,
        "evidence_weighting_reliability_claim_allowed": False,
        "invalidation_rewrite_reliability_claim_allowed": False,
        "scenario_switch_reliability_claim_allowed": False,
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
    parser = argparse.ArgumentParser(description="PS-Q17M scenario-trace semantic mapping adapter")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use static Q17L and scenario trace fixtures; no D-hot/scenario-trace read is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
