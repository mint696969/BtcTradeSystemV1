# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31Z_WARROOM_V2_WS_DISPLAY_ADAPTER_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_SOCKET_2026-07-03.md
# desc: PS-Q31Z WarRoom v2 hidden session_state WS display adapter observation. No socket and no UI mount.

# PS-Q31Z WarRoom v2 WS display adapter observation to hidden session state

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31Y_WARROOM_V2_WS_DISPLAY_PUSH_TRANSPORT_ADAPTER_CONTRACT_NO_SOCKET_DONE
Slice: PS-Q31Z_WARROOM_V2_WS_DISPLAY_ADAPTER_OBSERVATION_TO_HIDDEN_SESSION_STATE_NO_SOCKET

## Decision

PS-Q31Z records the Q31Y no-socket WS display adapter/outbox observation in the WarRoom Streamlit render path as hidden `session_state` only. It keeps the current small goal focused on WarRoom tab realtime WebSocket push and Japanese readability, while still opening no socket and sending no messages.

```text
observation_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_display_adapter_observation.py
state_key=warroom_v2_ws_display_adapter_observation_q31z
input_pipeline=q31x_realtime_japanese_read_surface,q31y_ws_display_adapter_contract
current_small_goal=warroom_tab_ws_push_realtime_update_and_japanese_readability
streamlit_path_messages=[]
websocket_display_push_required=true
websocket_display_push_main_path=true
bidirectional_websocket_premise=true
read_model_push_plane=server_to_warroom_ui
browser_timer_polling_is_legacy_compat_only=true
browser_timer_refresh_replacement_target=true
no_new_polling_fallback=true
no_browser_timer_reload_introduced=true
warroom_diagnostic_policy=minimal_status_only
detailed_diagnostics_default_surface=audit_or_diagnostics_tab
socket_opened=false
adapter_sends_messages=false
external_message_send_enabled=false
websocket_enabled=false
runtime_connected=false
push_connected=false
order_intent_submitted=false
broker_send_enabled=false
would_send_to_broker=false
```

## WarRoom readability policy

WarRoom keeps only compact operator status. Detailed diagnostics remain hidden and belong to Audit/Diagnostics unless promoted later as a compact warning.

```text
diagnostic_minimal_summary_allowed_in_warroom=true
allowed_warroom_diagnostic_summary_fields=safety_state,data_freshness,transport_state,last_update_age
warroom_visible_diagnostic_panel_default=false
visible_panel_render_plan_deprioritized=true
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
- ws_display_adapter_observation.py exists and stays pure.
- WarRoom page records hidden WS display adapter observation state only.
- Existing visible WarRoom layout remains unchanged.
- Default Streamlit path uses messages=[].
- Outbox message_count defaults to 0 and dropped_count defaults to 0.
- WS display push remains the main path but socket_opened=false and adapter_sends_messages=false.
- Browser timer polling remains legacy compatibility only; no new polling or browser reload fallback is introduced.
- Detailed diagnostics remain outside the main WarRoom tab by default.
- no UI mount, no external send, no OrderIntent, no broker, no ledger, no mode, no parameter, and no prediction generation/inference/classifier.
- existing Q31Y-Q30C guards remain green.
```
