# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q26N_WARROOM_OPERATOR_FOCUS_NAV_2026-07-01.md
# desc: PS-Q26N adds a compact externalized operator-first focus navigation panel to the WarRoom page. Layout-only display-only UI change; no producer/scheduler/AutoTrade/broker behavior.
# PS-Q26N WarRoom operator focus navigation

Updated: 2026-07-01 JST
Base: PS-Q26M WarRoom live D-hot observation audit
Mode: WarRoom UI visual cleanup / layout-only / externalized panel / display-only / no runtime writes / no scheduler or producer enablement / no trading guidance

```text
ps_q26n_warroom_operator_focus_nav=true
base_reentry=PS_Q26M_WARROOM_LIVE_D_HOT_OBSERVATION_AUDIT_DONE
selected_lane=WARROOM_UI_VISUAL_CLEANUP_INTAKE
production_ui_code_changed=true
changed_file=btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py
externalized_panel_file=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_operator_focus_nav_panel.py
warroom_page_change_boundary=import_and_single_render_call_only
operator_first_navigation_visible=true
top_expanded_default=true
row_count=5
reduces_first_screen_ambiguity=true
keeps_existing_panels_available=true
layout_only_change=true
externalized_panel_module=true
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

WarRoom has accumulated many sections and repeated safety/freshness notes. PS-Q26N adds a compact top navigation block that tells the operator what to look at first:

```text
1. 現在状態 nowcast / board・freshness
2. リアルタイム予測表示 / read model
3. ヘッダー / alert / AI operator
4. 市場証拠 / graph / active event
5. operator support / timeline / evidence
```

The navigation logic is externalized to `warroom_operator_focus_nav_panel.py` so the already-large `warroom_page.py` only imports and renders it.

## Safety boundary

This slice only changes WarRoom presentation. It does not read/write prediction/runtime/status/view artifacts, trigger UI refresh, generate predictions, enable scheduler/producer, stage/apply parameters, append ledgers, trigger AutoTrade, or call broker/private APIs.

## Next likely UI cleanup

After screenshot/manual visual review, the next slice can fold or move duplicated detail sections under clearer groupings while keeping the top focus navigation visible. Continue extracting new UI logic into small modules rather than growing `warroom_page.py`.
