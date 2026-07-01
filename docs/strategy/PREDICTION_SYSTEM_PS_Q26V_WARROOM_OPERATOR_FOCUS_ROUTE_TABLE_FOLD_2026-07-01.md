# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q26V_WARROOM_OPERATOR_FOCUS_ROUTE_TABLE_FOLD_2026-07-01.md
# desc: PS-Q26V folds the WarRoom operator focus route table while leaving the one-line route visible.
# PS-Q26V WarRoom operator focus route table fold

Updated: 2026-07-01 JST
Base: PS-Q26U WarRoom operator focus detail fold
Mode: WarRoom UI visual tuning / first-screen table density reduction / display-only / no runtime writes / no scheduler or producer enablement / no trading guidance

```text
ps_q26v_warroom_operator_focus_route_table_fold=true
base_reentry=PS_Q26U_WARROOM_OPERATOR_FOCUS_DETAIL_FOLD_DONE
selected_lane=WARROOM_UI_VISUAL_TUNING
production_ui_code_changed=true
changed_file=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_operator_focus_nav_panel.py
warroom_page_changed=false
warroom_page_slimming_main_goal=false
command_cards_visible=true
visual_route_text_visible=true
visual_route_strip_visible=true
route_table_available=true
route_table_folded_default=true
detail_table_folded_default=true
reduces_first_screen_table_density=true
visual_only_change=true
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

Q26V keeps the one-line reading route visible and folds the 4-step route table by default. The first glance becomes cards + one-line route, with tables available only when the operator opens details.

## Safety boundary

This is visual-only UI presentation. It does not read or write runtime artifacts, trigger refreshes, enable producer/scheduler, change predictions, append ledger entries, call AutoTrade/broker APIs, or apply mode/parameter changes.
