# path: ./docs/strategy/PREDICTION_SYSTEM_PS_F_COMPLETE_11_FAMILY_REVIEW_BTC_BITFLYER_2026-06-19.md
# desc: PS-F completion review for 11-family rule_based_v0 coverage and next standalone Prediction System implementation direction.

# Prediction System PS-F Complete 11-Family Review

Updated: 2026-06-19 JST  
Profile: BtcTradeSystem  
Branch: `docs/phase2-handoff-sync`  
Scope: standalone Prediction System only  
Status: review / non-executing / no behavior change

## 1. Decision summary

PS-F is functionally complete at the rule-output coverage level.

The standalone Prediction System now has deterministic `rule_based_v0` output coverage for all 11 original prediction families and the PS-G-lite runner can emit all 11 families across the requested horizons.

Current result:

```text
build_rule_based_v0_outputs(...) emits 11 families per horizon.
build_prediction_system_result(...) emits 11 families per horizon.
short_horizon 5m / 10m / 15m emits 33 outputs.
ScenarioCoreOutput-lite surfaces family labels through gpt_review_digest and selected machine fields.
All outputs remain read-only and non-executing.
```

This does not mean the Prediction System is complete. It means the missing-family gap identified in PS-B has been closed enough to move from family coverage to scenario integration and/or feature-depth work.

## 2. Hard boundaries preserved

PS-F preserved the standalone Prediction System boundary:

```text
No AutoTrade runtime import in system.py.
No Collector runtime import.
No broker/private API call.
No live collection.
No external API call.
No artifact writes.
No append_decision_jsonl behavior.
No command ledger append.
No mode apply.
No Pre-Armed grant behavior.
No WarRoom/UI runtime dependency.
```

Prediction System remains a producer of market-reading outputs, not an execution owner.

## 3. Current 11-family coverage

`btcts_next/src/btcts/prediction/rule_based_v0.py` now covers:

| # | Family | PS-F status | Current v1 implementation quality |
|---:|---|---|---|
| 1 | `market_regime` | implemented before PS-F | basic technical + cross-venue summary |
| 2 | `trend_bias` | implemented before PS-F | basic MA/VWAP direction |
| 3 | `reversal_zone` | added in PS-F3 | summary-based support/resistance/VWAP/wick/range reaction proxy |
| 4 | `volatility_risk` | implemented before PS-F | basic volatility state |
| 5 | `liquidity_execution_quality` | added in PS-F5 | summary-based liquidity proxy, not true orderbook/spread/depth |
| 6 | `breakout_false_break` | added in PS-F6 | summary-based breakout/false-break proxy, not retest/volume/orderbook model |
| 7 | `opportunity_participation` | added in PS-F7 | summary-based participation/no-edge proxy, not outcome/near-miss driven yet |
| 8 | `cross_venue_confirmation` | implemented before PS-F | snapshot dispersion + Spot-FX basis skeleton |
| 9 | `macro_risk_context` | added in PS-F9 | context/warning only, no live macro provider and not direction owner |
| 10 | `human_technical_structure` | implemented before PS-F | basic chart-structure proxy |
| 11 | `algorithmic_participant_footprint` | added in PS-F11 | summary-based footprint proxy, no live tradeflow/orderbook collection |

## 4. PS-F slices completed

Completed and committed sequence:

```text
PS-G-lite: standalone multi-horizon runner over existing family logic
PS-F3: reversal_zone deterministic v1
PS-F5: liquidity_execution_quality deterministic v1
PS-F6: breakout_false_break deterministic v1
PS-F7: opportunity_participation deterministic v1
PS-F9: macro_risk_context deterministic v1
PS-F11: algorithmic_participant_footprint deterministic v1
```

PS-F intentionally skipped heavy feature construction and live data collection. The purpose was to close family-output coverage first while preserving the Collector/Prediction/AutoTrade boundaries.

## 5. Current output shape after PS-F

For `short_horizon`:

```text
horizons: 300 / 600 / 900 sec
families per horizon: 11
outputs: 33
forecast_batch.record_count: 33
```

The runner also supports:

```text
nowcast: 15 / 30 / 60 sec
mid_horizon: 1800 / 3600 sec
long_horizon: 14400 / 86400 sec
```

Current top-level runner:

```text
btcts_next/src/btcts/prediction/system.py
build_prediction_system_result(...)
```

Current family runner:

```text
btcts_next/src/btcts/prediction/rule_based_v0.py
build_rule_based_v0_outputs(...)
```

## 6. What PS-F did not solve

PS-F did not make the Prediction System operationally complete.

Major remaining gaps:

```text
ScenarioCoreOutput is still lite/basic.
evidence_weighting_summary is still rule_based_v0_unweighted.
evidence_conflict_state is still basic_bundle_only_ps_g_lite.
continuation_vs_reversal_balance is not evaluated.
turning_point_risk is not evaluated.
invalidation_state is not evaluated.
rewrite_state is not evaluated.
scenario_switch_hint is not evaluated.
what_to_watch_next is not generated.
refresh_required remains basic/default.
revision diff is not implemented.
outcome/hit/miss explanation is not wired into family scoring.
provider reliability registry is not implemented.
parameter lifecycle/comparison/rollback is not implemented.
feature layer for orderbook/tradeflow/liquidity/footprint is still weak.
```

## 7. Weak/proxy-only family index

The following families are useful as deterministic first pass but should be treated as proxy-only:

| Family | Current weakness | Needed future strengthening |
|---|---|---|
| `liquidity_execution_quality` | no board spread/depth/thin-book/slippage input | PS-E orderbook/depth/spread features |
| `breakout_false_break` | no retest/volume/tradeflow confirmation | PS-E breakout/retest/volume/tradeflow features |
| `opportunity_participation` | no forecast/outcome/near-miss/missed-opportunity ledger input | PS-J outcome explanation + near-miss calibration |
| `macro_risk_context` | no macro/calendar/session/provider registry | PS-D provider reliability + PS-E macro/session context snapshots |
| `algorithmic_participant_footprint` | no live tradeflow/orderbook/cancel-reprice footprint | PS-E tradeflow/orderbook/footprint features |
| `cross_venue_confirmation` | lead/lag remains snapshot skeleton | PS-D/PS-E provider reliability and time-series lead/lag context |

These proxy-only families must not be over-weighted as final trading signals.

## 8. Recommended next work: PS-H before PS-E

The next implementation should be PS-H-lite / PS-H1: Scenario Core integration and evidence weighting.

Reason:

```text
All 11 families now emit outputs, but the system does not yet integrate them into a real scenario.
Adding more low-level features before scenario integration risks producing more signals without a coherent decision model.
```

Recommended next slice:

```text
PS-H1: Scenario Core lite integration
```

First PS-H1 should remain deterministic and non-executing.

Minimum PS-H1 target:

```text
replace not_evaluated_ps_g_lite placeholders with deterministic scenario summaries
compute continuation_vs_reversal_balance from trend/reversal/breakout/human-technical families
compute turning_point_risk from reversal/volatility/algorithmic footprint families
compute evidence_conflict_state from trend/cross/liquidity/breakout/macro disagreements
compute scenario_switch_hint from false_break/reversal/divergence/high volatility labels
compute invalidation_state basic values from trend + reversal + breakout conflict
add what_to_watch_next candidates in gpt_review_digest or scenario_trace
keep trigger_eligibility blocked
keep no AutoTrade / Collector / broker / append / mode / grant behavior
```

After PS-H1, the next major path should be:

```text
PS-E: feature layer strengthening for orderbook/tradeflow/liquidity/footprint inputs
```

## 9. Guard policy after PS-F

Future guards should continue to verify:

```text
all 11 families remain present in INITIAL_FAMILIES
short_horizon emits 33 outputs for 3 horizons
no Collector runtime import
no AutoTrade runtime import in system.py
no broker/private API markers
no append_decision_jsonl
no live collection / external API call in rule_based_v0/system.py
read_only / non_executing flags remain true
would_send_to_broker / mode_apply_requested / command_ledger_append_requested remain false
```

## 10. PS-F completion conclusion

PS-F closes the original missing 6-family implementation gap from PS-B.

Current Prediction System state:

```text
Foundation contracts exist.
Standalone runner exists.
All 11 families emit deterministic outputs.
Multi-horizon runner can produce a full 11-family output set.
Scenario integration remains the next bottleneck.
Feature depth remains intentionally shallow for several families.
```

Therefore the recommended next step is:

```text
PS-H1: Scenario Core lite integration and evidence weighting.
```
