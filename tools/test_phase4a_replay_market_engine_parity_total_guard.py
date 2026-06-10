# path: ./tools/test_phase4a_replay_market_engine_parity_total_guard.py
# desc: Phase 4-A replay / market_engine parity total guard integrated with post Phase C boundary guard.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]

GUARD_SPECS = [
    {
        "path": "tools/test_phase4a_post_phasec_total_guard.py",
        "kind": "json_ok",
        "role": "post_phasec_boundary_total_guard",
    },
    {
        "path": "btcts_next/src/btcts/market_engine/tests/test_replay_realtime_parity.py",
        "kind": "plain_ok",
        "role": "replay_realtime_parity",
    },
    {
        "path": "btcts_next/src/btcts/market_engine/tests/test_runtime_orderbook_usage_alignment.py",
        "kind": "plain_ok",
        "role": "runtime_orderbook_usage_alignment",
    },
    {
        "path": "btcts_next/src/btcts/market_engine/tests/test_live_orderbook_semantics_summary.py",
        "kind": "plain_ok",
        "role": "live_orderbook_semantics_summary",
    },
    {
        "path": "btcts_next/src/btcts/market_engine/tests/test_market_state_flow.py",
        "kind": "plain_ok",
        "role": "market_state_flow",
    },
    {
        "path": "btcts_next/src/btcts/market_engine/tests/test_foundation_flow.py",
        "kind": "plain_ok",
        "role": "market_engine_foundation_flow",
    },
    {
        "path": "tools/test_market_engine_short_soak_gate.py",
        "kind": "json_ok",
        "role": "market_engine_short_soak_gate",
    },
    {
        "path": "tools/test_market_engine_interpretation_audit.py",
        "kind": "json_interpretation_audit",
        "role": "market_engine_interpretation_audit",
    },
    {
        "path": "tools/test_l3_event_usage_audit.py",
        "kind": "json_ok",
        "role": "l3_event_usage_policy_audit",
    },
    {
        "path": "btcts_next/src/btcts/processing/l3_market_semantics/orderbook/tests/test_event_usage_policy_contract.py",
        "kind": "plain_ok",
        "role": "l3_event_usage_policy_contract",
    },
    {
        "path": "btcts_next/src/btcts/replay/tests/test_replay_prediction_feedback.py",
        "kind": "plain_ok",
        "role": "replay_prediction_feedback_bridge",
    },
    {
        "path": "btcts_next/src/btcts/replay/tests/test_replay_runner_prediction_feedback_scenario_bridge.py",
        "kind": "plain_ok",
        "role": "replay_runner_prediction_feedback_scenario_bridge",
    },
    {
        "path": "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_replay_feedback_builder.py",
        "kind": "plain_ok",
        "role": "prediction_replay_feedback_builder",
    },
    {
        "path": "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_tactic_contract.py",
        "kind": "plain_ok",
        "role": "prediction_tactic_contract",
    },
    {
        "path": "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_tactic_review_builder.py",
        "kind": "plain_ok",
        "role": "prediction_tactic_review_builder",
    },
    {
        "path": "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_tactic_operation_builder.py",
        "kind": "plain_ok",
        "role": "prediction_tactic_operation_builder",
    },
    {
        "path": "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_tactic_selection.py",
        "kind": "plain_ok",
        "role": "prediction_tactic_selection",
    },
    {
        "path": "tools/test_phase4a_ai_ui_prediction_tactic_consumer_boundary_audit.py",
        "kind": "json_ok",
        "role": "ai_ui_prediction_tactic_consumer_boundary_audit",
    },
    {
        "path": "tools/test_phase4a_phase_d_l4_health_warroom_compact_reading_guard.py",
        "kind": "json_ok",
        "role": "phase_d_l4_health_warroom_compact_reading_guard",
    },
    {
        "path": "tools/test_phase4a_phase_e_warroom_operational_reading_guard.py",
        "kind": "json_ok",
        "role": "phase_e_warroom_operational_reading_guard",
    },
    {
        "path": "tools/test_phase4a_phase_e_health_operational_reading_guard.py",
        "kind": "json_ok",
        "role": "phase_e_health_operational_reading_guard",
    },
    {
        "path": "tools/test_phase4a_direction_position_execution_entry_criteria_guard.py",
        "kind": "json_ok",
        "role": "direction_position_execution_entry_criteria_guard",
    },
    {
        "path": "tools/test_phase4a_direction_read_only_boundary_guard.py",
        "kind": "json_ok",
        "role": "direction_read_only_boundary_guard",
    },
    {
        "path": "tools/test_phase4a_direction_replay_artifact_entry_criteria_guard.py",
        "kind": "json_ok",
        "role": "direction_replay_artifact_entry_criteria_guard",
    },
    {
        "path": "tools/test_phase4a_direction_replay_artifact_entry_close_guard.py",
        "kind": "json_ok",
        "role": "direction_replay_artifact_entry_close_guard",
    },
    {
        "path": "tools/test_phase4a_direction_replay_calibration_review_material_entry_guard.py",
        "kind": "json_ok",
        "role": "direction_replay_calibration_review_material_entry_guard",
    },
    {
        "path": "tools/test_phase4a_direction_replay_material_slice_audit.py",
        "kind": "json_ok",
        "role": "direction_replay_material_slice_audit",
    },
    {
        "path": "tools/test_phase4a_direction_unconnected_scope_cleanup_guard.py",
        "kind": "json_ok",
        "role": "direction_unconnected_scope_cleanup_guard",
    },
    {
        "path": "tools/test_phase4a_position_review_hint_entry_criteria_guard.py",
        "kind": "json_ok",
        "role": "position_review_hint_entry_criteria_guard",
    },
    {
        "path": "tools/test_phase4a_execution_review_hint_entry_criteria_guard.py",
        "kind": "json_ok",
        "role": "execution_review_hint_entry_criteria_guard",
    },
    {
        "path": "tools/test_phase4a_read_only_real_data_validation_probe_entry_criteria_guard.py",
        "kind": "json_ok",
        "role": "read_only_real_data_validation_probe_entry_criteria_guard",
    },
    {
        "path": "tools/test_phase4a_read_only_real_data_replay_report_validation_entry_criteria_guard.py",
        "kind": "json_ok",
        "role": "read_only_real_data_replay_report_validation_entry_criteria_guard",
    },
    {
        "path": "tools/test_phase4a_broader_real_data_validation_review_entry_criteria_guard.py",
        "kind": "json_ok",
        "role": "broader_real_data_validation_review_entry_criteria_guard",
    },
    {
        "path": "tools/test_phase4a_extended_real_data_validation_review_entry_criteria_guard.py",
        "kind": "json_ok",
        "role": "extended_real_data_validation_review_entry_criteria_guard",
    },
    {
        "path": "tools/test_phase4a_real_data_validation_evidence_connection_entry_criteria_guard.py",
        "kind": "json_ok",
        "role": "real_data_validation_evidence_connection_entry_criteria_guard",
    },
    {
        "path": "tools/test_phase4a_operator_ui_health_latency_snapshot_responsibility_entry_criteria_guard.py",
        "kind": "json_ok",
        "role": "operator_ui_health_latency_snapshot_responsibility_entry_criteria_guard",
    },
    {
        "path": "tools/test_phase4a_operator_ui_health_latency_snapshot_read_model_skeleton_guard.py",
        "kind": "json_ok",
        "role": "operator_ui_health_latency_snapshot_read_model_skeleton_guard",
    },
    {
        "path": "tools/test_phase4a_operator_ui_health_audit_read_model_bounded_inputs_guard.py",
        "kind": "json_ok",
        "role": "operator_ui_health_audit_read_model_bounded_inputs_guard",
    },
    {
        "path": "tools/test_phase4a_operator_ui_health_audit_tail_latency_budget_guard.py",
        "kind": "json_ok",
        "role": "operator_ui_health_audit_tail_latency_budget_guard",
    },
    {
        "path": "tools/test_phase4a_operator_ui_health_latency_budget_metadata_observability_guard.py",
        "kind": "json_ok",
        "role": "operator_ui_health_latency_budget_metadata_observability_guard",
    },
    {
        "path": "tools/test_phase4a_de_archive_transfer_health_dashboard_entry_criteria_guard.py",
        "kind": "json_ok",
        "role": "de_archive_transfer_health_dashboard_entry_criteria_guard",
    },
    {
        "path": "tools/test_phase4a_operational_readiness_hot_cold_10day_retention_health_safety_entry_close_guard.py",
        "kind": "json_ok",
        "role": "operational_readiness_hot_cold_10day_retention_health_safety_entry_close_guard",
    },
    {
        "path": "tools/test_phase4a_operational_readiness_hot_cold_10day_plan_summary_health_payload_close_guard.py",
        "kind": "json_ok",
        "role": "operational_readiness_hot_cold_10day_plan_summary_health_payload_close_guard",
    },
    {
        "path": "tools/test_phase4a_operational_readiness_hot_cold_retention_safety_health_display_close_guard.py",
        "kind": "json_ok",
        "role": "operational_readiness_hot_cold_retention_safety_health_display_close_guard",
        "env": {"BTCTS_HOT_COLD_SKIP_PRIMARY_COMPACT_GUARD": "1"},
    },
    {
        "path": "tools/test_phase4a_operational_readiness_hot_cold_retention_dry_run_plan_entry_close_guard.py",
        "kind": "json_ok",
        "role": "operational_readiness_hot_cold_retention_dry_run_plan_entry_close_guard",
    },
    {
        "path": "tools/test_phase4a_operational_readiness_hot_cold_copy_manifest_model_close_guard.py",
        "kind": "json_ok",
        "role": "operational_readiness_hot_cold_copy_manifest_model_close_guard",
        "env": {"BTCTS_HOT_COLD_SKIP_PRIMARY_COMPACT_GUARD": "1"},
    },
    {
        "path": "tools/test_phase4a_operational_readiness_hot_cold_copy_manifest_writer_dry_run_close_guard.py",
        "kind": "json_ok",
        "role": "operational_readiness_hot_cold_copy_manifest_writer_dry_run_close_guard",
        "env": {"BTCTS_HOT_COLD_SKIP_PRIMARY_COMPACT_GUARD": "1"},
    },
    {
        "path": "tools/test_phase4a_operational_readiness_hot_cold_duplicate_safe_dataset_view_entry_close_guard.py",
        "kind": "json_ok",
        "role": "operational_readiness_hot_cold_duplicate_safe_dataset_view_entry_close_guard",
    },
    {
        "path": "tools/test_phase4a_operational_readiness_hot_cold_duplicate_safe_dataset_view_model_close_guard.py",
        "kind": "json_ok",
        "role": "operational_readiness_hot_cold_duplicate_safe_dataset_view_model_close_guard",
    },
    {
        "path": "tools/test_phase4a_operational_readiness_hot_cold_copy_correctness_manifest_entry_close_guard.py",
        "kind": "json_ok",
        "role": "operational_readiness_hot_cold_copy_correctness_manifest_entry_close_guard",
    },
    {
        "path": "tools/test_phase4a_operational_readiness_hot_cold_low_load_copy_scheduler_entry_close_guard.py",
        "kind": "json_ok",
        "role": "operational_readiness_hot_cold_low_load_copy_scheduler_entry_close_guard",
    },
    {
        "path": "tools/test_phase4a_operational_readiness_hot_cold_periodic_10day_health_payload_refresh_entry_close_guard.py",
        "kind": "json_ok",
        "role": "operational_readiness_hot_cold_periodic_10day_health_payload_refresh_entry_close_guard",
    },
    {
        "path": "tools/test_phase4a_operational_readiness_hot_cold_safety_thread_close_guard.py",
        "kind": "json_ok",
        "role": "operational_readiness_hot_cold_safety_thread_close_guard",
        "env": {"BTCTS_HOT_COLD_SKIP_PRIMARY_COMPACT_GUARD": "1"},
    },
    {
        "path": "tools/test_phase4a_hot_cold_dashboard_display_source_catalog_close_guard.py",
        "kind": "json_ok",
        "role": "hot_cold_dashboard_display_source_catalog_close_guard",
    },
    {
        "path": "tools/test_phase4a_hot_cold_dashboard_display_source_status_close_guard.py",
        "kind": "json_ok",
        "role": "hot_cold_dashboard_display_source_status_close_guard",
    },
    {
        "path": "tools/test_phase4a_health_warroom_read_only_evidence_consumption_entry_criteria_guard.py",
        "kind": "json_ok",
        "role": "health_warroom_read_only_evidence_consumption_entry_criteria_guard",
    },
    {
        "path": "tools/test_phase4a_health_warroom_evidence_consumption_adapter_connection_guard.py",
        "kind": "json_ok",
        "role": "health_warroom_evidence_consumption_adapter_connection_guard",
    },
    {
        "path": "tools/test_phase4a_health_warroom_evidence_consumption_presentation_entry_criteria_guard.py",
        "kind": "json_ok",
        "role": "health_warroom_evidence_consumption_presentation_entry_criteria_guard",
    },
    {
        "path": "tools/test_phase4a_health_warroom_evidence_consumption_render_free_presentation_model_guard.py",
        "kind": "json_ok",
        "role": "health_warroom_evidence_consumption_render_free_presentation_model_guard",
    },
    {
        "path": "tools/test_phase4a_health_warroom_evidence_consumption_ui_rendering_entry_criteria_guard.py",
        "kind": "json_ok",
        "role": "health_warroom_evidence_consumption_ui_rendering_entry_criteria_guard",
    },
    {
        "path": "tools/test_phase4a_health_warroom_evidence_consumption_shared_ui_rendering_component_guard.py",
        "kind": "json_ok",
        "role": "health_warroom_evidence_consumption_shared_ui_rendering_component_guard",
    },
    {
        "path": "tools/test_phase4a_health_evidence_presentation_page_wiring_guard.py",
        "kind": "json_ok",
        "role": "health_evidence_presentation_page_wiring_guard",
    },
    {
        "path": "tools/test_phase4a_warroom_evidence_presentation_page_wiring_guard.py",
        "kind": "json_ok",
        "role": "warroom_evidence_presentation_page_wiring_guard",
    },
    {
        "path": "tools/test_phase4a_health_warroom_evidence_presentation_upstream_payload_production_entry_criteria_guard.py",
        "kind": "json_ok",
        "role": "health_warroom_evidence_presentation_upstream_payload_production_entry_criteria_guard",
    },
    {
        "path": "tools/test_phase4a_health_warroom_evidence_presentation_upstream_payload_producer_guard.py",
        "kind": "json_ok",
        "role": "health_warroom_evidence_presentation_upstream_payload_producer_guard",
    },
    {
        "path": "tools/test_phase4a_health_warroom_evidence_presentation_payload_lowering_channel_entry_criteria_guard.py",
        "kind": "json_ok",
        "role": "health_warroom_evidence_presentation_payload_lowering_channel_entry_criteria_guard",
    },
    {
        "path": "tools/test_phase4a_health_warroom_evidence_presentation_payload_lowering_channel_guard.py",
        "kind": "json_ok",
        "role": "health_warroom_evidence_presentation_payload_lowering_channel_guard",
    },
    {
        "path": "tools/test_phase4a_health_warroom_evidence_presentation_payload_lowering_channel_wiring_entry_criteria_guard.py",
        "kind": "json_ok",
        "role": "health_warroom_evidence_presentation_payload_lowering_channel_wiring_entry_criteria_guard",
    },
    {
        "path": "tools/test_phase4a_health_warroom_evidence_presentation_payload_lowering_channel_wiring_bridge_guard.py",
        "kind": "json_ok",
        "role": "health_warroom_evidence_presentation_payload_lowering_channel_wiring_bridge_guard",
    },
    {
        "path": "tools/test_phase4a_health_warroom_evidence_payload_lowering_page_local_wiring_entry_criteria_guard.py",
        "kind": "json_ok",
        "role": "health_warroom_evidence_payload_lowering_page_local_wiring_entry_criteria_guard",
    },
    {
        "path": "tools/test_phase4a_health_warroom_evidence_payload_lowering_page_local_wiring_guard.py",
        "kind": "json_ok",
        "role": "health_warroom_evidence_payload_lowering_page_local_wiring_guard",
    },
    {
        "path": "tools/test_phase4a_phase_f_collector_transform_migration_prep_entry_criteria_guard.py",
        "kind": "json_ok",
        "role": "phase_f_collector_transform_migration_prep_entry_criteria_guard",
    },
    {
        "path": "tools/test_phase4a_phase_f_collector_transform_usage_audit_guard.py",
        "kind": "json_ok",
        "role": "phase_f_collector_transform_usage_audit_guard",
    },
    {
        "path": "tools/test_phase4a_phase_f_collector_transform_facade_decision_entry_guard.py",
        "kind": "json_ok",
        "role": "phase_f_collector_transform_facade_decision_entry_guard",
    },
    {
        "path": "tools/test_phase4a_phase_f_collector_transform_facade_skeleton_guard.py",
        "kind": "json_ok",
        "role": "phase_f_collector_transform_facade_skeleton_guard",
    },
    {
        "path": "tools/test_phase4a_phase_f_collector_transform_runtime_import_migration_rest_guard.py",
        "kind": "json_ok",
        "role": "phase_f_collector_transform_runtime_import_migration_rest_guard",
    },
    {
        "path": "tools/test_phase4a_phase_f_collector_transform_runtime_import_migration_emit_ws_guard.py",
        "kind": "json_ok",
        "role": "phase_f_collector_transform_runtime_import_migration_emit_ws_guard",
    },
    {
        "path": "tools/test_phase4a_phase_f_collector_transform_runtime_import_migration_unified_ws_board_guard.py",
        "kind": "json_ok",
        "role": "phase_f_collector_transform_runtime_import_migration_unified_ws_board_guard",
    },
    {
        "path": "tools/test_phase4a_phase_f_collector_transform_runtime_import_migration_unified_ws_executions_guard.py",
        "kind": "json_ok",
        "role": "phase_f_collector_transform_runtime_import_migration_unified_ws_executions_guard",
    },
    {
        "path": "tools/test_phase4a_phase_f_collector_transform_facade_migration_close_audit_guard.py",
        "kind": "json_ok",
        "role": "phase_f_collector_transform_facade_migration_close_audit_guard",
    },
]


def _compile_cfile_for(rel_path: str) -> str:
    cache_root = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "replay_market_engine_parity_total"
    cache_root.mkdir(parents=True, exist_ok=True)
    safe_name = rel_path.replace("/", "__").replace("\\", "__") + ".pyc"
    return str(cache_root / safe_name)


def _compile_guard_scripts(failures: List[str]) -> Dict[str, Any]:
    passed: List[str] = []
    failed: List[Dict[str, str]] = []

    for spec in GUARD_SPECS:
        rel_path = str(spec["path"])
        path = REPO_ROOT / rel_path
        if not path.exists():
            failed.append({"path": rel_path, "error": "missing"})
            failures.append(f"guard script missing: {rel_path}")
            continue

        try:
            py_compile.compile(str(path), cfile=_compile_cfile_for(rel_path), doraise=True)
            passed.append(rel_path)
        except Exception as exc:
            failed.append({"path": rel_path, "error": str(exc)})
            failures.append(f"guard script py_compile failed: {rel_path}: {exc}")

    return {
        "passed_count": len(passed),
        "failed": failed,
    }


def _parse_json(stdout: str, rel_path: str, failures: List[str]) -> Dict[str, Any] | None:
    try:
        parsed = json.loads(stdout)
    except Exception as exc:
        failures.append(f"{rel_path} did not emit valid JSON: {exc}")
        return None

    if not isinstance(parsed, dict):
        failures.append(f"{rel_path} JSON output must be an object")
        return None

    return parsed


def _validate_result(
    *,
    rel_path: str,
    kind: str,
    proc: subprocess.CompletedProcess[str],
    failures: List[str],
) -> Dict[str, Any]:
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    stdout_stripped = stdout.strip()

    result: Dict[str, Any] = {
        "returncode": proc.returncode,
        "ok": False,
        "kind": kind,
        "phase": None,
        "json": None,
        "stdout_tail": stdout[-2000:],
        "stderr_tail": stderr[-2000:],
    }

    if kind == "plain_ok":
        ok = proc.returncode == 0 and stdout_stripped == "ok"
        if not ok:
            failures.append(f"{rel_path} must emit plain 'ok'")
        result["ok"] = bool(ok)
        return result

    if kind == "json_ok":
        parsed = _parse_json(stdout, rel_path, failures)
        result["json"] = parsed
        if isinstance(parsed, dict):
            result["phase"] = parsed.get("phase")
            failures_value = parsed.get("failures", [])
            ok = proc.returncode == 0 and parsed.get("ok") is True and failures_value == []
            if not ok:
                failures.append(f"{rel_path} must return ok:true and no failures")
            result["ok"] = bool(ok)
        return result

    if kind == "json_interpretation_audit":
        parsed = _parse_json(stdout, rel_path, failures)
        result["json"] = parsed
        if isinstance(parsed, dict):
            cases = parsed.get("runtime_interpretation_cases")
            buckets = parsed.get("review_policy_buckets")
            ok = (
                proc.returncode == 0
                and parsed.get("profile_name") == "bitflyer"
                and isinstance(cases, list)
                and len(cases) >= 10
                and isinstance(buckets, list)
                and len(buckets) > 0
            )
            if not ok:
                failures.append(
                    f"{rel_path} must emit bitflyer interpretation audit with cases and review policy buckets"
                )
            result["ok"] = bool(ok)
        return result

    failures.append(f"unknown guard kind for {rel_path}: {kind}")
    return result


def _run_guard(spec: Dict[str, Any], failures: List[str]) -> Dict[str, Any]:
    rel_path = str(spec["path"])
    kind = str(spec["kind"])
    path = REPO_ROOT / rel_path

    if not path.exists():
        failures.append(f"guard script missing: {rel_path}")
        return {
            "returncode": None,
            "ok": False,
            "kind": kind,
            "phase": None,
            "json": None,
            "stdout_tail": "",
            "stderr_tail": "",
        }

    env = None
    spec_env = spec.get("env")
    if isinstance(spec_env, dict) and spec_env:
        env = os.environ.copy()
        env.update({str(key): str(value) for key, value in spec_env.items()})

    proc = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=900,
        env=env,
    )

    return _validate_result(
        rel_path=rel_path,
        kind=kind,
        proc=proc,
        failures=failures,
    )


def main() -> int:
    failures: List[str] = []

    compile_result = _compile_guard_scripts(failures)
    guard_results = {
        str(spec["path"]): {
            "role": spec["role"],
            **_run_guard(spec, failures),
        }
        for spec in GUARD_SPECS
    }

    summary = {
        "phase": "phase4a_replay_market_engine_parity_total_guard",
        "checks": {
            "compile": compile_result,
            "guards": guard_results,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())