# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q19I_WARROOM_PREDICTION_BILINGUAL_EXPLANATION_2026-06-25.md
# desc: PS-Q19I WarRoom prediction bilingual explanation layer design note.
# PS-Q19I WarRoom prediction bilingual explanation layer

Updated: 2026-06-25 JST
Branch: docs/phase2-handoff-sync

## Purpose

This slice pivots from periodic producer work back to operator comprehension. It adds a bilingual explanation layer to the PS-Q19D WarRoom realtime prediction display.

```text
ps_q19i_warroom_prediction_bilingual_explanation=true
warroom_prediction_display_ja_en_switch=true
ui_lang_session_state_consumed=true
operator_visible_bilingual_explanation=true
prediction_table_columns_localized=true
family_label_meaning_visible=true
prediction_label_meaning_visible=true
warning_meaning_visible=true
driver_meaning_visible=true
field_guide_visible=true
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
scheduler_enabled=false
producer_enabled=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Scope

Changed:

```text
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py
```

Added tests and doc only.

## Behavior

The panel now reads `st.session_state["ui_lang"]` and renders:

- English when `ui_lang=en`.
- Japanese when `ui_lang=ja`.
- A field guide explaining horizon / family / label / score / warnings / drivers.
- Per-row meanings for family, label, warnings, and drivers.
- A short operator summary emphasizing that the rows are observation support, not trade instructions.

## Safety boundary

```text
read_only=true
non_executing=true
display_only=true
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
scheduler_enabled=false
producer_enabled=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
ledger_append_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Deferred

Prediction auto-generation / periodic producer work is deferred until after this bilingual explanation layer is confirmed in the WarRoom UI.
