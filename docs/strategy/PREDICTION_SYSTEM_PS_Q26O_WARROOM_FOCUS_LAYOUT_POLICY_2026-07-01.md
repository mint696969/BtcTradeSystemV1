# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q26O_WARROOM_FOCUS_LAYOUT_POLICY_2026-07-01.md
# desc: PS-Q26O externalizes WarRoom top focus layout policy and folds the quick-status detail section by default. Layout-only display-only UI change.
# PS-Q26O WarRoom focus layout policy

Updated: 2026-07-01 JST
Base: PS-Q26N WarRoom operator focus navigation externalized panel
Mode: WarRoom UI density folding / externalized layout policy / display-only / no runtime writes / no scheduler or producer enablement / no trading guidance

```text
ps_q26o_warroom_focus_layout_policy=true
base_reentry=PS_Q26N_WARROOM_OPERATOR_FOCUS_NAV_EXTERNALIZED_PANEL_DONE
selected_lane=WARROOM_UI_VISUAL_REVIEW_OR_DENSITY_FOLDING
production_ui_code_changed=true
changed_file=btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py
externalized_layout_policy_file=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_focus_layout_policy.py
warroom_page_change_boundary=import_and_policy_lookup_only
q26n_focus_nav_test_policy_lookup_compatible=true
quick_status_detail_folded_default=true
operator_focus_nav_expanded_default=true
live_nowcast_expanded_default=true
latest_prediction_read_model_expanded_default=true
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

Q26N added a top navigation block, but the old quick-status detail section still opened above the main nowcast/prediction sections. PS-Q26O keeps the section available, but folds it by default so the operator sees:

```text
1. WarRoom入口 navigation
2. 現在状態 nowcast
3. リアルタイム予測表示
```

The policy is externalized to `warroom_focus_layout_policy.py` so `warroom_page.py` remains wiring/composition only.

Q26O also updates the Q26N focus-nav ordering test so it accepts the policy-lookup render path introduced here.

## Safety boundary

This is a layout-only display change. It does not read or write artifacts, trigger refreshes, enable producer/scheduler, change predictions, append ledger entries, call AutoTrade/broker APIs, or apply mode/parameter changes.
