# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31D_WARROOM_V2_CONSUMER_STATE_DEDUP_REPLAY_HELPERS_2026-07-03.md
# desc: PS-Q31D WarRoom v2 consumer state, dedup, replay, and reconnect helpers for whole-display transport preparation.

# PS-Q31D WarRoom v2 consumer state, dedup, replay helpers

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31C_WARROOM_V2_TRANSPORT_SCHEMA_AND_TOPIC_POLICY_DONE
Slice: PS-Q31D_WARROOM_V2_CONSUMER_STATE_DEDUP_REPLAY_HELPERS

## Decision

PS-Q31D adds pure consumer-state and replay helpers under `v2/transport/`. These helpers decide whether an incoming WarRoom display update message should patch a widget region, be dropped as duplicate, or be treated as stale. They also build replay cursors and reconnect replay responses without opening sockets or touching UI rendering.

```text
consumer_state_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/consumer_state.py
replay_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/replay.py
whole_warroom_display_update_target=true
prediction_cards_display_update_target=true
prediction_generation_out_of_scope=true
prediction_inference_out_of_scope=true
classifier_invoked=false
transport_enabled_default=false
websocket_enabled=false
sse_enabled=false
push_connected=false
runtime_connected=false
would_send_to_broker=false
```

## Consumer state responsibility

`consumer_state.py` owns only per-topic/per-widget sequence and fingerprint state.

```text
state_scope=per_topic_and_widget
apply_rule=apply_first_message_or_newer_sequence_or_same_sequence_changed_fingerprint
drop_rule=drop_lower_sequence_or_same_sequence_same_fingerprint
patch_unit=widget_dom_region
broad_page_reload_required=false
idempotent_patch_required=true
```

## Replay responsibility

`replay.py` owns only cursor building, bounded replay selection, reconnect request shape, latest snapshot fallback, and gap markers.

```text
cursor_scope=topic_to_last_sequence
replay_rule=events_after_last_sequence_per_topic
replay_bound_default=32
initial_connect_behavior=latest_snapshot_per_subscribed_topic
reconnect_behavior=events_after_cursor_then_latest_snapshot_if_gap
gap_marker_allowed=true
```

## Non-goals

```text
not_enabling_websocket=true
not_enabling_sse=true
not_opening_socket=true
not_sending_messages=true
not_starting_server=true
not_starting_client=true
not_touching_streamlit_ui=true
not_invoking_prediction_generation=true
not_invoking_prediction_inference=true
not_invoking_classifier=true
not_connecting_runtime=true
not_connecting_broker=true
not_creating_order=true
not_appending_ledger=true
not_applying_mode=true
not_applying_parameter=true
```

## Acceptance criteria

```text
- consumer_state.py exists and stays pure.
- replay.py exists and stays pure.
- duplicate same-topic/same-widget/same-fingerprint messages are dropped.
- lower sequence messages are dropped as stale.
- same sequence with changed fingerprint is allowed.
- replay cursor is derived from consumer state.
- reconnect replay response is bounded and can emit latest snapshot fallback/gap marker.
- existing Q31C/Q31B/Q31A/Q30G-Q30C guards remain green.
```
