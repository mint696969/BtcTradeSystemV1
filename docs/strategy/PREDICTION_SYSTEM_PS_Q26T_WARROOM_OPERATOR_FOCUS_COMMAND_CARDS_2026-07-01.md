# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q26T_WARROOM_OPERATOR_FOCUS_COMMAND_CARDS_2026-07-01.md
# desc: PS-Q26T adds first-glance command cards to WarRoom operator focus entry.
# PS-Q26T WarRoom operator focus command cards

Updated: 2026-07-01 JST
Base: PS-Q26S WarRoom operator focus visual tune
Mode: WarRoom UI visual tuning / first-glance command cards / display-only / no runtime writes / no scheduler or producer enablement / no trading guidance

```text
ps_q26t_warroom_operator_focus_command_cards=true
base_reentry=PS_Q26S_WARROOM_OPERATOR_FOCUS_VISUAL_TUNE_DONE
selected_lane=WARROOM_UI_VISUAL_TUNING
production_ui_code_changed=true
changed_file=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_operator_focus_nav_panel.py
warroom_page_changed=false
warroom_page_slimming_main_goal=false
command_cards_visible=true
card_row_count=3
improves_first_screen_glanceability=true
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

Q26T continues the UI tuning lane. It adds three compact command cards before the route strip:

```text
① 現在状態
② 予測表示
③ alert / operator
```

This is intended to make the first screen easier to scan without spending more time on broad file slimming.

## Safety boundary

This is visual-only UI presentation. It does not read or write runtime artifacts, trigger refreshes, enable producer/scheduler, change predictions, append ledger entries, call AutoTrade/broker APIs, or apply mode/parameter changes.
