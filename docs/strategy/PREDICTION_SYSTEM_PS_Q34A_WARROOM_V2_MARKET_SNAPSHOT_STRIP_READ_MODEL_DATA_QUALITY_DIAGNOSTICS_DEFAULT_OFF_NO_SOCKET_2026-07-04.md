# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q34A_WARROOM_V2_MARKET_SNAPSHOT_STRIP_READ_MODEL_DATA_QUALITY_DIAGNOSTICS_DEFAULT_OFF_NO_SOCKET_2026-07-04.md
# desc: PS-Q34A WarRoom v2 market_snapshot_strip read-model data quality diagnostics. Default-off, read-only, no socket open, and no send.

# PS-Q34A WarRoom v2 market snapshot strip read-model data quality diagnostics default-off no-socket

Date: 2026-07-04
Profile: BtcTradeSystem
Base gate: PS_Q33M_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_LIGHTWEIGHT_STATE_TARGET_WRITE_READBACK_RESET_ROLLBACK_DEFAULT_OFF_NO_SOCKET_DONE
Slice: PS-Q34A_WARROOM_V2_MARKET_SNAPSHOT_STRIP_READ_MODEL_DATA_QUALITY_DIAGNOSTICS_DEFAULT_OFF_NO_SOCKET

## Decision

PS-Q34A adds market_snapshot_strip read-model data quality diagnostics for D-hot market overview rows. The slice exposes bid/ask crossed and spread-sign validity without changing the visible strip field contract or connecting runtime transport.

```text
market_snapshot_read_model=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/market_snapshot_read_model.py
market_snapshot_strip=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/market_snapshot_strip.py
read_model_version=prediction_warroom.v2.market_snapshot_read_model.ps_q34a.v1
bid_ask_crossed_diagnostic=true
spread_sign_valid_diagnostic=true
spread_matches_best_bid_ask_diagnostic=true
market_data_quality_state_values=NO_DATA,OK,CROSSED_BOOK,SPREAD_SIGN_INVALID,SPREAD_MISSING,SPREAD_MISMATCH
visible_field_contract_changed=false
field_count_stays_12=true
data_quality_badge_only=true
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

## D-hot evidence used for the slice

Representative D-hot market overview rows can expose `best_bid > best_ask` and negative `spread` while status files may still report `last_error=null`. Q34A therefore treats these as read-model data quality states, not transport failures and not trading signals.

## Non-goals

```text
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
- market_snapshot_read_model.py exposes data_quality_diagnostics.
- A crossed book sets bid_ask_crossed=true and market_data_quality_state=CROSSED_BOOK.
- A negative spread sets spread_sign_valid=false.
- market_snapshot_strip packet carries diagnostics as metadata and keeps field_count=12.
- WarRoom page is not modified in Q34A.
- socket_opened=false, client_started=false, client_sends_messages=false, websocket_enabled=false, runtime_connected=false, and push_connected=false.
```

## Next boundary

Q34B may add a compact read-only visual/badge policy for these diagnostics, but should remain default-off/no-socket and should not add new widgets directly to WarRoom page.
