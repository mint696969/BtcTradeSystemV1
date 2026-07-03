# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31G_WARROOM_V2_OPERATOR_REVIEWED_LOCAL_TRANSPORT_ENABLEMENT_GATE_2026-07-03.md
# desc: PS-Q31G WarRoom v2 operator-reviewed local transport enablement gate contract.

# PS-Q31G WarRoom v2 operator-reviewed local transport enablement gate

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q31F_WARROOM_V2_LOCAL_ONLY_DISABLED_PRODUCER_CONSUMER_SKELETON_DONE
Slice: PS-Q31G_WARROOM_V2_OPERATOR_REVIEWED_LOCAL_TRANSPORT_ENABLEMENT_GATE

## Decision

PS-Q31G adds a pure operator-reviewed gate contract under `v2/transport/gates.py`. It evaluates whether the previous disabled transport preparation slices are complete enough to request a future local-only transport experiment. It does not enable transport in this slice.

```text
gate_module=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/gates.py
gate_scope=operator_reviewed_local_transport_enablement_decision_contract
whole_warroom_display_update_target=true
prediction_cards_display_update_target=true
prediction_generation_out_of_scope=true
prediction_inference_out_of_scope=true
approval_required_before_enable=true
approval_recorded_default=false
candidate_transport_path_default=local_only_in_process
transport_enabled_effective=false
local_loop_enabled_effective=false
producer_enabled_effective=false
consumer_enabled_effective=false
message_emission_enabled=false
websocket_enabled=false
sse_enabled=false
push_connected=false
runtime_connected=false
would_send_to_broker=false
```

## Gate responsibility

`gates.py` owns only a review packet and deterministic gate evaluation. It may summarize guard evidence from Q31B-Q31F and classify the next path as blocked, needs review, or ready for a future slice. It must not open sockets, start a server, start a client, emit messages, render UI, write artifacts, or invoke prediction generation.

```text
approval_token_required=APPROVE_Q31G_LOCAL_ONLY_SHADOW_EXPERIMENT
approved_result=ready_for_next_slice_not_enabled_here
not_enabled_here=true
next_slice_after_approval=PS-Q31H_LOCAL_ONLY_TRUE_TRANSPORT_EXPERIMENT
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
- gates.py exists and stays pure.
- missing guard evidence blocks the gate.
- missing operator approval blocks the gate.
- explicit local-only approval can mark next-slice readiness, but does not enable transport here.
- SSE/WebSocket are not candidate defaults.
- prediction-card display remains in target scope.
- prediction generation/inference remains out of scope.
- existing Q31F/Q31E/Q31D/Q31C/Q31B/Q31A/Q30G-Q30C guards remain green.
```
