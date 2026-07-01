# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q26S_WARROOM_OPERATOR_FOCUS_VISUAL_TUNE_2026-07-01.md
# desc: PS-Q26S tunes WarRoom operator focus entry visuals without additional warroom_page slimming.
# PS-Q26S WarRoom operator focus visual tune

Updated: 2026-07-01 JST
Base: PS-Q26R WarRoom quick-status panel extraction
Mode: WarRoom UI visual tuning / operator-first scanability / display-only / no runtime writes / no scheduler or producer enablement / no trading guidance

```text
ps_q26s_warroom_operator_focus_visual_tune=true
base_reentry=PS_Q26R_WARROOM_QUICK_STATUS_PANEL_EXTRACTION_DONE
selected_lane=WARROOM_UI_VISUAL_TUNING
production_ui_code_changed=true
changed_file=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_operator_focus_nav_panel.py
warroom_page_changed=false
warroom_page_slimming_main_goal=false
visual_route_strip_visible=true
improves_first_screen_scanability=true
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

After Q26R, avoid spending more time on file slimming. PS-Q26S returns to the main goal: WarRoom first-screen visual tuning.

The operator focus entry now shows a short route strip before the detailed table:

```text
読む順: ① 現在状態 → ② 予測表示 → ③ alert/operator → ④⑤ 理由確認
```

This keeps the existing detailed rows and panels available while making the first glance easier.

## Safety boundary

This is visual-only UI presentation. It does not read or write runtime artifacts, trigger refreshes, enable producer/scheduler, change predictions, append ledger entries, call AutoTrade/broker APIs, or apply mode/parameter changes.
