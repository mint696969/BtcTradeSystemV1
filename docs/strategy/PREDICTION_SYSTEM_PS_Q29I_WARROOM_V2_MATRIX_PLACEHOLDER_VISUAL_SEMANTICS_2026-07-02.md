# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29I_WARROOM_V2_MATRIX_PLACEHOLDER_VISUAL_SEMANTICS_2026-07-02.md
# desc: PS-Q29I WarRoom v2 matrix placeholder visual semantics policy.

# PS-Q29I WarRoom v2 matrix placeholder visual semantics

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29H_WARROOM_V2_SCENARIO_PLACEHOLDER_COMPOSITION_DONE
Slice: PS-Q29I_WARROOM_V2_MATRIX_PLACEHOLDER_VISUAL_SEMANTICS

## Decision

Make WarRoom v2 matrix cards read visual semantics from card payload fields while preserving Q26W/Q27E meaning separation.

```text
background_tone=tradability_or_readability_or_risk_temperature
freshness=badge_only
border=evidence_quality
background_color_never_encodes_freshness=true
freshness_not_encoded_by_border=true
freshness_encoded_by_badge_only=true
```

This is still placeholder-only. It does not connect live data or infer real card state.

## Non-goals

```text
not_connecting_dhot=true
not_invoking_classifier=true
not_enabling_websocket=true
not_enabling_sse=true
not_enabling_scheduler_or_producer=true
not_touching_autotrade_broker_ledger_mode_parameter=true
not_changing_app_route=true
not_changing_warroom_v2_page=true
not_changing_legacy_warroom=true
```
