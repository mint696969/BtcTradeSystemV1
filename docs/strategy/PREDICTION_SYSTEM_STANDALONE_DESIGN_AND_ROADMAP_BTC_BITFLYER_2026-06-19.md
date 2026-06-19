# path: ./docs/strategy/PREDICTION_SYSTEM_STANDALONE_DESIGN_AND_ROADMAP_BTC_BITFLYER_2026-06-19.md
# desc: Standalone Prediction System design and roadmap for BTC / bitFlyer. Separate from AutoTrade until explicit return gate.

# Prediction System Standalone Design and Roadmap

Updated: 2026-06-19 JST  
Profile: BtcTradeSystem  
Status: design / roadmap / non-executing  
Scope: BTC / bitFlyer first, AutoTrade-separated

## 1. Current decision

Prediction System must be treated as a standalone system before returning to the AutoTrade roadmap.

The current workstream is not S138 AutoTrade preview status, Operator UI visibility, mode apply, broker execution, or AutoTrade trigger integration.

Current mainline:

```text
Implement Prediction System itself to a usable level first.
After Prediction System reaches its own completion gate, return to the AutoTrade roadmap explicitly.
```

Hard boundary:

```text
Prediction System predicts and explains.
Prediction System does not trade.
Prediction System does not apply modes.
Prediction System does not append AutoTrade decisions.
Prediction System does not execute Pre-Armed grants.
Prediction System does not call broker/private APIs.
```

## 2. Working definition

Prediction System is a market-reading, hypothesis-building, multi-horizon scenario prediction, invalidation, replay/scoring, and calibration system.

It answers:

```text
What market state are we in?
Is the dominant direction up, down, flat/status-quo, range, or unknown?
What scenario is likely over now / short / mid / long horizons?
What evidence supports the scenario?
What evidence conflicts with the scenario?
What would invalidate the scenario?
When should the prediction be refreshed?
Why did a previous prediction hit or miss?
Which parameter set should be adjusted, kept, or rolled back?
```

Prediction System must be allowed to say:

```text
unknown
no_edge
data_insufficient
too_noisy
conflicting_evidence
wait_for_confirmation
flat
no_change
status_quo
```

A correct no-edge / no-change / cannot-predict output is a successful Prediction System behavior, not a failure.

## 3. Non-goals until explicit return gate

Do not implement in this standalone Prediction System phase:

```text
AutoTrade mode apply
broker execution
real orders
private API calls
AutoTrade decision ledger append
command ledger append
approval ledger append
Pre-Armed grant execution
UI command buttons
watchdog/autonomous execution loop
live_shadow.py behavior modification
append_decision_jsonl integration
S138 AutoTrade preview status continuation
```

WarRoom / Operator UI may later consume Prediction System output, but must not own or recalculate prediction meaning.


## 4. Deployment and folder separation from Collector

Prediction System must be structurally separated from Collector.

Core requirement:

```text
Prediction System and Collector should be movable to separate PCs in the future.
```

This means Prediction System must not depend on Collector internals, Collector runtime process state, or Collector package imports for prediction logic.

Allowed boundary:

```text
Collector produces canonical data artifacts, source status artifacts, and freshness/quality metadata.
Prediction System consumes already-produced artifacts or explicit data contracts.
Prediction System may read configured data roots or compact input snapshots.
Prediction System must not call Collector components as an in-process dependency.
```

Forbidden boundary:

```text
Prediction System core imports btcts.collector_vnext runtime workers
Prediction System starts/stops Collector processes
Prediction System owns public-source collection loops
Prediction System relies on Collector UI state
Prediction System writes Collector runtime state
Prediction System reaches into Collector locks/watchdogs/daemons
```

Folder-structure direction:

```text
btcts_next/src/btcts/prediction/        # standalone Prediction System code
btcts_next/src/btcts/collector_vnext/   # Collector code, separate owner
btcts_next/src/btcts/autotrade/         # AutoTrade code, separate owner
```

Future external deployment direction:

```text
Collector PC:
  collects public/local data
  writes canonical market data and source-quality artifacts
  does not predict or trade

Prediction PC:
  reads canonical artifacts / snapshots / provider-quality summaries
  produces PredictionSystemResult, scenario traces, forecast records, calibration digests
  does not collect, trade, or mutate Collector runtime

AutoTrade PC or process later:
  consumes stable Prediction System outputs only after explicit return gate
  does not scrape public data directly
```

Data exchange must be through stable files, snapshots, or contracts rather than Python runtime coupling.

Candidate artifact boundary:

```text
market_snapshot.json
provider_quality_snapshot.json
feature_snapshot.json
prediction_input_snapshot.json
prediction_system_result.json
scenario_trace_digest.json
forecast_ledger_batch.json
calibration_review_packet.md
```

Design implication:

```text
Prediction System code must remain portable enough to run without Collector installed as an active runtime service, as long as the required input artifacts/contracts are available.
```

Guard implication:

```text
Future Prediction System implementation guards should include no Collector runtime import checks, no collector_vnext worker/daemon/watchdog dependency checks, and no Collector state write checks.
```

## 5. Time-axis model

Prediction System uses concrete horizons and human horizon groups.

### 4.1 Concrete horizons

```text
execution_micro: 15s / 30s / 60s / 180s
primary_trade: 5m / 10m / 15m / 30m
context: 1h / 4h / 1d
```

The existing code already has 15s / 30s / 60s / 180s / 5m / 15m / 30m / 1h / 4h / 1d. 10m should be added or mapped where needed because the Scenario Prediction Core design uses 5m / 10m / 30m.

### 4.2 Human horizon groups

WarRoom and human reports should use provisional display labels:

```text
現在
短期
中期
長期
```

Suggested internal mapping:

| Human label | Internal group | Candidate horizons | Purpose |
|---|---|---|---|
| 現在 | nowcast | now / 15s / 30s / 60s | immediate state, data quality, micro risk |
| 短期 | short_horizon | 5m / 10m / 15m | primary near-term scenario |
| 中期 | mid_horizon | 30m / 1h | scenario continuation / transition |
| 長期 | long_horizon | 4h / 1d | higher context and large-risk background |

### 4.3 Prediction lifetime

Every prediction must have a lifetime.

Required fields:

```text
valid_from
valid_until
stale_after_sec
refresh_required
refresh_reason
```

Short-term volatility or evidence shifts can make mid/long predictions stale even before their normal expiry.

## 6. Public provider / information resource plan

Provider expansion is adopted, but most external/context providers start as warning/context/confidence-modifier inputs, not primary short-horizon direction owners.

### Tier 1: bitFlyer local public data

```text
bitFlyer Spot BTC_JPY board
bitFlyer Spot BTC_JPY trades
bitFlyer Spot BTC_JPY ticker
bitFlyer FX BTC_JPY board
bitFlyer FX BTC_JPY trades
bitFlyer FX BTC_JPY ticker
```

Uses:

```text
Spot-FX basis
local trend
local liquidity
micro pressure
false-break detection
```

### Tier 2: OHLCV / human technical resources

```text
1m / 5m / 10m / 15m / 30m / 1h / 4h / 1d OHLCV
support / resistance
moving averages
VWAP
ATR
wick/body structure
recent high/low
volume
```

### Tier 3: global spot venues

```text
Binance
Coinbase
Kraken
OKX
```

Uses:

```text
global reference price
cross-venue confirmation
lead/lag
divergence
bitFlyer local distortion detection
```

### Tier 4: global derivatives venues

```text
Binance Futures
Bybit
CME BTC futures
funding
open interest
basis
```

Uses:

```text
futures-led moves
squeeze risk
basis dislocation
crowded long/short context
false-break risk
```

### Tier 5: macro / risk context

```text
USD/JPY
DXY proxy
US rates / yields proxy
Nasdaq
S&P 500
Gold
economic calendar
FOMC / CPI / employment events
```

### Tier 6: news / incident context

```text
exchange incidents
regulation headlines
ETF / institutional headlines
sudden liquidity deterioration
system incidents
```

### Tier 7: internal replay / outcome / calibration resources

```text
forecast ledger
outcome ledger
hit / miss
near miss
missed opportunity
weak family
confidence calibration
```

### Adopted additional providers / contexts

```text
Exchange status / incident providers
Session / calendar context
Derivatives liquidation context
Options-derived context
Stablecoin / USD liquidity stress
Funding / carry context
On-chain / mempool stress context
Provider reliability registry
```

Provider reliability registry is mandatory before heavily weighting external sources.

## 7. Source quality and provider reliability

Every provider must have a quality/reliability state before its data is trusted.

Candidate fields:

```text
provider_id
provider_family
source_id
source_family
freshness
latest_event_ts
latest_age_sec
gap_count
missing_window_count
rate_limit_state
outage_state
trust_state
last_success_at
last_error
usable
blockers
warnings
```

Prediction families should consume strong signals only when the provider is usable, fresh, and trusted.

## 8. Prediction families

Prediction System must support 11 prediction families.

| ID | Family | Responsibility | Must not own |
|---:|---|---|---|
| 1 | market_regime | market type / 地合い | final execution decision |
| 2 | trend_bias | up/down/flat/range direction bias | liquidity safety |
| 3 | reversal_zone | likely reaction / reversal zones | global macro direction |
| 4 | volatility_risk | tradability / shock / compression | trend direction alone |
| 5 | liquidity_execution_quality | spread/depth/slippage/book stability | final order placement |
| 6 | breakout_false_break | breakout vs false break | position sizing |
| 7 | opportunity_participation | waiting too much / near miss | execution authorization |
| 8 | cross_venue_confirmation | external confirmation / divergence | local liquidity safety |
| 9 | macro_risk_context | risk-on/off and event caution | short-horizon direction owner |
| 10 | human_technical_structure | human chart structure | source collection |
| 11 | algorithmic_participant_footprint | trap-like / bot-like footprint warning | manipulative behavior |

Each family returns structured output:

```text
family
horizon_sec
horizon_group
primary_label
score
confidence
caution_level
drivers
blockers
warnings
values
evidence_refs
source_quality_notes
parameter_set_id
parameter_set_version
valid_from
valid_until
stale_after_sec
refresh_required
```

## 9. Direction / state vocabulary

Prediction output vocabulary must include at least:

```text
up
long_bias
down
short_bias
flat
range
no_change
status_quo
unknown
no_edge
data_insufficient
too_noisy
conflicting_evidence
wait_for_confirmation
```

For human display, no_change/status_quo should be visible as a real state, not hidden under unknown.

## 10. Scenario Prediction Core

Scenario Prediction Core combines family outputs into horizon-grouped scenarios.

Required outputs:

```text
current_regime_state
current_hypothesis_health
outlook_now
outlook_short
outlook_mid
outlook_long
continuation_vs_reversal_balance
turning_point_risk
invalidation_state
rewrite_state
scenario_switch_hint
evidence_weighting_summary
evidence_conflict_state
scenario_trace
trigger_eligibility_state
human_narrative_ja
gpt_review_digest
```

Scenario Core must explain:

```text
what the current main hypothesis is
why it is trusted or weak
which evidence supports it
which evidence conflicts with it
what would invalidate it
what would trigger a scenario rewrite
what next evidence should be watched
what changed since the previous prediction
```

## 11. Evidence conflict and no-edge handling

Conflicting family outputs must be explicit.

Candidate fields:

```text
evidence_conflict_state
conflicting_families
dominant_family
suppressed_family
conflict_reason
no_edge_reason
wait_for_confirmation_reason
```

Example human narrative:

```text
短期は上方向優勢ですが、反転ゾーン接近と外部市場未確認により追随リスクが高い状態です。
```

## 12. Invalidation / rewrite / switch conditions

Every scenario must include conditions for discarding or rewriting the forecast.

Required fields:

```text
invalidation_condition
rewrite_condition
scenario_switch_condition
what_to_watch_next
```

A prediction without invalidation conditions is not operationally usable.

## 13. Re-prediction and revision tracking

Prediction System must support repeated re-prediction and revision tracking.

Required fields:

```text
prediction_run_id
previous_prediction_run_id
revision_reason
revision_trigger
changed_families
changed_horizons
previous_primary_label
new_primary_label
previous_confidence
new_confidence
previous_invalidation_state
new_invalidation_state
change_summary_for_human
change_summary_for_gpt
```

WarRoom must distinguish:

```text
current prediction
stale prediction
refreshed prediction
superseded prediction
```

## 14. Parameter-set architecture

Parameter sets are a core Prediction System concept.

Rules:

```text
Each prediction family / feature / scenario component uses parameter sets.
Parameter sets are horizon-aware.
Multiple parameter sets may exist per family/component.
Evaluated versions are immutable.
Changes create a new version, not silent mutation.
Versions must be comparable and rollback-capable.
GPT may propose changes.
Human approval is required for activation.
```

Candidate parameter-set metadata:

```text
parameter_set_id
family
component_scope
version
status
created_at
created_by
change_reason
change_hypothesis
expected_improvement
expected_risk
validation_window
rollback_condition
parent_parameter_set_id
rollback_target_id
supported_horizons_sec
horizon_specific_thresholds
horizon_specific_weights
feature_weights
source_weights
risk_thresholds
invalidation_thresholds
scenario_switch_thresholds
confidence_calibration
caution_calibration
human_review_status
human_approved_by
human_approved_at
gpt_review_id
gpt_summary_ref
replay_evaluation_refs
comparison_refs
activation_decision_ref
retirement_decision_ref
```

Parameter activation lifecycle:

```text
draft -> candidate -> shadow -> paper -> active -> retired
```

Rollback must be possible from any active parameter version.

## 15. Evaluation / comparison / calibration

Parameter sets and predictions must be evaluated by:

```text
family
horizon
horizon_group
market_regime
time window
source quality state
session / calendar state
provider set
```

Required comparison metrics:

```text
forecast_count
scored_count
hit_rate
direction_hit_rate
flat/no_change_hit_rate
average_score
false_positive_count
false_negative_count
near_miss_count
missed_opportunity_count
blocked_too_much_count
overconfidence_count
underconfidence_count
weak_evidence_cases
source_quality_impact
late_reprediction_needed_count
```

全体 hit rate だけで評価してはいけない。trend / range / volatile / transition / low_liquidity / event_window / weekend / high_basis / cross_venue_divergent などの相場タイプ別評価が必要。

## 16. Hit/miss explanation

Outcome scoring must explain why a prediction hit or missed.

Candidate fields:

```text
outcome_explanation_state
hit_reason_candidates
miss_reason_candidates
dominant_success_evidence
dominant_failure_evidence
source_quality_impact
parameter_set_impact
evidence_conflict_impact
late_reprediction_needed
missed_refresh_signal
notes_for_human
notes_for_gpt
```

Hit reasons are as important as miss reasons because they reveal which evidence and parameter sets worked.

## 17. GPT-readable summaries and future 7B AI connection

Initial implementation is logic-first / deterministic-first.

Architecture must remain AI-connectable for a future 7B-class dedicated AI.

AI roles later:

```text
scenario explanation support
evidence contradiction detection
miss reason analysis
weak-family / weak-horizon diagnosis
parameter adjustment proposal
alternate scenario proposal
overconfidence warning
data/source quality caution explanation
compact daily/weekly review summary generation
```

AI must not become execution owner and must not silently mutate live parameters.

GPT-readable artifacts should be compact, structured, bounded, and source-linked:

```text
prediction_run_summary.json
scenario_trace_digest.json
family_horizon_score_digest.json
weak_family_report.md
parameter_comparison_digest.md
source_quality_digest.json
miss_reason_digest.md
near_miss_digest.md
calibration_review_packet.md
gpt_parameter_adjustment_proposal.md
human_parameter_review_record.md
```

## 18. Data roots and artifact policy

Current operational distinction:

```text
D:\btc_ts_hot = hot/latest/live runtime artifacts, latest state/logs, Collector/UI live data
E:\btc_ts = cold/archive/copy/long-term retention validation
```

Design direction:

```text
Latest compact GPT-readable review artifacts should live under the hot/latest side when available.
Archive/comparison history can live under cold/archive side as appropriate.
Raw/full data must remain separate from compact GPT digests.
```

GPT should inspect summaries and references freely enough to propose parameter adjustments, while large raw artifacts remain bounded by digest/index layers.

## 19. Human-visible WarRoom consumption requirement

WarRoom should eventually display clear Prediction System output at the top of the tab.

Top-level cards:

```text
現在
短期
中期
長期
```

Each card shows:

```text
地合い
トレンド
反転リスク
ブレイク / だましリスク
ボラ / 危険度
confidence
caution / warning
scenario switch / invalidation warning
```

Clicking a card should open detail:

```text
primary label
score / confidence
drivers
blockers
warnings
source quality notes
feature/evidence refs
scenario trace
invalidation condition
what to watch next
parameter_set_id / version
```

Below the cards, WarRoom should show Japanese scenario narratives:

```text
現在の予測シナリオ
短期の予測シナリオ
中期の予測シナリオ
長期の予測シナリオ
```

Perspective switching should be supported where feasible:

```text
分足
時足
日足
```

WarRoom is a consumer only. It must not invent or recalculate prediction meaning.

## 20. Future AutoTrade trigger boundary

Prediction output may later become an AutoTrade trigger/input source only after the standalone Prediction System completion gate and an explicit AutoTrade return gate.

Trigger consumption must use stable machine-readable fields, not Japanese UI text.

Candidate future trigger fields:

```text
horizon_group
regime_state
trend_bias
reversal_risk
breakout_false_break_risk
volatility_risk
liquidity_execution_quality
confidence
caution_level
invalidation_state
scenario_switch_hint
parameter_set_id
source_quality_state
trigger_eligibility_state
confirmation_count
minimum_persistence_sec
horizon_alignment_required
cooldown_after_switch
do_not_trigger_during_conflict
```

Prediction and trigger eligibility are separate:

```text
prediction = market view
trigger_eligibility = whether the view is reliable/safe enough to become an AutoTrade input later
```

## 21. Roadmap overview

The roadmap uses PS-prefixed standalone phases. AutoTrade phases are not resumed until PS completion gate.

```text
PS-A design and roadmap closure
PS-B current code inventory and gap index
PS-C standalone contracts and result shape
PS-D source quality and provider reliability foundation
PS-E feature layer expansion
PS-F 11-family rule-based v1
PS-G multi-horizon orchestration
PS-H Scenario Core integration
PS-I re-prediction / expiry / revision tracking
PS-J forecast / outcome / hit-miss explanation
PS-K parameter-set versioning / comparison / rollback
PS-L GPT-readable digest and human review packets
PS-M WarRoom/AutoTrade consumption contract design, no integration
PS-N standalone completion gate and AutoTrade return gate
```

## 22. Detailed checkpoints

### PS-A: Design and roadmap closure

Goal: close this standalone design and roadmap.

Checkpoints:

```text
PS-A1: standalone scope documented
PS-A2: AutoTrade non-goals documented
PS-A3: horizons and horizon groups documented
PS-A4: 11 families documented
PS-A5: provider/resource plan documented
PS-A6: parameter-set requirements documented
PS-A7: GPT/AI future requirements documented
PS-A8: WarRoom/trigger future boundary documented
PS-A9: Collector / Prediction folder and deployment separation documented
```

Exit criteria:

```text
design document exists
guard confirms required sections
no code behavior change
no AutoTrade runtime integration
```

### PS-B: Current code inventory and gap index

Goal: record what exists now and what is missing.

Checkpoints:

```text
PS-B1: btcts.prediction module inventory
PS-B2: existing contracts inventory
PS-B3: existing feature helpers inventory
PS-B4: existing rule_based_v0 family coverage index
PS-B5: missing 6-family logic index
PS-B6: missing orchestrator index
PS-B7: missing multi-horizon behavior index
PS-B8: missing parameter-set lifecycle index
PS-B9: Collector import/dependency gap check
```

Exit criteria:

```text
gap index document exists
implementation order remains Prediction System only
```

### PS-C: Standalone contracts and result shape

Goal: create the top-level Prediction System API shape.

Candidate files:

```text
btcts_next/src/btcts/prediction/system_contract.py
btcts_next/src/btcts/prediction/system.py
```

Checkpoints:

```text
PS-C1: PredictionSystemInput
PS-C2: PredictionSystemResult
PS-C3: HorizonGroupSummary
PS-C4: ScenarioCoreOutput
PS-C5: PredictionRunIdentity
PS-C6: machine-readable trigger-eligible fields but no AutoTrade dependency
PS-C7: human_narrative_ja field
PS-C8: gpt_review_digest field
PS-C9: to_dict serialization
PS-C10: no Collector runtime import dependency
```

Exit criteria:

```text
contracts serialize
no btcts.autotrade import
no btcts.collector_vnext runtime import
no broker/mode/append/grant fields except false safety flags
```

### PS-D: Source quality and provider reliability foundation

Goal: ensure every provider has freshness/trust/outage/gap visibility.

Checkpoints:

```text
PS-D1: ProviderReliabilityStatus contract
PS-D2: ProviderRegistry contract
PS-D3: source quality aggregation by provider family
PS-D4: bitFlyer provider entries
PS-D5: global spot provider entries
PS-D6: derivatives provider entries
PS-D7: macro/calendar/news/status provider entries as context/warning
PS-D8: provider reliability digest for GPT
```

Exit criteria:

```text
prediction families can receive provider quality summary
unusable providers produce blockers/warnings, not silent trust
```

### PS-E: Feature layer expansion

Goal: provide minimum deterministic features needed by all 11 families.

Checkpoints:

```text
PS-E1: OHLCV 10m support or mapping
PS-E2: orderbook pressure feature contract
PS-E3: liquidity execution quality feature contract
PS-E4: tradeflow dynamics feature contract
PS-E5: breakout / retest feature contract
PS-E6: opportunity / near-miss feature contract
PS-E7: macro context feature contract
PS-E8: session/calendar feature contract
PS-E9: algorithmic footprint feature contract
PS-E10: feature digest for GPT
```

Exit criteria:

```text
all 11 families have minimum input features or explicit blockers
missing data is visible and bounded
```

### PS-F: 11-family rule-based v1

Goal: implement all 11 families as deterministic v1 outputs.

Checkpoints:

```text
PS-F1: market_regime v1
PS-F2: trend_bias v1 with up/down/flat/range/no_edge
PS-F3: reversal_zone v1
PS-F4: volatility_risk v1
PS-F5: liquidity_execution_quality v1
PS-F6: breakout_false_break v1
PS-F7: opportunity_participation v1
PS-F8: cross_venue_confirmation v1
PS-F9: macro_risk_context v1 warning/context first
PS-F10: human_technical_structure v1
PS-F11: algorithmic_participant_footprint v1 warning/context first
PS-F12: all families expose drivers/blockers/warnings/evidence_refs/parameter_set_id
```

Exit criteria:

```text
all 11 families emit PredictionOutput-compatible records
no family owns execution decisions
```

### PS-G: Multi-horizon orchestration

Goal: run all selected families over all selected horizons.

Checkpoints:

```text
PS-G1: build_prediction_outputs_for_horizons
PS-G2: horizon group mapping now/short/mid/long
PS-G3: per-horizon parameter selection
PS-G4: horizon-specific confidence/caution
PS-G5: horizon summary aggregation
PS-G6: flat/no_change/no_edge behavior across horizons
```

Exit criteria:

```text
Prediction System can produce now/short/mid/long summaries in one run
```

### PS-H: Scenario Core integration

Goal: combine family outputs into operational scenarios.

Checkpoints:

```text
PS-H1: evidence weighting summary
PS-H2: evidence conflict state
PS-H3: current_regime_state
PS-H4: current_hypothesis_health
PS-H5: continuation vs reversal balance
PS-H6: invalidation condition
PS-H7: rewrite condition
PS-H8: scenario switch hint
PS-H9: Japanese scenario narrative per horizon group
PS-H10: GPT review digest
```

Exit criteria:

```text
Scenario Core explains conclusion, evidence, conflict, invalidation, and next watch items
```

### PS-I: Re-prediction / expiry / revision tracking

Goal: predictions are refreshable, not static.

Checkpoints:

```text
PS-I1: valid_from / valid_until / stale_after_sec
PS-I2: refresh_required and refresh_reason
PS-I3: previous_prediction_run_id
PS-I4: revision reason and trigger
PS-I5: changed family/horizon tracking
PS-I6: mid/long refresh caused by short-term volatility
PS-I7: stale/refreshed/superseded states
```

Exit criteria:

```text
new runs can explain what changed since previous run
```

### PS-J: Forecast / outcome / hit-miss explanation

Goal: evaluate predictions and explain outcomes.

Checkpoints:

```text
PS-J1: forecast record includes prediction_run_id and parameter_set_id
PS-J2: outcome record includes realized up/down/flat/no_change/range states
PS-J3: hit/miss scoring by family/horizon/regime
PS-J4: hit reason candidates
PS-J5: miss reason candidates
PS-J6: late refresh / missed refresh signal detection
PS-J7: family-horizon score digest
PS-J8: miss reason digest for GPT
```

Exit criteria:

```text
Prediction System can say not only hit/miss, but why it likely hit/missed
```

### PS-K: Parameter-set versioning / comparison / rollback

Goal: make tuning safe and reviewable.

Checkpoints:

```text
PS-K1: horizon-aware parameter-set contract
PS-K2: parameter-set registry
PS-K3: immutable evaluated versions
PS-K4: parent/rollback target references
PS-K5: change_hypothesis / expected_improvement / expected_risk
PS-K6: validation_window / rollback_condition
PS-K7: comparison records by family/horizon/regime
PS-K8: GPT proposal packet
PS-K9: human review record
PS-K10: activation gate, no silent mutation
```

Exit criteria:

```text
human + GPT can compare parameter versions and safely propose/approve changes
```

### PS-L: GPT-readable digest and review packets

Goal: give GPT compact, bounded material for analysis.

Checkpoints:

```text
PS-L1: prediction_run_summary.json shape
PS-L2: scenario_trace_digest.json shape
PS-L3: weak_family_report.md shape
PS-L4: parameter_comparison_digest.md shape
PS-L5: source_quality_digest.json shape
PS-L6: calibration_review_packet.md shape
PS-L7: digest size and reference policy
PS-L8: hot/cold data-root placement policy
```

Exit criteria:

```text
GPT can inspect summaries without huge raw dumps and propose parameter adjustments
```

### PS-M: WarRoom / AutoTrade consumption contract design only

Goal: define how consumers will read Prediction System output later.

Checkpoints:

```text
PS-M1: WarRoom top-card contract
PS-M2: card detail popup contract
PS-M3: Japanese scenario narrative contract
PS-M4: 分足/時足/日足 switching contract
PS-M5: machine trigger field contract
PS-M6: trigger_eligibility separated from prediction
PS-M7: no WarRoom recalculation rule
PS-M8: no AutoTrade integration yet
```

Exit criteria:

```text
consumer contract is designed but not wired into AutoTrade runtime
```

### PS-N: Standalone completion gate and AutoTrade return gate

Goal: decide when Prediction System is ready enough to return to AutoTrade roadmap.

Completion checks:

```text
PS-N1: all 11 families implemented
PS-N2: now/short/mid/long multi-horizon output works
PS-N3: Scenario Core produces evidence/conflict/invalidation/switch/narrative
PS-N4: re-prediction and revision tracking works
PS-N5: hit/miss explanation works
PS-N6: parameter-set comparison and rollback design works
PS-N7: GPT-readable digest exists
PS-N8: no AutoTrade dependency in Prediction System core
PS-N9: no broker/mode/append/grant behavior
PS-N10: AutoTrade return gate document created
```

Only after PS-N should AutoTrade roadmap resume.

## 23. Initial implementation order

Recommended first code slices after this document:

```text
PS-B: current code inventory and gap index
PS-C1: PredictionSystemInput / PredictionSystemResult contracts
PS-C2: HorizonGroupSummary and ScenarioCoreOutput skeleton
PS-G1: multi-horizon output runner over existing 5 families
PS-F remaining families v1, one or two families per slice
PS-H Scenario Core richer integration
PS-I re-prediction / expiry
PS-J outcome explanation
PS-K parameter-set lifecycle
```

Reasoning:

```text
First create the top-level shape.
Then make existing logic run through that shape.
Then fill missing families.
Then strengthen scenario, replay, parameter tuning, and display contracts.
```

## 24. Guard policy

Each implementation slice must have focused guards.

Guard categories:

```text
serialization guard
no AutoTrade import guard
no Collector runtime import guard
no broker/private API guard
no append/mode/grant guard
family coverage guard
horizon coverage guard
parameter-set metadata guard
GPT digest bounded-shape guard
scenario trace guard
outcome explanation guard
```

## 25. Final standalone design principle

Prediction System must be:

```text
logic-first now
AI-connectable later
multi-horizon from the beginning
provider-quality-aware from the beginning
parameter-set-versioned from the beginning
GPT-reviewable from the beginning
human-approved for activation
replay/comparison-driven for tuning
rollback-capable for every active parameter change
human-visible through clear narratives later
machine-readable for future AutoTrade trigger consumption later
separate from Collector runtime and AutoTrade until explicit return gate
```
