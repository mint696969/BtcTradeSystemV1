# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_16_SINGLE_ORIGIN_WRITER_PREFLIGHT_2026-07-14.md
# desc: Defines MR-F6.16 explicit-candidate single-origin writer preflight without write execution.

# Prediction System MarketRegime MR-F6.16 Single-origin Writer Preflight

Updated: 2026-07-14 JST
Status: implementation slice
Gate: MR_F6_MANDATORY_SIMPLE_BASELINE_COMPARISON

## Responsibility

MR-F6.16 connects one ready MR-F6.15 runtime feature bundle to:

```text
one immutable prediction origin
one feature snapshot, cryptographically bound across packet and runtime bundle
seven canonical horizons
seven immutable origin-evidence bundles
one deterministic append-only write plan
optional operator-approved writer preflight
```

## Identity separation

Forecast model parameter identity and origin-feature parameter identity are different contracts.

```text
forecast_parameter_set_ids = identities already carried by the seven forecasts
origin_feature_parameter_set_id = exact MR-F6.10 shadow feature parameter set
shadow_candidate_id = same exact MR-F6.10 candidate ID
```

The origin-feature candidate ID is not injected into forecast `parameter_set_id`. The runtime feature bundle must carry the same `feature_bundle_generated_at` and deterministic `feature_snapshot_ref` as the forecast packet; cross-snapshot mixing fails closed.

## Approval behavior

Without approval, the bridge builds and hashes the seven bundles but returns:

```text
preflight_ready=false
blockers=[operator_approval_missing]
```

With a valid active approval, it calls only `preflight_origin_evidence_write`. The resulting nested writer preflight may state that the separately gated writer would be permitted, but the MR-F6.16 outer artifact always remains non-executing.

## Boundary

```text
preflight_only=true
write_allowed=false
would_write=false
writer_invoked=false
write_execution_performed=false
writes_dhot=false
scheduler_enabled=false
counts_as_real_shadow_evidence=false
candidate_selection_performed=false
live_parameter_apply_allowed=false
auto_promotion_allowed=false
canonical_replacement_allowed=false
```

MR-F6.17 may define a human-reviewed once-only execution request artifact. It must not call the writer or modify D-hot as part of request construction.
