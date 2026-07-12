# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_4_EXPLICIT_EVIDENCE_ADAPTER_AND_SHADOW_PACKET_2026-07-12.md
# desc: MR-F5.4 design and safety boundary for explicit feature/signal adaptation into a shadow-only future MarketRegime packet.

# Prediction System MarketRegime MR-F5.4 Explicit Evidence Adapter and Shadow Packet

Updated: 2026-07-12 JST
Status: implementation slice prepared
Scope: pure adapter and shadow-only packet

## Inputs

```text
MarketRegimeFeatureBundle
signal_score_report from score_market_regime_signals
origin_current_state
origin_timestamp_epoch_sec
source_timestamp_epoch_sec
```

The adapter does not read D-hot and does not call the current-state estimator. The caller must supply the already accepted current state and explicit timestamped evidence.

## Behavior

```text
validate source_snapshot_ok
validate market_regime_only score report
require each canonical future horizon score row exactly once
map available feature groups into MR-F5 feature-family names
compute deterministic feature_snapshot_ref
build FutureBaselineEvidence per horizon
run transparent shadow baseline
validate complete seven-horizon packet
```

Long-horizon `session_context` is not synthesized. If absent, 6h/12h/24h forecasts abstain.

## Packet boundary

The output is `MarketRegimeFutureShadowPacket`, not the existing canonical `MarketRegimePredictionPacket`. It is not consumed by `regime_classifier.py`, latest writer, UI, or outcome resolver in this slice.

## Safety

```text
shadow_only=true
canonical_future_label_replacement=false
d_hot_read=false
d_hot_write=false
writer_change=false
ui_change=false
scheduler_change=false
calibrated_probability_claim=false
broker_private_api=false
autotrade=false
order_submission=false
```
