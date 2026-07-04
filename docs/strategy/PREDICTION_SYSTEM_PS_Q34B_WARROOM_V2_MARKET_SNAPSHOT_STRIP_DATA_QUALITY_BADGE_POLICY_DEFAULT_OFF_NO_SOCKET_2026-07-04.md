# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q34B_WARROOM_V2_MARKET_SNAPSHOT_STRIP_DATA_QUALITY_BADGE_POLICY_DEFAULT_OFF_NO_SOCKET_2026-07-04.md
# desc: PS-Q34B WarRoom v2 market_snapshot_strip data quality badge policy metadata. Default-off, read-only, no socket open, and no send.

# PS-Q34B WarRoom v2 market snapshot strip data quality badge policy default-off no-socket

Date: 2026-07-04
Profile: BtcTradeSystem
Base gate: PS_Q34A_WARROOM_V2_MARKET_SNAPSHOT_STRIP_READ_MODEL_DATA_QUALITY_DIAGNOSTICS_DEFAULT_OFF_NO_SOCKET_DONE
Slice: PS-Q34B_WARROOM_V2_MARKET_SNAPSHOT_STRIP_DATA_QUALITY_BADGE_POLICY_DEFAULT_OFF_NO_SOCKET

## Decision

PS-Q34B adds compact read-only badge policy metadata for Q34A market data quality diagnostics. It does not render the badge by default and does not modify WarRoom page. The policy maps data quality states to severity, token, Japanese label, and operator guidance.

```text
market_snapshot_strip=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/market_snapshot_strip.py
renderer_version=prediction_warroom.v2.market_snapshot_strip_renderer.ps_q34b.v1
data_quality_badge_policy_version=prediction_warroom.v2.market_snapshot_data_quality_badge_policy.ps_q34b.v1
data_quality_badge_policy_default_visible=false
badge_render_allowed_default=false
streamlit_badge_invoked=false
visual_policy_only=true
field_count_stays_12=true
visible_field_contract_changed=false
badge_state_OK=normal
badge_state_CROSSED_BOOK=danger
badge_state_SPREAD_SIGN_INVALID=warning
badge_state_SPREAD_MISMATCH=warning
badge_state_SPREAD_MISSING=muted
badge_state_NO_DATA=muted
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

## Non-goals

```text
not_rendering_badge_now=true
not_adding_visible_controls=true
not_modifying_warroom_page=true
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
- market_snapshot_strip packet exposes data_quality_badge_policy metadata.
- OK maps to normal severity.
- CROSSED_BOOK maps to danger severity but remains metadata-only and default-hidden.
- SPREAD_SIGN_INVALID and SPREAD_MISMATCH map to warning severity.
- field_count remains 12 and no data-quality field is added to field_keys.
- WarRoom page is not modified in Q34B.
- socket_opened=false, client_started=false, client_sends_messages=false, websocket_enabled=false, runtime_connected=false, and push_connected=false.
```

## Next boundary

Q34C may add an event-payload/read-model bridge policy for carrying the badge metadata through transport envelopes, still default-off/no-socket and without new WarRoom page widgets.
