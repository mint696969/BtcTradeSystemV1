# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31H_WARROOM_V2_LOCAL_ONLY_TRUE_TRANSPORT_EXPERIMENT_2026-07-03.md
# desc: PS-Q31H WarRoom v2 local-only true transport experiment after Q31G approval.

# PS-Q31H WarRoom v2 local-only true transport experiment

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31G_WARROOM_V2_OPERATOR_REVIEWED_LOCAL_TRANSPORT_ENABLEMENT_GATE_DONE
Slice: PS-Q31H_WARROOM_V2_LOCAL_ONLY_TRUE_TRANSPORT_EXPERIMENT
Approval: APPROVE_Q31G_LOCAL_ONLY_SHADOW_EXPERIMENT

## Decision

PS-Q31H adds a pure local-only in-process transport experiment under `v2/transport/local_loop.py`. The experiment can mark a local producer→consumer handoff as effective only when the Q31G gate evidence passes and the explicit approval token is supplied. It does not open sockets, start a server, start a client, touch Streamlit UI, or send messages outside the process.

```text
local_loop_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/local_loop.py
transport_kind=local_only_in_process
approval_token_required=APPROVE_Q31G_LOCAL_ONLY_SHADOW_EXPERIMENT
whole_warroom_display_update_target=true
prediction_cards_display_update_target=true
prediction_generation_out_of_scope=true
prediction_inference_out_of_scope=true
websocket_enabled=false
sse_enabled=false
push_connected=false
runtime_connected=false
would_send_to_broker=false
external_message_send_enabled=false
streamlit_ui_touched=false
```

## Experiment responsibility

`local_loop.py` owns only local in-process packet handoff. When approved, it returns an in-memory outbox and applies those normalized messages to Q31D consumer state. When not approved, it returns a blocked packet with no emitted messages.

```text
approved_effective_flags=transport_enabled,local_loop_enabled,producer_enabled,consumer_enabled,message_emission_enabled
message_emission_scope=in_process_return_value_only
external_transport_scope=none
operator_review_required=true
```

## Non-goals

```text
not_enabling_websocket=true
not_enabling_sse=true
not_opening_socket=true
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
- local_loop.py exists and stays pure.
- without Q31G approval, emitted_message_count remains 0.
- with Q31G approval and guard evidence, local-only effective flags can become true.
- external transport flags remain false even when local-only effective flags are true.
- producer outbox contains only normalized display-topic messages.
- consumer state projection uses Q31D consumer helpers.
- prediction-card display remains in target scope.
- prediction generation/inference remains out of scope.
- existing Q31G-Q30C guards remain green.
```
