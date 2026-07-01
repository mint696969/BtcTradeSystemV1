# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q26P_WARROOM_SECONDARY_DETAIL_FOLDING_2026-07-01.md
# desc: PS-Q26P folds WarRoom secondary detail sections by default using the externalized focus layout policy. Layout-only display-only UI change.
# PS-Q26P WarRoom secondary detail folding

Updated: 2026-07-01 JST
Base: PS-Q26O WarRoom focus layout policy
Mode: WarRoom UI density folding / externalized layout policy / display-only / no runtime writes / no scheduler or producer enablement / no trading guidance

```text
ps_q26p_warroom_secondary_detail_folding=true
base_reentry=PS_Q26O_WARROOM_FOCUS_LAYOUT_POLICY_DONE
selected_lane=WARROOM_UI_SECONDARY_DETAIL_FOLDING
production_ui_code_changed=true
changed_file=btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py
externalized_layout_policy_file=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_focus_layout_policy.py
warroom_page_change_boundary=import_and_policy_lookup_only
operator_focus_nav_expanded_default=true
live_nowcast_expanded_default=true
latest_prediction_read_model_expanded_default=true
header_alert_operator_expanded_default=true
quick_status_detail_folded_default=true
market_evidence_detail_folded_default=true
operator_support_detail_folded_default=true
secondary_detail_sections_folded_default=true
keeps_existing_panels_available=true
layout_only_change=true
read_only=true
display_only=true
non_executing=true
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
scheduler_enabled=false
producer_enabled=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
ledger_append=false
mode_apply=false
parameter_apply=false
would_send_to_broker=false
```

## Purpose

Q26N added a top navigation block and Q26O folded the quick-status detail section. PS-Q26P continues the same UI density cleanup by folding priority 4/5 sections by default:

```text
4. 市場証拠 / graph / active event
5. operator support / timeline / evidence
```

The sections are still available. This slice only changes their initial expanded/collapsed state and routes labels/defaults through `warroom_focus_layout_policy.py`.

## Safety boundary

This is a layout-only display change. It does not read or write artifacts, trigger refreshes, enable producer/scheduler, change predictions, append ledger entries, call AutoTrade/broker APIs, or apply mode/parameter changes.
