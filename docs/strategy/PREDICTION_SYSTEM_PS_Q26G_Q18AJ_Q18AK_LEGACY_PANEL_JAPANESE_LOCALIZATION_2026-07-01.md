# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q26G_Q18AJ_Q18AK_LEGACY_PANEL_JAPANESE_LOCALIZATION_2026-07-01.md
# desc: PS-Q26G Q18AJ/Q18AK legacy panel visible Japanese localization. Display-only; legacy searchable token functions preserved.
# PS-Q26G Q18AJ/Q18AK legacy panel Japanese localization

Updated: 2026-07-01 JST
Base: PS-Q26F WarRoom Japanese display review and remaining token audit
Mode: display-only / visible text localization / legacy searchable tokens preserved / no trading guidance / no writes / no scheduler / no producer enablement

```text
ps_q26g_q18aj_q18ak_legacy_panel_japanese_localization=true
base_reentry=PS_Q26F_WARROOM_JAPANESE_DISPLAY_REVIEW_REMAINING_TOKEN_AUDIT_DONE
q18aj_visible_plain_text_japanese_localized=true
q18aj_visible_rows_japanese_localized=true
q18ak_visible_plain_text_japanese_localized=true
q18ak_visible_rows_japanese_localized=true
legacy_searchable_plain_text_preserved=true
q18ap_compatibility_preserved=true
trade_guidance_added=false
trade_signal_added=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
ledger_append=false
mode_apply=false
parameter_apply=false
scheduler_enabled=false
producer_enabled=false
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
would_send_to_broker=false
```

## Purpose

Q26G localizes the visible Q18AJ/Q18AK legacy panel surface while preserving the old searchable plain-text functions used by Q18AP compatibility guards.

## Scope

```text
Q18AJ visible surface:
- operator caption
- status line
- visible plain text
- visible display rows

Q18AK visible surface:
- operator caption
- freshness/fallback status line
- visible plain text
- visible display rows
```

## Compatibility note

The legacy functions `latest_prediction_summary_widget_q18aj_searchable_plain_text` and `latest_prediction_summary_widget_q18ak_searchable_plain_text` remain available and continue to emit old searchable markers for Q18AP compatibility. The Streamlit render path now uses Japanese visible functions.

## Safety boundary

This slice is display-only. It does not add trading guidance, trade signals, producer/scheduler behavior, artifact writes, AutoTrade, broker/private API, ledger, mode, or parameter action.
