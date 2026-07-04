# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q34C_WARROOM_V2_MARKET_SNAPSHOT_STRIP_EVENT_PAYLOAD_CARRIES_DATA_QUALITY_METADATA_DEFAULT_OFF_NO_SOCKET_2026-07-04.md
# desc: PS-Q34C WarRoom v2 market_snapshot_strip event payload carries data quality metadata. Default-off, read-only, no socket open, and no send.

# PS-Q34C WarRoom v2 market snapshot strip event payload carries data quality metadata default-off no-socket

Date: 2026-07-04
Profile: BtcTradeSystem
Base gate: PS_Q34B_WARROOM_V2_MARKET_SNAPSHOT_STRIP_DATA_QUALITY_BADGE_POLICY_DEFAULT_OFF_NO_SOCKET_DONE
Slice: PS-Q34C_WARROOM_V2_MARKET_SNAPSHOT_STRIP_EVENT_PAYLOAD_CARRIES_DATA_QUALITY_METADATA_DEFAULT_OFF_NO_SOCKET

## Decision

PS-Q34C carries Q34A/Q34B market data quality metadata through the existing panel-event/read-model event payload path. This is a future-card/badge/balloon preparation slice only. It does not render any badge, warning, help text, or new WarRoom visible information.

```text
panel_event_bridge=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/panel_event_bridge.py
panel_event_bridge_adapter_version=prediction_warroom.v2.panel_event_bridge.ps_q34c.v1
event_payload_carries_data_quality_metadata=true
carried_metadata=market_data_quality_state,data_quality_diagnostics,data_quality_badge_policy
data_quality_metadata_carried_default=false
badge_visible_default=false
badge_render_allowed_default=false
streamlit_badge_invoked=false
visual_policy_only=true
visible_field_contract_changed=false
field_count_stays_12=true
warroom_page_modified=false
visible_controls_added=false
read_only=true
display_only=true
receiver_only=true
send_disabled=true
socket_opened=false
client_started=false
client_sends_messages=false
external_message_send_enabled=false
websocket_enabled=false
runtime_connected=false
push_connected=false
```

## Visibility policy

```text
not_rendering_badge_now=true
not_rendering_warning_now=true
not_rendering_help_text_now=true
not_adding_visible_controls=true
not_modifying_warroom_page=true
future_visual_surface=card_or_badge_or_balloon_only_when_explicitly_scoped
operator_readability_priority=true
```

## Non-goals

```text
not_connecting_runtime_transport=true
not_opening_socket=true
not_starting_client=true
not_subscribing_live=true
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
- market_snapshot_event_payload_from_strip_packet carries market_data_quality_state, data_quality_diagnostics, and data_quality_badge_policy.
- Empty/default payload has data_quality_metadata_carried=false and safe empty metadata.
- build_warroom_v2_panel_event_bridge_packet embeds the metadata in the market_snapshot_event read-model payload.
- No new visible fields are added to the market_snapshot_strip fields map.
- WarRoom page is not modified in Q34C.
- socket_opened=false, client_started=false, client_sends_messages=false, websocket_enabled=false, runtime_connected=false, and push_connected=false.
```

## Next boundary

Q34D should stop the market-snapshot visibility chain unless a specific visual surface is explicitly scoped. Reasonable next work is either a compact card/balloon proposal document for necessary warnings or returning to the broader WarRoom v2 WebSocket receiver/page-mount path without adding unnecessary visible information.
