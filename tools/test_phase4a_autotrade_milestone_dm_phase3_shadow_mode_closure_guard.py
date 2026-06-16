# path: ./tools/test_phase4a_autotrade_milestone_dm_phase3_shadow_mode_closure_guard.py
# desc: Closure guard for AutoTrade Phase 3 Shadow Mode scope before moving to Paper/Execution phases.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PHASE3_FILES = (
    "btcts_next/src/btcts/autotrade/README.md",
    "btcts_next/src/btcts/autotrade/modes.py",
    "btcts_next/src/btcts/autotrade/boundary.py",
    "btcts_next/src/btcts/autotrade/config/defaults.py",
    "btcts_next/src/btcts/autotrade/config/models.py",
    "btcts_next/src/btcts/autotrade/config/registry.py",
    "btcts_next/src/btcts/autotrade/read_model/models.py",
    "btcts_next/src/btcts/autotrade/read_model/live_input_adapter.py",
    "btcts_next/src/btcts/autotrade/read_model/temporal_flow_adapter.py",
    "btcts_next/src/btcts/autotrade/read_model/forecast.py",
    "btcts_next/src/btcts/autotrade/strategy/selector.py",
    "btcts_next/src/btcts/autotrade/strategy/models.py",
    "btcts_next/src/btcts/autotrade/risk/gates.py",
    "btcts_next/src/btcts/autotrade/risk/models.py",
    "btcts_next/src/btcts/autotrade/live_shadow.py",
    "btcts_next/src/btcts/autotrade/shadow_cycle.py",
    "btcts_next/src/btcts/autotrade/observer_cycle.py",
    "btcts_next/src/btcts/autotrade/mode_runtime_gate.py",
    "btcts_next/src/btcts/autotrade/health.py",
    "btcts_next/src/btcts/autotrade/readiness.py",
    "btcts_next/src/btcts/autotrade/ledger/decision_log.py",
    "btcts_next/src/btcts/autotrade/ledger/decision_status.py",
    "btcts_next/src/btcts/autotrade/ledger/forecast_resolution.py",
    "btcts_next/src/btcts/autotrade/ledger/forecast_outcome_status.py",
    "btcts_next/src/btcts/autotrade/ledger/observer_run_status.py",
    "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py",
)

REQUIRED_GUARD_FILES = (
    "tools/test_phase4a_autotrade_milestone_a_boundary_guard.py",
    "tools/test_phase4a_autotrade_milestone_b_parameter_sets_guard.py",
    "tools/test_phase4a_autotrade_milestone_c_read_model_forecast_guard.py",
    "tools/test_phase4a_autotrade_milestone_d_strategy_risk_ledger_guard.py",
    "tools/test_phase4a_autotrade_milestone_e_performance_diagnostics_guard.py",
    "tools/test_phase4a_autotrade_milestone_f_forecast_calibration_guard.py",
    "tools/test_phase4a_autotrade_milestone_g_operator_ui_tab_guard.py",
    "tools/test_phase4a_autotrade_milestone_m_runtime_paths_guard.py",
    "tools/test_phase4a_autotrade_milestone_n_live_input_adapter_guard.py",
    "tools/test_phase4a_autotrade_milestone_o_temporal_flow_adapter_guard.py",
    "tools/test_phase4a_autotrade_milestone_p_live_snapshot_forecast_usability_guard.py",
    "tools/test_phase4a_autotrade_milestone_q_market_state_shadow_decision_guard.py",
    "tools/test_phase4a_autotrade_milestone_r_shadow_cycle_once_guard.py",
    "tools/test_phase4a_autotrade_milestone_s_bounded_shadow_cycle_runner_guard.py",
    "tools/test_phase4a_autotrade_milestone_t_shadow_decision_ledger_status_guard.py",
    "tools/test_phase4a_autotrade_milestone_u_autotrade_tab_shadow_ledger_status_guard.py",
    "tools/test_phase4a_autotrade_milestone_v_forecast_outcome_resolver_guard.py",
    "tools/test_phase4a_autotrade_milestone_w_target_time_actual_matcher_guard.py",
    "tools/test_phase4a_autotrade_milestone_x_forecast_outcome_ledger_status_guard.py",
    "tools/test_phase4a_autotrade_milestone_y_autotrade_tab_forecast_calibration_status_guard.py",
    "tools/test_phase4a_autotrade_milestone_z_forecast_outcome_resolver_cli_guard.py",
    "tools/test_phase4a_autotrade_milestone_aa_bounded_observer_cycle_guard.py",
    "tools/test_phase4a_autotrade_milestone_ab_observer_duplicate_snapshot_suppression_guard.py",
    "tools/test_phase4a_autotrade_milestone_ac_observer_run_status_ledger_guard.py",
    "tools/test_phase4a_autotrade_milestone_ad_autotrade_tab_observer_run_status_guard.py",
    "tools/test_phase4a_autotrade_milestone_ae_runtime_health_snapshot_guard.py",
    "tools/test_phase4a_autotrade_milestone_af_autotrade_tab_runtime_health_status_guard.py",
    "tools/test_phase4a_autotrade_milestone_ag_runtime_health_cli_guard.py",
    "tools/test_phase4a_autotrade_milestone_ah_live_readiness_preflight_guard.py",
    "tools/test_phase4a_autotrade_milestone_ai_autotrade_tab_live_readiness_preflight_guard.py",
    "tools/test_phase4a_autotrade_milestone_aj_mode_change_command_request_ledger_guard.py",
    "tools/test_phase4a_autotrade_milestone_ak_autotrade_tab_mode_change_request_button_guard.py",
    "tools/test_phase4a_autotrade_milestone_al_command_request_ledger_status_guard.py",
    "tools/test_phase4a_autotrade_milestone_am_autotrade_tab_command_request_status_guard.py",
    "tools/test_phase4a_autotrade_milestone_an_autotrade_tab_import_render_smoke_guard.py",
    "tools/test_phase4a_autotrade_milestone_ao_mode_state_ledger_contract_guard.py",
    "tools/test_phase4a_autotrade_milestone_ap_mode_change_command_applier_once_guard.py",
    "tools/test_phase4a_autotrade_milestone_aq_autotrade_tab_mode_state_status_guard.py",
    "tools/test_phase4a_autotrade_milestone_ar_readiness_current_mode_from_mode_state_guard.py",
    "tools/test_phase4a_autotrade_milestone_as_mode_change_applier_preview_status_guard.py",
    "tools/test_phase4a_autotrade_milestone_at_autotrade_tab_mode_change_apply_preview_guard.py",
    "tools/test_phase4a_autotrade_milestone_au_autotrade_tab_full_render_smoke_guard.py",
    "tools/test_phase4a_autotrade_milestone_av_mode_change_applier_readiness_recheck_guard.py",
    "tools/test_phase4a_autotrade_milestone_aw_mode_change_rechecked_preview_guard.py",
    "tools/test_phase4a_autotrade_milestone_ax_autotrade_tab_rechecked_apply_preview_guard.py",
    "tools/test_phase4a_autotrade_milestone_ay_default_apply_cli_rechecked_guard.py",
    "tools/test_phase4a_autotrade_milestone_az_mode_state_latest_rejection_visibility_guard.py",
    "tools/test_phase4a_autotrade_milestone_ba_autotrade_tab_full_render_smoke_guard_refresh.py",
    "tools/test_phase4a_autotrade_milestone_bb_plain_mode_change_applier_quarantine_guard.py",
    "tools/test_phase4a_autotrade_milestone_bc_mode_state_runtime_gating_preview_guard.py",
    "tools/test_phase4a_autotrade_milestone_bd_shadow_observer_runtime_gate_guard.py",
    "tools/test_phase4a_autotrade_milestone_be_autotrade_tab_mode_runtime_gate_status_guard.py",
    "tools/test_phase4a_autotrade_milestone_bf_autotrade_tab_full_render_smoke_guard_runtime_gate_refresh.py",
    "tools/test_phase4a_autotrade_milestone_bg_shadow_observer_runtime_gate_shadow_allow_guard.py",
    "tools/test_phase4a_autotrade_milestone_bh_bounded_observer_runtime_gate_shadow_allow_guard.py",
    "tools/test_phase4a_autotrade_milestone_bi_bounded_shadow_runtime_gate_guard.py",
    "tools/test_phase4a_autotrade_milestone_bj_observer_run_latest_blocked_visibility_guard.py",
    "tools/test_phase4a_autotrade_milestone_bk_runtime_health_observer_latest_blocked_visibility_guard.py",
    "tools/test_phase4a_autotrade_milestone_bl_full_render_smoke_guard_observer_blocked_refresh.py",
    "tools/test_phase4a_autotrade_milestone_bm_live_readiness_blocks_latest_observer_run_blocked_guard.py",
    "tools/test_phase4a_autotrade_milestone_bn_mode_change_applier_rejects_latest_observer_blocked_guard.py",
    "tools/test_phase4a_autotrade_milestone_bo_autotrade_tab_readiness_observer_blocked_visibility_guard.py",
    "tools/test_phase4a_autotrade_milestone_bp_full_render_smoke_guard_readiness_observer_refresh.py",
    "tools/test_phase4a_autotrade_milestone_bq_mode_change_request_readiness_observer_visibility_guard.py",
    "tools/test_phase4a_autotrade_milestone_br_command_note_readiness_observer_details_guard.py",
    "tools/test_phase4a_autotrade_milestone_bs_command_status_readiness_observer_note_visibility_guard.py",
    "tools/test_phase4a_autotrade_milestone_bt_full_render_smoke_guard_command_note_visibility_refresh.py",
    "tools/test_phase4a_autotrade_milestone_bu_command_status_latest_mode_change_readiness_note_guard.py",
    "tools/test_phase4a_autotrade_milestone_bv_full_render_smoke_guard_latest_mode_change_note_refresh.py",
    "tools/test_phase4a_autotrade_milestone_bw_command_status_readiness_note_fail_soft_guard.py",
    "tools/test_phase4a_autotrade_milestone_bx_command_status_mode_change_note_filters_command_type_guard.py",
    "tools/test_phase4a_autotrade_milestone_by_full_render_smoke_guard_mode_change_note_filter_refresh.py",
    "tools/test_phase4a_autotrade_milestone_bz_command_status_mode_change_readiness_snapshot_context_guard.py",
    "tools/test_phase4a_autotrade_milestone_ca_full_render_smoke_guard_readiness_context_refresh.py",
    "tools/test_phase4a_autotrade_milestone_cb_command_status_mode_change_readiness_command_metadata_guard.py",
    "tools/test_phase4a_autotrade_milestone_cc_full_render_smoke_guard_command_metadata_refresh.py",
    "tools/test_phase4a_autotrade_milestone_cd_mode_change_preview_candidate_readiness_note_guard.py",
    "tools/test_phase4a_autotrade_milestone_ce_full_render_smoke_guard_candidate_readiness_note_refresh.py",
    "tools/test_phase4a_autotrade_milestone_cf_mode_change_preview_candidate_note_fail_soft_guard.py",
    "tools/test_phase4a_autotrade_milestone_cg_mode_change_preview_candidate_command_metadata_guard.py",
    "tools/test_phase4a_autotrade_milestone_ch_full_render_smoke_guard_candidate_command_metadata_refresh.py",
    "tools/test_phase4a_autotrade_milestone_ci_rechecked_apply_result_candidate_context_guard.py",
    "tools/test_phase4a_autotrade_milestone_cj_rechecked_apply_cli_candidate_context_guard.py",
    "tools/test_phase4a_autotrade_milestone_ck_rechecked_preview_cli_candidate_context_guard.py",
    "tools/test_phase4a_autotrade_milestone_cl_rechecked_apply_candidate_note_fail_soft_guard.py",
    "tools/test_phase4a_autotrade_milestone_cm_rechecked_apply_cli_candidate_note_fail_soft_guard.py",
    "tools/test_phase4a_autotrade_milestone_cn_rechecked_preview_cli_candidate_note_fail_soft_guard.py",
    "tools/test_phase4a_autotrade_milestone_co_mode_state_rejection_status_after_rechecked_apply_guard.py",
    "tools/test_phase4a_autotrade_milestone_cp_full_render_after_rechecked_apply_rejection_guard.py",
    "tools/test_phase4a_autotrade_milestone_cq_rechecked_apply_sequential_candidate_draining_guard.py",
    "tools/test_phase4a_autotrade_milestone_cr_rechecked_apply_cli_sequential_candidate_draining_guard.py",
    "tools/test_phase4a_autotrade_milestone_cs_rechecked_preview_sequential_candidate_visibility_guard.py",
    "tools/test_phase4a_autotrade_milestone_ct_rechecked_preview_cli_sequential_candidate_visibility_guard.py",
    "tools/test_phase4a_autotrade_milestone_cu_full_render_sequential_candidate_visibility_guard.py",
    "tools/test_phase4a_autotrade_milestone_cv_full_render_drained_candidate_queue_visibility_guard.py",
    "tools/test_phase4a_autotrade_milestone_cw_mixed_command_ledger_filtering_guard.py",
    "tools/test_phase4a_autotrade_milestone_cx_mixed_command_ledger_cli_filtering_guard.py",
    "tools/test_phase4a_autotrade_milestone_cy_full_render_mixed_command_ledger_filtering_visibility_guard.py",
    "tools/test_phase4a_autotrade_milestone_cz_top_recent_command_rows_failsoft_guard.py",
    "tools/test_phase4a_autotrade_milestone_da_strict_command_ledger_reader_isolation_guard.py",
    "tools/test_phase4a_autotrade_milestone_db_malformed_mode_state_candidate_visibility_guard.py",
    "tools/test_phase4a_autotrade_milestone_dc_malformed_mode_state_cli_candidate_visibility_guard.py",
    "tools/test_phase4a_autotrade_milestone_dd_full_render_malformed_mode_state_candidate_visibility_guard.py",
    "tools/test_phase4a_autotrade_milestone_de_mode_runtime_gate_malformed_mode_state_failsoft_guard.py",
    "tools/test_phase4a_autotrade_milestone_df_live_readiness_malformed_mode_state_failsoft_guard.py",
    "tools/test_phase4a_autotrade_milestone_dg_runtime_health_malformed_decision_ledgers_failsoft_guard.py",
    "tools/test_phase4a_autotrade_milestone_dh_decision_ledger_status_panels_malformed_rows_failsoft_guard.py",
    "tools/test_phase4a_autotrade_milestone_di_full_render_all_malformed_ledgers_failsoft_guard.py",
    "tools/test_phase4a_autotrade_milestone_dj_mode_change_command_request_malformed_decision_ledgers_guard.py",
    "tools/test_phase4a_autotrade_milestone_dk_rejected_mode_change_not_apply_candidate_guard.py",
    "tools/test_phase4a_autotrade_milestone_dl_accepted_mode_change_recheck_malformed_decision_ledgers_guard.py",
)

PHASE3_FORBIDDEN_TOKENS = (
    "pybitflyer",
    "ccxt",
    "private_api",
    "send_order(",
    "place_order(",
    "broker_order(",
    "requests.post",
    "httpx.post",
)

PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)


def read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


def function_source(rel: str, function_name: str) -> str:
    text = read(rel)
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(text, node) or ""
    return ""


def missing(paths: tuple[str, ...]) -> list[str]:
    return [path for path in paths if not (REPO_ROOT / path).exists()]


def main() -> int:
    failures: list[str] = []
    missing_phase3_files = missing(REQUIRED_PHASE3_FILES)
    missing_guard_files = missing(REQUIRED_GUARD_FILES)
    if missing_phase3_files:
        failures.append(f"missing_phase3_files: {missing_phase3_files}")
    if missing_guard_files:
        failures.append(f"missing_guard_files: {missing_guard_files}")

    readme = read("btcts_next/src/btcts/autotrade/README.md")
    decision_log = read("btcts_next/src/btcts/autotrade/ledger/decision_log.py")
    shadow_cycle = read("btcts_next/src/btcts/autotrade/shadow_cycle.py")
    observer_cycle = read("btcts_next/src/btcts/autotrade/observer_cycle.py")
    risk_gates = read("btcts_next/src/btcts/autotrade/risk/gates.py")
    strategy_selector = read("btcts_next/src/btcts/autotrade/strategy/selector.py")
    forecast = read("btcts_next/src/btcts/autotrade/read_model/forecast.py")
    model_contracts = read("btcts_next/src/btcts/autotrade/read_model/models.py")
    mode_runtime_gate = read("btcts_next/src/btcts/autotrade/mode_runtime_gate.py")
    autotrade_page = read("btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py")

    shadow_once_source = function_source("btcts_next/src/btcts/autotrade/shadow_cycle.py", "run_shadow_cycle_once")
    shadow_bounded_source = function_source("btcts_next/src/btcts/autotrade/shadow_cycle.py", "run_shadow_cycle_bounded")
    observer_once_source = function_source("btcts_next/src/btcts/autotrade/observer_cycle.py", "run_observer_cycle_once")
    observer_bounded_source = function_source("btcts_next/src/btcts/autotrade/observer_cycle.py", "run_observer_cycle_bounded")
    risk_source = function_source("btcts_next/src/btcts/autotrade/risk/gates.py", "evaluate_risk_gate")
    candidate_source = function_source("btcts_next/src/btcts/autotrade/strategy/selector.py", "build_action_candidate")
    forecast_source = function_source("btcts_next/src/btcts/autotrade/read_model/forecast.py", "build_rule_based_forecast_5m")
    render_source = function_source("btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py", "render")

    autotrade_phase3_sources = "\n".join(
        [
            decision_log,
            shadow_cycle,
            observer_cycle,
            risk_gates,
            strategy_selector,
            forecast,
            model_contracts,
            mode_runtime_gate,
            autotrade_page,
        ]
    )

    checks = {
        "phase3_required_files_exist": not missing_phase3_files,
        "phase3_guard_files_exist_through_dl": not missing_guard_files,
        "readme_locks_boundaries_and_non_goals": all(token in readme for token in ("L1-L4 provide read-only market truth", "GPT/AI is not the live order decision maker", "Operator UI is not the execution source of truth", "If state is unknown, do not add exposure")),
        "decision_log_has_phase3_required_audit_fields_and_no_order": all(token in decision_log for token in ("decision_id", "snapshot_id", "forecast_id", "forecast_5m", "candidate", "risk_gate", "final_action", "reason_codes", "blocked_by", "would_order", "None")),
        "read_model_and_forecast_contracts_include_5m_temporal_and_stale_guard": all(token in model_contracts for token in ("AutoTradeSnapshot", "TemporalFlowFeatures", "Forecast5m", "horizon_sec", "target_ts", "source_snapshot_id")) and all(token in forecast_source for token in ("target_ts_for", "_downgrade_confidence_for_stale")) and all(token in forecast for token in ("temporal_flow_unusable", "trade_unusable", "liquidity_unusable")),
        "strategy_is_deterministic_candidate_builder_not_execution": all(token in candidate_source for token in ("compute_entry_quality", "entry_threshold_for", "CandidateAction", "reason_codes", "blocked_hint")) and not any(token in candidate_source for token in PHASE3_FORBIDDEN_TOKENS),
        "risk_gate_fail_closed_shadow_non_executable": all(token in risk_source for token in ("RISK_ENTRY_BLOCKED_STALE", "executable=False", "RISK_NO_REAL_ORDERS_IN_SHADOW", "mode_not_entry_capable")) and not any(token in risk_source for token in PHASE3_FORBIDDEN_TOKENS),
        "shadow_cycle_bounded_no_broker_and_mode_gated": all(token in shadow_once_source for token in ("build_mode_runtime_gate", "allow_shadow_decision_append", "mode_runtime_gate_blocked_shadow_decision_append", "would_send_to_broker=False")) and all(token in shadow_bounded_source for token in ("skip_duplicate_snapshot", "bounded=True", "would_send_to_broker=False")) and "MAX_BOUNDED_SHADOW_CYCLES" in shadow_cycle and not any(token in shadow_cycle for token in PHASE3_FORBIDDEN_TOKENS),
        "observer_cycle_bounded_resolves_forecast_only_and_records_status": all(token in observer_once_source for token in ("run_shadow_cycle_once", "resolve_due_shadow_forecast_outcomes", "allow_forecast_outcome_resolution", "would_send_to_broker=False")) and all(token in observer_bounded_source for token in ("ObserverRunRecord", "append_observer_run_record", "skip_duplicate_snapshot", "bounded=True", "would_send_to_broker=False")) and not any(token in observer_cycle for token in PHASE3_FORBIDDEN_TOKENS),
        "mode_runtime_gate_covers_shadow_paper_armed_live_without_auto_escalation": all(token in mode_runtime_gate for token in ("allow_observer_cycle", "allow_shadow_decision_append", "allow_forecast_outcome_resolution", "allow_paper_order", "allow_armed_dry_run", "allow_live_order_capability", "read_only=True", "would_send_to_broker=False")),
        "operator_ui_autotrade_tab_is_status_and_command_layer_not_broker": all(token in autotrade_page for token in ("_render_top_critical_state", "_render_mode_state_status", "_render_mode_runtime_gate_status", "_render_mode_change_apply_preview_status", "_render_runtime_health_status", "_render_live_readiness_preflight", "_render_observer_run_status", "_render_shadow_decision_status", "_render_forecast_calibration_status")) and all(call in render_source for call in ("_render_top_critical_state()", "_render_mode_state_status()", "_render_mode_runtime_gate_status()", "_render_mode_change_apply_preview_status()", "_render_command_request_status()", "_render_runtime_health_status()", "_render_live_readiness_preflight()", "_render_operation_visibility()", "_render_observer_run_status()", "_render_shadow_decision_status()", "_render_forecast_calibration_status()", "_render_parameter_settings()")) and not any(token in autotrade_page for token in PHASE3_FORBIDDEN_TOKENS),
        "phase3_sources_do_not_contain_direct_broker_order_calls": not any(token in autotrade_phase3_sources for token in PHASE3_FORBIDDEN_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone DM: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_dm_phase3_shadow_mode_closure_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "phase3_required_files_exist": checks["phase3_required_files_exist"],
            "phase3_guard_files_exist_through_dl": checks["phase3_guard_files_exist_through_dl"],
            "readme_locks_boundaries_and_non_goals": checks["readme_locks_boundaries_and_non_goals"],
            "decision_log_has_phase3_required_audit_fields_and_no_order": checks["decision_log_has_phase3_required_audit_fields_and_no_order"],
            "read_model_and_forecast_contracts_include_5m_temporal_and_stale_guard": checks["read_model_and_forecast_contracts_include_5m_temporal_and_stale_guard"],
            "strategy_is_deterministic_candidate_builder_not_execution": checks["strategy_is_deterministic_candidate_builder_not_execution"],
            "risk_gate_fail_closed_shadow_non_executable": checks["risk_gate_fail_closed_shadow_non_executable"],
            "shadow_cycle_bounded_no_broker_and_mode_gated": checks["shadow_cycle_bounded_no_broker_and_mode_gated"],
            "observer_cycle_bounded_resolves_forecast_only_and_records_status": checks["observer_cycle_bounded_resolves_forecast_only_and_records_status"],
            "mode_runtime_gate_covers_shadow_paper_armed_live_without_auto_escalation": checks["mode_runtime_gate_covers_shadow_paper_armed_live_without_auto_escalation"],
            "operator_ui_autotrade_tab_is_status_and_command_layer_not_broker": checks["operator_ui_autotrade_tab_is_status_and_command_layer_not_broker"],
            "phase3_sources_do_not_contain_direct_broker_order_calls": checks["phase3_sources_do_not_contain_direct_broker_order_calls"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "missing_phase3_files": missing_phase3_files,
        "missing_guard_files": missing_guard_files,
        "required_phase3_file_count": len(REQUIRED_PHASE3_FILES),
        "required_guard_file_count": len(REQUIRED_GUARD_FILES),
        "protected_dirty_hits": protected_dirty_hits,
        "checks": checks,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
