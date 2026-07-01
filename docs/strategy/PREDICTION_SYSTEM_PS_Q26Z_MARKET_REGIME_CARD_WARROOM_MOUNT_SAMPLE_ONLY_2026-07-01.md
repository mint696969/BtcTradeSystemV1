# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q26Z_MARKET_REGIME_CARD_WARROOM_MOUNT_SAMPLE_ONLY_2026-07-01.md
# desc: PS-Q26Z mounts the sample-only market regime card shell in WarRoom for visual review. No live data connection.
# PS-Q26Z Market regime card WarRoom mount sample-only

Updated: 2026-07-01 JST
Base: PS-Q26Y Market regime card renderer shell
Mode: WarRoom sample-only UI mount / no live data connection / no runtime artifact write / no scheduler or producer enablement / no trading guidance

```text
ps_q26z_market_regime_card_warroom_mount_sample_only=true
base_reentry=PS_Q26Y_MARKET_REGIME_CARD_RENDERER_SHELL_DONE
selected_lane=MARKET_REGIME_CARD_WARROOM_MOUNT_SAMPLE_ONLY
market_regime_first=true
other_prediction_cards_implemented=false
production_ui_code_changed=true
warroom_page_changed=true
warroom_page_mounted=true
sample_data_only=true
live_data_connected=false
streamlit_render_function_declared=true
streamlit_render_invoked_by_page=true
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

Q26Z mounts the Q26Y market-regime card shell into the WarRoom so the operator can visually review the card row in the real page layout. The section is placed immediately after the WarRoom entry/navigation section and before the detailed quick-status section.

## Boundary

This remains sample-only. It does not connect D-hot, latest prediction, runtime state, model output, producer status, scheduler status, AutoTrade, broker, ledger, mode, or parameters.

## Visual placement

```text
最初に見る場所 / WarRoom 入口
地合いカード / sample preview
予測最新ステータス / quick status
現在状態 nowcast / board・freshness
リアルタイム予測表示 / read model
...
```

The market-regime cards are expanded by default for visual review.
