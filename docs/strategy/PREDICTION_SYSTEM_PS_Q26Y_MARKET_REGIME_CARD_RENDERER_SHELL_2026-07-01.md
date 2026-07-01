# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q26Y_MARKET_REGIME_CARD_RENDERER_SHELL_2026-07-01.md
# desc: PS-Q26Y adds a market regime card renderer shell using static Q26X card specs. No live data or WarRoom page mount.
# PS-Q26Y Market regime card renderer shell

Updated: 2026-07-01 JST
Base: PS-Q26X Market regime card contract
Mode: UI renderer shell / sample data only / no live data connection / no WarRoom page mount / no runtime artifact write / no scheduler or producer enablement / no trading guidance

```text
ps_q26y_market_regime_card_renderer_shell=true
base_reentry=PS_Q26X_MARKET_REGIME_CARD_CONTRACT_DONE
selected_lane=MARKET_REGIME_CARD_RENDERER_SHELL_UI_ONLY
market_regime_first=true
other_prediction_cards_implemented=false
production_ui_code_changed=true
warroom_page_changed=false
warroom_page_mounted=false
sample_data_only=true
live_data_connected=false
streamlit_render_function_declared=true
streamlit_render_invoked_by_page=false
horizontal_scroll_required=true
cards_do_not_shrink=true
full_width_target_horizon=24時間後
detail_disclosure_available=true
dialog_popup_planned_later=true
freshness_encoded_by_badge_only=true
border_meaning=evidence_quality
background_tone_is_readability_first=true
confidence_meaning=market_regime_classification_certainty_not_win_rate
read_only=true
display_only=true
non_executing=true
runtime_read_allowed=false
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

Q26Y creates the visual shell for market-regime cards using static Q26X card specs. The cards are horizontal, do not shrink, and can scroll horizontally when the window is narrow. This prepares the UI shape before any live-data wiring.

## Implemented UI shell behavior

```text
horizons=現在,5分後,15分後,30分後,60分後,6時間後,12時間後,24時間後
card_body=line_1_regime,line_2_confidence,line_3_short_tag
freshness=badge_only
border=evidence_quality
background=readability_first_pale_tone
narrow_window=horizontal_scroll_not_card_shrink
long_text=details_disclosure_now_dialog_later
```

## Boundary

This slice does not mount the panel into `warroom_page.py`. It does not read D-hot data, runtime artifacts, latest predictions, or live state. It does not implement other prediction cards.

## Safety boundary

Display-only shell. No runtime write, status write, prediction artifact write, view artifact write, scheduler/producer enablement, AutoTrade/broker access, ledger append, mode apply, or parameter apply.
