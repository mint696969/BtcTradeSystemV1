# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q35I_WARROOM_V2_WEBSOCKET_RECEIVER_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_READBACK_STATUS_NO_SOCKET_NO_SEND_2026-07-04.md
# desc: PS-Q35I WarRoom v2 WebSocket receiver page-mount compact status badge readback status. One visible line, no socket open, and no send.

# PS-Q35I WarRoom v2 WebSocket receiver page-mount compact status badge readback status no-socket no-send

Date: 2026-07-04
Profile: BtcTradeSystem
Base gate: PS_Q35H_WARROOM_V2_WEBSOCKET_RECEIVER_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_READBACK_COUNT_NO_SOCKET_NO_SEND_DONE
Slice: PS-Q35I_WARROOM_V2_WEBSOCKET_RECEIVER_PAGE_MOUNT_PATH_COMPACT_STATUS_BADGE_READBACK_STATUS_NO_SOCKET_NO_SEND

## Decision

PS-Q35I makes the compact receiver badge more truthful by separating mount readiness from receiver readback readiness. The badge remains exactly one visible markdown line and now displays readback=ready, readback=blocked, or readback=unknown using only the existing hidden observation packet.

```text
module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_page_mount_path_compact_status_badge.py
compact_status_badge_readback_status_version=prediction_warroom.v2.transport.ws_receiver_only_client_page_mount_path_compact_status_badge_readback_status.ps_q35i.v1
selected_visible_surface=compact_status_badge
readback_count_display_enabled=true
readback_status_display_enabled=true
rendered_line_template=`WS Receiver` mount ready · readback={ready|blocked|unknown} · msgs={receiver_state_message_count} · no socket/send
one_compact_line_only=true
visible_surface_implemented_now=true
visible_surface_implementation_allowed_now=true
warroom_page_modified=true
warroom_page_visible_ui_modified=true
q35i_warroom_page_delta_modified=false
q35i_warroom_page_visible_ui_delta_modified=false
visible_information_added=true
visible_controls_added=false
renders_badge_now=true
renders_card_now=false
renders_balloon_now=false
renders_warning_now=false
renders_help_text_now=false
streamlit_markdown_only=true
receiver_only=true
send_disabled=true
socket_opened=false
client_started=false
client_sends_messages=false
external_message_send_enabled=false
websocket_enabled=false
runtime_connected=false
push_connected=false
target_session_state_mutated=false
state_mutated=false
aggregator_exports_added=false
```

## Rendered line template

```text
`WS Receiver` mount ready · readback={ready|blocked|unknown} · msgs={receiver_state_message_count} · no socket/send
```

## Non-goals

```text
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
not_adding_aggregator_exports=true
not_adding_visible_controls=true
not_rendering_card_now=true
not_rendering_balloon_now=true
not_rendering_warning_now=true
not_rendering_help_text_now=true
```

## Acceptance criteria

```text
- Badge remains one compact visible line.
- Q35I does not modify WarRoom page; it only changes the existing badge packet/text contract.
- Missing hidden observation displays readback=unknown and msgs=0.
- Ready hidden observation displays readback=ready.
- Blocked hidden observation displays readback=blocked.
- Badge still renders only when the existing Q32Y visible mount point allows markdown.
- No socket/client/send/broker/ledger/prediction path is added.
- transport/__init__.py and v2/__init__.py are not modified for Q35I exports.
```

## Next boundary

Continue bundled low-risk visible read-only UI/readback/docs/tests. Keep socket/client/send/broker/order/ledger/mode/parameter/prediction/runtime-write boundaries narrow.
