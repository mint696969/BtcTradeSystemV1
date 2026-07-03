# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31X_WARROOM_V2_REALTIME_JAPANESE_READ_SURFACE_WS_DISPLAY_TARGET_CONTRACT_2026-07-03.md
# desc: PS-Q31X WarRoom v2 realtime Japanese read surface WS display target contract. Contract only; no socket and no UI mount.

# PS-Q31X WarRoom v2 realtime Japanese read surface WS display target contract

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31W_WARROOM_V2_VISIBLE_PANEL_GATE_TO_HIDDEN_SESSION_STATE_NO_UI_MOUNT_DONE
Slice: PS-Q31X_WARROOM_V2_REALTIME_JAPANESE_READ_SURFACE_WS_DISPLAY_TARGET_CONTRACT

## Small goal alignment

The current small goal is not prediction expansion or trading logic. The goal is:

```text
current_small_goal=warroom_tab_ws_push_realtime_update_and_japanese_readability
```

WarRoom must become a Japanese-readable manual-trading information board that updates seamlessly through WebSocket push. Prediction enrichment comes later, then trading logic after that.

## Decision

PS-Q31X records the WarRoom v2 display surfaces that must be fed by the future WebSocket display push plane. It also fixes the Japanese reading order and labels for the current WarRoom tab. This slice is contract-only: it does not open sockets, mount new UI, render visible panels, call prediction generation, or touch trading logic.

```text
surface_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/realtime_read_surface.py
current_small_goal=warroom_tab_ws_push_realtime_update_and_japanese_readability
websocket_display_push_required=true
bidirectional_websocket_premise=true
read_model_push_plane=server_to_warroom_ui
command_intent_plane=warroom_ui_or_autotrade_to_order_intent_gateway
japanese_readable_now_target=true
manual_trading_information_board=true
prediction_enrichment_deferred=true
trading_logic_deferred=true
order_logic_deferred=true
browser_timer_polling_is_legacy_compat_only=true
browser_timer_reload_replacement_target=true
no_new_polling_fallback=true
no_browser_timer_reload_introduced=true
websocket_enabled=false
socket_opened=false
external_message_send_enabled=false
order_intent_submitted=false
broker_send_enabled=false
would_send_to_broker=false
```

## Japanese reading order

```text
1. 地合い・安全境界
2. 現在価格・板・鮮度
3. 予測カード
4. シナリオ日本語要約
5. チャート確認
6. 操作判断メモ
```

## WS display targets

```text
warroom.current_state -> 地合い・現在状態
warroom.alerts -> 警告
warroom.safety -> 安全境界
warroom.market.snapshot -> 現在価格・板・鮮度
warroom.prediction.* -> 予測カード
warroom.prediction.scenario_ja -> シナリオ日本語要約
warroom.chart.review -> チャート確認
```

## Non-goals

```text
not_mounting_panel_into_warroom=true
not_rendering_streamlit=true
not_enabling_websocket=true
not_opening_socket=true
not_sending_external_messages=true
not_using_polling_fallback=true
not_using_browser_timer_reload=true
not_submitting_order_intent=true
not_sending_order_to_broker=true
not_appending_live_order_ledger=true
not_applying_mode=true
not_applying_parameter=true
not_invoking_prediction_generation=true
not_invoking_prediction_inference=true
not_invoking_classifier=true
```

## Acceptance criteria

```text
- realtime_read_surface.py exists and stays pure.
- current small goal is explicit.
- WebSocket display push is required as the target update method.
- browser timer polling is marked legacy compatibility only.
- Japanese reading order and labels are explicit.
- display targets include current state, alerts, safety, market snapshot, prediction cards, scenario_ja, and chart review.
- no socket, no UI mount, no external send, no OrderIntent, no broker, no ledger, no mode, no parameter, and no prediction generation/inference/classifier.
- existing Q31W-Q30C guards remain green.
```
