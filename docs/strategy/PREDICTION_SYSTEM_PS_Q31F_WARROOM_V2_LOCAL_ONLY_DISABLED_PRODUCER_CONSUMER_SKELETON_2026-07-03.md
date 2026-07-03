# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31F_WARROOM_V2_LOCAL_ONLY_DISABLED_PRODUCER_CONSUMER_SKELETON_2026-07-03.md
# desc: PS-Q31F WarRoom v2 local-only disabled producer/consumer skeleton behind flags.

# PS-Q31F WarRoom v2 local-only disabled producer/consumer skeleton

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31E_WARROOM_V2_STREAMLIT_SHADOW_INTEGRATION_NO_UI_DECORATION_DONE
Slice: PS-Q31F_WARROOM_V2_LOCAL_ONLY_DISABLED_PRODUCER_CONSUMER_SKELETON

## Decision

PS-Q31F adds a local-only disabled producer/consumer skeleton under `v2/transport/skeleton.py`. It provides lifecycle shape and flag semantics for the future transport path, but all effective runtime, producer, consumer, message-emission, WebSocket, and SSE flags remain disabled by default and in this slice.

```text
skeleton_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/skeleton.py
skeleton_scope=local_only_disabled_producer_consumer_shape
whole_warroom_display_update_target=true
prediction_cards_display_update_target=true
prediction_generation_out_of_scope=true
prediction_inference_out_of_scope=true
local_loop_enabled_effective=false
producer_enabled_effective=false
consumer_enabled_effective=false
message_emission_enabled=false
transport_enabled_default=false
websocket_enabled=false
sse_enabled=false
push_connected=false
runtime_connected=false
would_send_to_broker=false
```

## Skeleton responsibility

`skeleton.py` owns only disabled lifecycle packet construction. It may call existing pure helpers to build shadow producer frames and shadow consumer application packets. It must not open sockets, start a server, start a client, write artifacts, render UI, or invoke prediction generation.

```text
producer_shape=disabled_shadow_frame_source
consumer_shape=disabled_shadow_consumer_state_projection
transport_kind=local_only_disabled_in_process
operator_review_required_before_enable=true
default_effective_state=disabled
```

## Non-goals

```text
not_enabling_websocket=true
not_enabling_sse=true
not_opening_socket=true
not_emitting_messages=true
not_starting_server=true
not_starting_client=true
not_touching_streamlit_ui=true
not_replacing_streamlit_fragment_refresh=true
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
- skeleton.py exists and stays pure.
- contract exposes local-only disabled lifecycle shape.
- requested flags are recorded separately from effective flags.
- effective producer/consumer/message-emission/transport flags remain false.
- producer packet can wrap Q31B disabled shadow frame without emitting anything.
- consumer packet can project Q31D state without connecting to runtime.
- prediction-card display remains in target scope.
- prediction generation/inference remains out of scope.
- existing Q31E/Q31D/Q31C/Q31B/Q31A/Q30G-Q30C guards remain green.
```
