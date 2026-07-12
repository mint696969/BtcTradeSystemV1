# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_IMPLEMENTATION_HANDOFF_2026-07-12.md
# desc: Canonical implementation handoff for MR-F5 horizon-specific future-regime forecasting.

# Prediction System MarketRegime MR-F5 Implementation Handoff

Updated: 2026-07-12 JST
Checkpoint: MR_F5_HORIZON_SPECIFIC_FUTURE_FORECAST_IMPLEMENTATION_READINESS
Status: ready to begin
Reference head: b5d55752
Current gate: MR_F4_TRANSITION_AND_PERSISTENCE_BEHAVIOR_ACCEPTED
Next gate: MR_F5_HORIZON_SPECIFIC_FUTURE_FORECAST_IMPLEMENTATION

## 1. Starting truth

MR-F4 is accepted and closed.

```text
mr_f4_canonical_application_commit=e4f0d913
mr_f4_closeout_commit=b5d55752
prediction_full_suite=320_passed
operator_ui_full_suite=1184_passed
working_tree=clean
```

The accepted current-state path includes:

```text
family-owned explainable candidate scoring
minimum dwell time
hysteresis
transition penalty
change-point override
invalid-transition guard
persisted state age and start time
canonical transition-policy label ownership
```

MR-F5 must not weaken, bypass, or duplicate this current-state responsibility.

## 2. MR-F5 objective

Build independent future-regime forecasts for:

```text
5m
15m
30m
60m
6h
12h
24h
```

Each forecast must preserve:

```text
origin_current_state
target_horizon
predicted_future_state
transition_path_candidate
raw_model_score_or_probability
calibrated_reliability
invalidation_conditions
feature_snapshot_ref
model_id
logic_version
parameter_set_id
target_definition_version
abstain_reason
```

MR-F5 acceptance requires:

```text
one_horizon_never_borrows_another_label_silently=true
future_labels_preserve_origin_current_state=true
transition_path_explicit=true
invalid_or_missing_evidence_yields_unknown_or_abstain=true
future_outcome_rule_is_horizon_specific=true
```

## 3. Current legacy path

The current classifier selects non-current labels from derived `forecast_records` features.

Relevant behavior:

```text
exact horizon key found:
  use forecast_records label for that exact horizon

forecast records stale and horizon <= 60m:
  bounded current-L4 compatibility fallback may be used

forecast records stale and horizon > 60m:
  UNKNOWN / blocked

missing exact horizon:
  UNKNOWN / missing
```

This path is compatibility input, not the target MR-F5 family-owned forecast model.

Primary files:

```text
btcts_next/src/btcts/prediction/market_regime/inference/regime_classifier.py
btcts_next/src/btcts/prediction/market_regime/sources/forecast_records_reader.py
btcts_next/src/btcts/prediction/market_regime/features.py
btcts_next/src/btcts/prediction/market_regime/horizon_policy.py
btcts_next/src/btcts/prediction/market_regime/evidence_profile.py
btcts_next/src/btcts/prediction/market_regime/source_priority_policy.py
btcts_next/src/btcts/prediction/market_regime/tools/write_latest.py
btcts_next/src/btcts/prediction/market_regime/tools/resolve_outcomes.py
```

## 4. Required first slice

The first slice is `MR-F5.1 horizon-specific future forecast contract and legacy-path audit`.

It must produce:

```text
legacy future-label ownership map
per-horizon source and feature matrix
future forecast result contract
abstention and invalidation contract
transition-path contract
horizon-specific target-definition requirements
replacement boundary for forecast_records compatibility labels
focused pure-contract tests
```

It must not yet:

```text
replace canonical future labels
change MR-F4 current state
write D-hot artifacts
change UI behavior
change displayed confidence
claim calibrated probability
invoke broker or AutoTrade paths
```

## 5. Recommended module boundary

Do not continue growing `inference/regime_classifier.py` with future-model responsibilities.

Preferred direction:

```text
market_regime/future_forecast_contract.py
  immutable result and validation contract

market_regime/future_forecast_policy.py
  horizon grouping and feature emphasis policy

market_regime/future_forecast_baseline.py
  first transparent family-owned forecast candidate

market_regime/inference/regime_classifier.py
  orchestration and compatibility projection only
```

Final names must follow repository conventions after target files are read. Do not create all modules in one slice without a proven responsibility boundary.

## 6. Horizon evidence policy

```text
5m-60m:
  microstructure
  orderflow
  short price structure
  short realized volatility
  liquidity and spread state
  cross-venue agreement

6h-24h:
  broader price structure
  session context
  longer volatility state
  cross-venue context
  macro/context inputs when available
```

Long horizons must abstain when broader evidence is unavailable. They must not reuse a short-horizon label to avoid `UNKNOWN`.

## 7. Target-definition discipline

Before canonical replacement, each horizon requires an explicit target definition covering:

```text
prediction origin timestamp
target evaluation timestamp
observation window
outcome resolver
regime assignment rule
partial-match rule
invalidated outcome rule
missing observation rule
lookahead controls
target_definition_version
```

MR-F1 recorded missing target-definition version as a blocker. MR-F5 must resolve this for new family-owned forecasts rather than copy the gap forward.

## 8. Transition-path discipline

Future transition paths are forecasts, not permission to mutate current persisted state.

```text
origin_current_state=current MR-F4 canonical state
transition_path_candidate=ordered candidate path or explicit direct transition
predicted_future_state=path terminal state
current_state_mutation=false
```

The MR-F4 transition matrix may be consulted as family-owned context, but future paths and current-state persistence must remain separate responsibilities.

## 9. Confidence discipline

MR-F5 may expose a raw score or model probability, but:

```text
calibrated_reliability_maturity=not_accepted
calibrated_probability_claim=false
mr_f7_required_for_calibrated_display=true
```

Existing heuristic confidence and shadow confidence paths remain unchanged during the first MR-F5 slice.

## 10. D-hot inspection policy

Use D-hot only to inspect current forecast-record coverage and representative horizon payloads.

Recommended sequence:

```text
data_glob_summary before broad reads
data_latest for latest prediction candidates
data_slice for bounded JSONL inspection
preserve path, timestamps, counts, limits, and truncated status
```

Forbidden during readiness work:

```text
write_market_regime_latest_artifacts_once
resolve_market_regime_outcomes_once
any writer used merely to create missing evidence
```

## 11. Initial guard plan

Focused contract guards should prove:

```text
all enabled future horizons covered exactly once
current horizon excluded from future forecast contract
horizon mismatch fails closed
missing evidence yields UNKNOWN or abstain
short evidence not accepted for long horizon by default
origin current state preserved
transition path terminal state matches predicted future state
model and target identity fields required
calibrated flag false by default
no runtime reads or writes in pure contract layer
no broker, AutoTrade, or order path
```

Only after these guards pass should the first transparent forecast candidate be designed.

## 12. Stop conditions

Stop and report rather than guessing when:

```text
existing upstream label provenance is ambiguous
target definition cannot be reconstructed safely
horizon-specific features are absent
current and future responsibilities would be mixed
D-hot artifact is missing or truncated beyond the requested bound
contract change would silently break outcome identity
```

## 13. Next-thread startup prompt

```text
BtcTradeSystemの続きをお願いします。project_bootstrapから開始し、
HEAD b5d55752 / MR-F4 accepted / working tree cleanを確認してください。
最初にMR-F5 handoff、roadmap、MR-F4 closeout、POLICY、CURRENT、DECISIONSを読み、
MR-F5.1 horizon-specific future forecast contract and legacy-path auditだけを進めてください。
canonical future label replacement、D-hot writer実行、UI変更はまだ行わないでください。
```
