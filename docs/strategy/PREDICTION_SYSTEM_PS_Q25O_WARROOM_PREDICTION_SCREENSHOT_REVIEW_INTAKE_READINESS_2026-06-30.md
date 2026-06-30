# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q25O_WARROOM_PREDICTION_SCREENSHOT_REVIEW_INTAKE_READINESS_2026-06-30.md
# desc: PS-Q25O WarRoom prediction screenshot review intake readiness. Read-only checklist; no production code changes.
# PS-Q25O WarRoom prediction screenshot review intake readiness

Updated: 2026-06-30 JST
Base: PS-Q25N WarRoom prediction display/cadence-gate closeout readiness
Mode: read-only screenshot-review intake / no production code change / no UI mutation / no cadence, scheduler, artifact, AutoTrade, broker, ledger, mode, or parameter change

```text
ps_q25o_warroom_prediction_screenshot_review_intake_readiness=true
base_reentry=PS_Q25N_WARROOM_PREDICTION_DISPLAY_CADENCE_GATE_CLOSEOUT_READINESS_DONE
screenshot_review_intake_packet_added=true
production_code_changed=false
read_only_review_intake=true
actual_screenshot_supplied=false
actual_screenshot_review_performed=false
actual_screenshot_review_required_before_visual_final=true
q25j_density_tuning_review_target=true
cadence_lane_stopped_at_human_gate=true
safe_default_option_id=keep_current_300s_context_only_until_gate
producer_cadence_changed=false
scheduler_action_changed=false
scheduler_enabled=false
producer_enabled=false
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
latest_manifest_written=false
run_sidecars_written=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
ledger_append=false
mode_apply=false
parameter_apply=false
```

## Screenshot intake purpose

Q25O prepares the review criteria for the actual WarRoom screenshot. It does not claim that visual review has been performed. The operator must still provide or inspect an actual WarRoom screenshot before marking the display visually final.

## Required screenshot areas

```text
warroom_page_top_visible
live_market_nowcast_panel_visible
prediction_compact_operator_header_visible
prediction_detail_checks_folded_by_default
prediction_metrics_visible
prediction_rows_visible
reading_guide_folded_by_default
footer_or_debug_markers_not_operator_blocking
```

## Acceptance checklist

```text
compact_header_first=true
detail_checks_not_repeated_as_full_blocks=true
stale_or_expired_prediction_state_is_understandable=true
operator_action_guidance_visible_or_accessible=true
horizon_expiry_visible_or_accessible=true
metrics_and_prediction_rows_remain_visible=true
no_horizontal_layout_break=true
no_nested_expander_runtime_error_observed=true
no_autotrade_or_broker_control_added=true
```

## If screenshot fails

If the screenshot shows crowding, confusing ordering, hidden operator action, nested expander error, or missing prediction rows, the next slice should be a display-only visual polish fix. It must not change producer cadence, scheduler actions, artifacts, AutoTrade, broker, ledger, mode, or parameters.
