# path: ./docs/strategy/PREDICTION_SYSTEM_INFERENCE_FORMAL_SPEC_BTC_BITFLYER_2026-06-20.md
# desc: Formal inference specification for the standalone BTC / bitFlyer Prediction System goal, WarRoom observability, and future AutoTrade trigger-candidate readiness.

# Prediction System Inference Formal Spec

Updated: 2026-06-20 JST
Profile: BtcTradeSystem
Status: canonical inference goal / implementation guardrail
Scope: BTC / bitFlyer first, standalone Prediction System, non-executing

## 1. Canonical final goal

The formal goal of the Prediction System roadmap is not only Scenario Core entry, evaluation, calibration, or UI display.

The final goal is:

```text
Complete a standalone inference system whose predictions can be observed and understood by a human in WarRoom, and whose structured outputs are granular, reliable, and safe enough to become future AutoTrade trigger candidates after a separate explicit return gate.
```

The system must provide both:

```text
1. Human-readable WarRoom prediction review:
   prediction, evidence, confidence, caution, invalidation, what-to-watch, Japanese scenario narrative, and an operator-readable reference strength percentage.

2. Machine-readable trigger-candidate output:
   stable structured fields that AutoTrade may later consume only after explicit human-reviewed return gate approval.
```

## 2. Core philosophy: inference, not prophecy

Prediction System must never be treated as prophecy, fortune-telling, clairvoyance, or a system expected to predict the future with 100% accuracy.

Prediction System is an original market inference / decision-support indicator. It produces forecasts, assumptions, and hypotheses derived from:

```text
past and current liquidity
orderbook and tradeflow behavior
available market data and numerical states
human technical indicators and market-reading concepts
source quality and provider reliability
AI-like and professional participant likely behavior
current regime, volatility, risk, and event context
replay/outcome/calibration feedback
```

The intended output is:

```text
an evidence-based forecast / inference / hypothesis that can be used as one proprietary reference indicator for trading decisions.
```

The intended output is not:

```text
a guaranteed future result
a 100% hit-rate promise
a command to place an order
a replacement for risk gates, human review, or AutoTrade safety boundaries
```

A correct no-edge / no-change / cannot-predict output is a successful inference result, not a failure.

This philosophy is mandatory. Future implementation must not optimize toward fake certainty, hidden overconfidence, or UI wording that implies prophecy.

## 3. WarRoom reference hit-rate / signal strength display

WarRoom signal cards must display an operator-readable percentage derived from the information used for inference.

Canonical field names:

```text
estimated_signal_strength_percent
estimated_reference_hit_rate_percent
```

Meaning:

```text
This percentage is a reference inference strength / hopeful estimated hit-rate based on available evidence, not a guaranteed probability and not a promise of future outcome.
```

Range rule:

```text
0% = prediction unavailable / cannot infer / data insufficient / too noisy / fully conflicting evidence
1% - 99% = reference inference strength based on evidence
99% = maximum display value
100% = forbidden; never display or store 100 as a prediction strength
```

Display and calibration rules:

```text
Do not use 0% as a normal weak prediction. Use 0% only when the system truly cannot infer.
Do not force most predictions into very low percentages if evidence is usable and coherent.
Allow moderate and strong percentages when evidence, source quality, family agreement, and replay/calibration context support them.
Show the percentage together with label, confidence, caution, blockers, source quality warnings, and invalidation state.
The percentage must be bounded by source quality, evidence conflict, freshness, and caution.
The percentage must be recalibratable by replay/outcome review, but production changes require explicit design and human review.
```

Recommended display bands:

```text
0%      = 予測不能
1-24%   = very weak / 参考度かなり低い
25-49%  = weak / 参考度低い
50-69%  = moderate / 参考になる
70-84%  = strong / 強めに参考
85-94%  = very strong / かなり強い参考
95-99%  = exceptional / 最大級だが絶対ではない
```

WarRoom wording should make clear that this is a proprietary reference indicator, not certainty.

## 3.1 Probability-improvement principle

Prediction System is intended to improve decision odds compared with blind or random direction selection.

Example interpretation:

```text
Choosing long/short without inference is like blindly choosing red/black.
Using Prediction System output should provide a better reference by reading liquidity, market data, human technical indicators, source quality, current context, likely AI/pro participant behavior, and replay/calibration feedback.
```

This does not mean guaranteed correctness. It means:

```text
the system should continuously improve the odds of a useful trading reference signal
by measuring misses, weak evidence, overconfidence, underconfidence, source-quality issues, and horizon/regime-specific behavior.
```

Therefore the system must include adjustable mechanisms for improving correct-reference probability over time:

```text
versioned parameter sets
signal-strength calibration
family/horizon/regime evaluation
hit/miss reason analysis
source contribution analysis
overconfidence and underconfidence review
human-approved parameter adjustment
replay/shadow comparison before activation
rollback-capable active parameter versions
```

The target is not 100% accuracy. The target is a tunable, reviewable, evidence-based inference indicator that can raise the probability of making a better-informed real-money trading decision.


## 4. Mandatory non-compression rule

Future GPT must not reduce the roadmap to any of the following smaller goals:

```text
Scenario Core skeleton only
evaluation/calibration only
WarRoom UI only
AutoTrade trigger integration only
PredictionSummary display only
Operation B completion only
```

Each is at most a sub-goal. The formal target is the complete inference system described in this spec.

## 5. System identity and boundaries

Prediction System is a standalone market-reading, hypothesis-building, multi-horizon scenario prediction, invalidation, replay/scoring, and calibration system.

It must answer:

```text
What market state are we in?
What is the dominant direction or no-edge/no-change state?
What scenario is likely over now / short / mid / long horizons?
What evidence supports the scenario?
What evidence conflicts with the scenario?
What would invalidate or rewrite the scenario?
When should the prediction be refreshed?
Why did a previous prediction hit or miss?
Which parameter set should be kept, adjusted, reviewed, or rolled back?
```

Hard boundaries:

```text
Prediction System does not trade.
Prediction System does not call broker/private APIs.
Prediction System does not append AutoTrade decision or command ledgers.
Prediction System does not apply modes or grants.
Prediction System does not own Collector runtime loops.
WarRoom displays Prediction System output and must not recalculate prediction meaning.
AutoTrade may consume outputs only after explicit return gate.
```

## 6. Required source / artifact coverage

Prediction System must implement or explicitly contract input coverage for:

```text
bitFlyer Spot ticker
bitFlyer FX ticker
bitFlyer trades
bitFlyer board / orderbook-derived summaries
OHLCV horizons: 1m / 5m / 10m / 15m / 30m / 1h / 4h / 1d
global spot venue references
global derivatives context
funding context
basis context
liquidation context
macro context
session/calendar context
exchange incident/status context
news/event context
provider/source reliability state for every non-local source
internal replay / outcome / calibration artifacts
```

Data acquisition boundary:

```text
Collector or provider artifact producers own collection.
Prediction System consumes already-produced artifacts, explicit snapshots, source-quality summaries, or portable input contracts.
Prediction core must not import Collector runtime workers, daemons, watchdogs, process controls, or UI state.
```

## 7. Required provider/source quality gate

Every source must have an explicit quality state before it can strongly affect prediction.

Required fields or equivalent:

```text
provider_id
source_id
source_family
freshness
latest_event_ts
latest_age_sec
missing_window_count
gap_count
rate_limit_state
outage_state
trust_state
usable_state
blockers
warnings
per-source contribution visibility
```

Rule:

```text
Unusable, stale, missing, or untrusted sources may contribute warnings, but must not silently raise confidence, estimated signal strength, or trigger eligibility.
```

## 7.1 Evidence hierarchy and conflict resolution

Prediction System must not treat all information sources as equal.

As source coverage grows, long-biased, short-biased, flat/no-edge, and caution signals will often appear at the same time. The system must therefore use an explicit evidence hierarchy, source-quality gate, and conflict-resolution model before producing a final scenario or signal-strength percentage.

Core principle:

```text
Start from high-trust/base evidence.
Use lower-tier evidence as confirmation, caution, context, or cap modifiers.
Do not let weak or stale lower-tier context override strong fresh base evidence.
When all required high-quality tiers align in the same direction, signal strength may approach 99%.
When tiers conflict, lower the signal strength, expose the conflict, or return wait_for_confirmation / no_edge.
```

Initial evidence hierarchy:

```text
Tier 0: source quality / freshness / integrity gate
  Role: veto, cap, or block inference. Not a direction owner.
  Examples: stale data, outage, missing windows, rate limit, provider trust, clock gaps.

Tier 1: local executable-market truth
  Role: highest-priority short-horizon market evidence.
  Examples: bitFlyer Spot/FX ticker, trades, board/orderbook summaries, spread/depth, local liquidity, local tradeflow.

Tier 2: multi-timeframe price/technical structure
  Role: primary human-readable market structure and horizon context.
  Examples: OHLCV, support/resistance, moving averages, VWAP, ATR, wick/body, recent highs/lows, volume.

Tier 3: cross-venue spot confirmation
  Role: confirmation or divergence check against local bitFlyer behavior.
  Examples: Binance, Coinbase, Kraken, OKX spot reference, lead/lag, cross-venue divergence.

Tier 4: derivatives and leverage context
  Role: squeeze, crowded positioning, basis/funding/liquidation risk modifier.
  Examples: futures, funding, basis, open interest, liquidation, CME context.

Tier 5: macro / session / calendar / incident / news context
  Role: risk/caution/cap modifier and event-context provider. Usually not a short-horizon direction owner alone.
  Examples: USD/JPY, DXY proxy, equities, rates proxy, session, economic calendar, exchange incident/status, news/event.

Tier 6: AI/pro participant behavior hypothesis
  Role: derived hypothesis about likely professional, algorithmic, or AI-assisted participant behavior.
  Examples: likely stop-run, false-break participation, liquidity hunting, absorption, crowding, wait-for-confirmation behavior.

Tier 7: replay / outcome / calibration prior
  Role: confidence, signal-strength, and parameter adjustment modifier based on historical performance. Not a live market direction owner by itself.
```

Required conflict-resolution fields:

```text
evidence_hierarchy_version
evidence_alignment_state
dominant_evidence_tier
dominant_evidence_family
supporting_evidence_tiers
conflicting_evidence_tiers
suppressed_evidence_tiers
direction_vote_ledger
source_contribution_ledger
signal_strength_cap_reason
conflict_resolution_reason
wait_for_confirmation_reason
```

Direction and signal-strength rules:

```text
If Tier 0 blocks or caps inference, signal strength must be capped or 0% when inference is unavailable.
If Tier 1 and Tier 2 are fresh, trusted, and aligned, the system may produce a usable directional signal.
If Tier 1 and Tier 2 conflict, do not let lower tiers force a high-confidence direction; prefer lower strength, caution, wait_for_confirmation, or no_edge.
If Tier 1-4 align and Tier 5 has no major caution, signal strength may become strong.
If all required fresh/trusted tiers align and replay/calibration does not object, signal strength may approach 95-99%.
99% is allowed only for exceptional multi-tier alignment with no serious source-quality blockers, but it is still not certainty.
100% remains forbidden.
If lower-tier context conflicts with high-tier evidence, expose it as warning/cap rather than silently flipping direction.
```

WarRoom must show why the final percentage was assigned, including:

```text
which tiers supported the signal
which tiers conflicted
which tiers were missing/stale
which tier dominated the decision
why signal strength was capped or raised
what information would change the scenario
```


## 7.2 Extensible reference-source registry

Prediction System must be extensible because future useful reference information is not fully knowable today.

New sources may be added only through an explicit source registry / input contract. Do not add ad-hoc fields that bypass source quality, evidence hierarchy, or conflict resolution.

Every new reference source must declare:

```text
source_id
provider_id
source_family
evidence_tier
owner_system
artifact_contract
freshness_policy
quality_policy
direction_ownership: none / supporting / primary_candidate
allowed_effects: confirm / warn / cap / veto / strengthen / weaken / context_only
default_weight
maximum_weight
minimum_required_quality
missing_behavior
stale_behavior
conflict_behavior
warroom_display_label_ja
machine_reason_codes
```

Extensibility rules:

```text
New sources must start conservative until evaluated.
New sources must not bypass Tier 0 source-quality gate.
New sources must not become primary direction owners without human-reviewed design.
New sources must define how they affect signal strength: raise, cap, warn, veto, or context-only.
New sources must expose their contribution in source_contribution_ledger.
New sources must support replay/shadow evaluation before active weighting.
New sources must be removable or weight-reducible without breaking the result schema.
```

This design allows more weapons to be added later without confusing the inference core.

## 7.3 Context-specific evidence profiles

Source reliability, evidence priority, and useful weighting must not be treated as one global value.

Different prediction cards, families, and time horizons need different optimal information sources. A source that is strong for one prediction context can be weak, delayed, or only cautionary for another.

Required principle:

```text
Evidence hierarchy defines the global default order.
Context-specific evidence profiles define how that hierarchy is applied for each prediction target.
```

Each prediction target must be able to select or declare an evidence profile by:

```text
prediction_card: market_regime / trend_bias / reversal_risk / breakout_false_break / volatility_risk / liquidity_execution_quality / macro_context / trigger_candidate
prediction_family
horizon_group: nowcast / short_horizon / mid_horizon / long_horizon
concrete_horizon
market_regime_state
session_context
risk_context
```

Every context-specific evidence profile must declare:

```text
evidence_profile_id
evidence_profile_version
applies_to_cards
applies_to_families
applies_to_horizon_groups
primary_evidence_tiers
secondary_evidence_tiers
caution_only_tiers
cap_only_tiers
veto_tiers
context_weight_overrides
minimum_required_sources
minimum_required_tiers
missing_source_behavior
conflict_resolution_policy
signal_strength_floor
signal_strength_ceiling
warroom_explanation_template_id
```

Examples:

```text
Trend / short_horizon:
  primary: Tier 1 local executable-market truth + Tier 2 multi-timeframe technical structure
  confirmation: Tier 3 cross-venue spot
  caution/cap: Tier 4 derivatives, Tier 5 macro/news

Reversal risk / nowcast-short_horizon:
  primary: Tier 1 orderbook/tradeflow + Tier 2 wick/ATR/support-resistance
  confirmation: Tier 4 liquidation/funding/crowding
  caution: Tier 3 cross-venue divergence

Macro context / long_horizon:
  primary: Tier 5 macro/session/calendar/news + Tier 2 higher timeframe structure
  confirmation: Tier 3 global spot and Tier 4 derivatives
  caution: Tier 1 local microstructure should not dominate alone

Liquidity execution quality / nowcast:
  primary: Tier 1 board/spread/depth/trades
  caution: Tier 0 freshness/integrity
  context: Tier 3/4 only as secondary confirmation or risk modifiers
```

Signal-strength rules:

```text
A global source trust score may be used as a base prior only.
The final contribution must be computed per prediction context.
A source may raise trend confidence but only cap reversal confidence, or vice versa.
A source may be primary for nowcast but context-only for long_horizon.
A source may be strong for risk/caution but weak for directional ownership.
```

WarRoom must expose the selected profile:

```text
evidence_profile_id
evidence_profile_version
why this profile was selected
which sources were primary for this card/horizon
which sources were secondary/caution/cap/veto
which expected sources were missing or stale
how the profile affected estimated_signal_strength_percent
```

This prevents “too many weapons” from confusing the inference core while preserving future extensibility.


## 8. Required prediction families

Prediction System must support 11 families:

```text
market_regime
trend_bias
reversal_zone
volatility_risk
liquidity_execution_quality
breakout_false_break
opportunity_participation
cross_venue_confirmation
macro_risk_context
human_technical_structure
algorithmic_participant_footprint
```

Each family output must be horizon-aware and include at least:

```text
family
horizon_sec
horizon_group
primary_label
score
confidence
estimated_signal_strength_percent
caution_level
drivers
blockers
warnings
values
evidence_refs
source_quality_notes
evidence_hierarchy_version
dominant_evidence_tier
supporting_evidence_tiers
conflicting_evidence_tiers
source_contribution_ledger
source_registry_version
reference_source_registry_ids
evidence_profile_id
evidence_profile_version
context_weight_overrides
parameter_set_id
parameter_set_version
valid_from
valid_until
stale_after_sec
refresh_required
refresh_reason
```

## 9. Horizon model

Concrete horizons:

```text
execution_micro: 15s / 30s / 60s / 180s
primary_trade: 5m / 10m / 15m / 30m
context: 1h / 4h / 1d
```

Human horizon groups:

```text
現在 = nowcast / immediate state / micro risk
短期 = short_horizon / primary trade scenario
中期 = mid_horizon / continuation or transition context
長期 = long_horizon / higher-timeframe background and large-risk context
```

WarRoom perspective switching should support, where feasible:

```text
分足
時足
日足
```

## 10. Scenario Prediction Core requirements

Scenario Core must combine family outputs into horizon-grouped scenario outputs.

Required scenario fields:

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
evidence_alignment_state
dominant_evidence_tier
supporting_evidence_tiers
conflicting_evidence_tiers
conflicting_families
dominant_family
suppressed_family
what_to_watch_next
refresh_required
refresh_reason
previous_prediction_diff
revision_explanation
estimated_signal_strength_percent
estimated_reference_hit_rate_percent
trigger_eligibility_state
human_narrative_ja
gpt_review_digest
```

The core must explicitly handle:

```text
up / long_bias
down / short_bias
flat / range / no_change / status_quo
unknown / no_edge / data_insufficient / too_noisy / conflicting_evidence / wait_for_confirmation
```

## 11. Invalidation, rewrite, and revision tracking

Every prediction must include lifetime and revision state.

Required fields:

```text
prediction_run_id
previous_prediction_run_id
valid_from
valid_until
stale_after_sec
refresh_required
refresh_reason
revision_reason
revision_trigger
changed_families
changed_horizons
previous_primary_label
new_primary_label
previous_confidence
new_confidence
previous_estimated_signal_strength_percent
new_estimated_signal_strength_percent
previous_invalidation_state
new_invalidation_state
change_summary_for_human
change_summary_for_gpt
```

A prediction without invalidation or refresh conditions is not operationally usable.

## 12. WarRoom observability requirements

WarRoom must consume and display Prediction System outputs as read-only packets.

Top-level cards:

```text
現在
短期
中期
長期
```

Each card should display:

```text
地合い
トレンド / no-change / no-edge state
推論強度 / 参考的中率 percentage, 0-99 only
反転リスク
ブレイク / だましリスク
ボラ / 危険度
confidence
caution / warning
source quality warning
scenario switch / invalidation warning
refresh/stale state
```

Each card should have a detail view showing:

```text
primary label
score / confidence
estimated_signal_strength_percent
estimated_reference_hit_rate_percent
why this percentage was assigned
evidence profile id/version
why this profile was selected
dominant evidence tier
supporting / conflicting tiers
signal strength cap reason
drivers
blockers
warnings
source quality notes
feature/evidence refs
scenario trace
invalidation condition
rewrite condition
what to watch next
parameter_set_id / version
latest evaluation/calibration status
```

Japanese narrative sections:

```text
現在の予測シナリオ
短期の予測シナリオ
中期の予測シナリオ
長期の予測シナリオ
```

Each narrative must explain:

```text
現在の地合い
優勢方向または no-edge/no-change 理由
推論強度 / 参考的中率の理由
継続条件
反転条件
警戒ポイント
根拠
予測が外れる条件
次に見るべき材料
```

WarRoom must not create its own prediction logic. It renders Prediction System result, evidence, trace, percentage, and narrative.

## 13. AutoTrade trigger-candidate readiness

Trigger-candidate readiness is a future contract, not current enablement.

Required machine-readable fields:

```text
horizon_group
regime_state
trend_bias
reversal_risk
breakout_false_break_risk
volatility_risk
liquidity_execution_quality
confidence
estimated_signal_strength_percent
estimated_reference_hit_rate_percent
caution_level
invalidation_state
scenario_switch_hint
parameter_set_id
parameter_set_version
source_quality_state
trigger_eligibility_state
trigger_blockers
trigger_warnings
trigger_reason_codes
```

Default rule:

```text
trigger_eligibility_state remains blocked by default until explicit human-reviewed AutoTrade return gate.
```

Required before any AutoTrade integration:

```text
exact trigger semantics documented
safety and rollback plan documented
guard coverage documented
no-live-trading gate documented
failure/blocker behavior documented
human approval recorded
broker/private API boundary remains closed until a separate approved phase
```

## 14. Evaluation, replay, calibration, and learning loop

Prediction System must support offline/replay evaluation before production calibration changes.

Required evaluation dimensions:

```text
family
horizon
horizon_group
market_regime
time window
source quality state
session/calendar state
provider set
parameter_set_id
estimated_signal_strength_percent bucket
```

Required review outputs:

```text
hit/miss/partial/not_evaluable
hit reason candidates
miss reason candidates
dominant success evidence
dominant failure evidence
source quality impact
parameter set impact
evidence conflict impact
late refresh needed
missed refresh signal
signal strength overconfidence / underconfidence
evidence hierarchy correctness
source contribution accuracy
extensible source registry correctness
context-specific evidence profile correctness
conflict-resolution outcome quality
notes_for_human
notes_for_gpt
```

Production calibration behavior must not change until explicitly designed, reviewed, and approved.

Evaluation must not be interpreted as a demand for 100% accuracy. It is used to measure reliability, failure modes, weak families, horizon/regime bias, overconfidence, underconfidence, and whether the proprietary inference indicator is useful enough for its intended review or trigger-candidate stage.

## 15. Parameter-set governance

Every family, feature, scenario component, and signal-strength mapping must use versioned parameter sets.

Rules:

```text
Parameter sets are horizon-aware.
Estimated signal-strength mapping is parameterized and replay-calibratable.
Evaluated versions are immutable.
Adjustments create new versions, not silent mutation.
GPT may propose changes.
Human approval is required for activation.
Replay/shadow comparison is required before activation.
Rollback target must be available for active versions.
```

Required lifecycle:

```text
draft -> candidate -> shadow -> paper -> active -> retired
```

## 16. GPT-readable artifacts

Prediction System must produce compact review artifacts for GPT/human review.

Candidate artifacts:

```text
prediction_run_summary.json
scenario_trace_digest.json
family_horizon_score_digest.json
signal_strength_calibration_digest.json
weak_family_report.md
parameter_comparison_digest.md
source_quality_digest.json
miss_reason_digest.md
near_miss_digest.md
calibration_review_packet.md
gpt_parameter_adjustment_proposal.md
human_parameter_review_record.md
```

Raw/full data must remain separate from compact GPT digests.

## 17. Missing mechanism proposals adopted as formal design requirements

The following mechanisms are adopted as formal design requirements unless superseded by a later explicit human-approved spec:

```text
1. Input coverage matrix: required sources, artifact path, owner, freshness, reliability, current implementation state.
2. Source contribution ledger: which source contributed to each scenario decision and with what quality state.
2A. Evidence hierarchy and conflict-resolution ledger: which tier dominated, which tiers supported/conflicted, and why signal strength was raised/capped.
3. TriggerEligibility state machine: blocked -> review_only_candidate -> shadow_candidate -> paper_candidate -> return_gate_ready, with blocked default.
4. Explanation contract separate from UI: human_narrative_ja and machine-readable reason fields live in Prediction System output, not WarRoom logic.
5. Revision graph: every refresh/rewrite links previous_prediction_run_id and explains changed families/horizons.
6. No-edge/conflict first-class handling: no_edge and conflicting_evidence are valid outputs with reasons.
7. Evaluation coverage gate: prediction cannot be called trigger-candidate-ready without sufficient evaluable samples by horizon/family/regime.
8. WarRoom packet schema: a stable read-only packet consumed by UI without recalculating meaning.
9. Parameter review packet: GPT proposal + human approval + replay/shadow comparison + rollback record.
10. Boundary guards: no Collector runtime imports, no AutoTrade append, no broker/private API, no WarRoom mutation controls.
11. Signal-strength percentage contract: 0 means prediction unavailable, 99 is maximum, 100 is forbidden, and the percentage must be evidence-derived and recalibratable.
12. Evidence hierarchy contract: Tier 0 source-quality gate, Tier 1 local executable-market truth, Tier 2 technical structure, Tier 3 cross-venue confirmation, Tier 4 derivatives context, Tier 5 macro/news/session context, Tier 6 AI/pro behavior hypothesis, Tier 7 replay/calibration prior.
13. Extensible reference-source registry contract: every new source declares tier, owner, artifact contract, quality policy, direction ownership, allowed effects, weight bounds, missing/stale/conflict behavior, WarRoom label, and reason codes.
14. Context-specific evidence profile contract: source priority and weight are selected per prediction card, family, horizon group, concrete horizon, regime, session, and risk context rather than as one global trust score.
```

## 18. Current official implementation sequence

Carry forward the PS-Q sequence:

```text
PS-Q2: source / artifact input coverage start
PS-Q3: provider reliability and source quality hardening
PS-Q4: feature construction from provided artifacts
PS-Q5: Scenario Prediction Core strengthening
PS-Q6: richer replay-data quality / evidence-quality expansion
PS-Q7: WarRoom prediction tab read-only display path
PS-Q8: AutoTrade trigger-candidate contract readiness
PS-Q9: explicit AutoTrade return gate / trigger integration design
```

Do not skip PS-Q2. Do not jump directly to WarRoom UI or AutoTrade trigger integration.

## Implementation workflow mandate

When implementing Prediction System slices, use the one-shot patch runner workflow.

Required workflow:

```text
1. Read target files first.
2. Briefly explain the change boundary.
3. Create tmp/work/<slice>/apply_<slice>.py or provide one copy-paste PowerShell block.
4. Make patches small and slice-based.
5. Make apply scripts idempotent and print [APPLIED] or [ALREADY APPLIED] where feasible.
6. Provide focused guard / close guard / git status commands together.
7. Do not ask the user to manually edit multiple files.
8. If a patch fails, create a minimal fix_<slice>.py from the logs instead of rewriting broadly.
9. Use pytest where reasonable.
10. Split implementation+confirmation and commit+gpt_room sync into separate steps, with GPT reviewing actual files between them.
```

Preferred command shape:

```powershell
cd C:\BtcTradeSystem
python .\tmp\work\<slice>\apply_<slice>.py
python .\tools\test_<focused_guard>.py
python .\tools\test_<close_guard>.py
git status --short
```

## 19. PS-Q8F implementation checkpoint and next-thread boundary

Updated: 2026-06-21 JST
Checkpoint commit: `a601442b`
Checkpoint state: `PS-Q8F human_observation_passed`
Working tree at checkpoint: clean

This checkpoint records the safe thread boundary after the first WarRoom-visible Prediction System UI insertion.

Completed by this checkpoint:

```text
PS-Q8A: UI mount catalog for the 12 Prediction WarRoom widget groups.
PS-Q8B: display-only UI mount presenter packet.
PS-Q8C: guarded WarRoom page insertion contract.
PS-Q8D: initial-collapsed read-only Prediction WarRoom mount review section inserted into warroom_page.py.
PS-Q8E: manual visual/UX verification contract.
PS-Q8F: human observation recorded as passed.
```

Human-observed WarRoom state:

```text
Prediction WarRoom mount review section is visible in WarRoom.
The section is initially collapsed.
After manual expansion, compact line is visible.
Compact line shows ready:true, entries:12, zones:3, blocked:0, render:false, page_mutation:false.
Zone summary rows are visible: overview=1, primary_live=4, operator_support=7.
Mount entry rows are visible.
No runtime operation, approval, authorization grant, loader control, file-read control, payload-decode control, AutoTrade control, or broker/private API control is visible in this section.
```

Important limitation:

```text
The visible PS-Q8F section is a mount/readiness review, not the live/current prediction card display.
Actual latest payload read is not implemented.
Actual payload decode is not implemented.
Actual schema validation of a hot/latest payload is not implemented.
Actual WarRoom prediction cards from current latest payload are not implemented.
AutoTrade trigger candidate advisory display is not implemented.
AutoTrade trigger execution/integration is not implemented.
```

Next safe implementation boundary:

```text
PS-Q9A: latest payload actual-read preflight final contract.
```

PS-Q9A must still be contract/preflight only. It should decide the exact artifact candidates, allowed path scope, freshness/size/schema requirements, blocked/warning behavior, and operator-visible readiness before any actual file read is enabled.

Do not begin PS-Q9B actual read until PS-Q9A is committed and guarded.

PS-Q9B, when eventually reached, must be a minimal read-only loader for explicitly allowed JSON artifacts only. It must not connect AutoTrade, broker/private APIs, command ledger append, approval/grant mutation, Collector runtime loops, or Prediction core collection ownership.
## 2026-07-08 parent inference engine common contract lock
<!-- PS_PARENT_INFERENCE_ENGINE_COMMON_CONTRACT_LOCK_2026_07_08 -->

The parent/common contract is fixed in:

```text
docs/strategy/PREDICTION_SYSTEM_PARENT_INFERENCE_ENGINE_COMMON_CONTRACT_2026-07-08.md
```

Key points:

```text
bitflyer_first_not_bitflyer_only=true
multi_source_ready=true
multi_prediction_family_ready=true
source_registry_required=true
prediction_family_registry_required=true
lead_lag_assumption_is_hypothesis_not_truth=true
source_reliability_calibratable=true
raw_external_data_duplication_forbidden=true
ui_displays_read_models_only=true
market_regime_first_canonical_family=true
```

This parent contract must be honored before adding external sources such as cross-exchange, derivatives, macro, FX, equities, gold, on-chain, session/calendar, news/event, or operator/manual review sources.
