# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_TO_MR_F10_THREAD_HANDOFF_2026-07-18.md
# desc: Canonical thread handoff at the boundary immediately before MR-F10 offline stable-context design begins.

# MarketRegime MR-F9 → MR-F10 Thread Handoff

Updated: 2026-07-18 JST
Status: ready_for_new_thread
Checkpoint: MR_F9_PRE_F10_HANDOFF_READY
Reference HEAD: `54e374ddddbde41e8b2edc59406a013c2c5b9a97`

<!-- MR_F9_TO_MR_F10_THREAD_HANDOFF_2026_07_18 -->

## 1. Why this handoff exists

This thread intentionally ends immediately before MR-F10 implementation so the next GPT starts from a clean architectural boundary rather than inheriting conversational drift.

MR-F9 is not complete. Its replacement 24-hour collection and later outcome maturity remain active obligations. MR-F10 may begin only as offline, family-neutral schema/interface work that does not alter the running MarketRegime producer or close any MR-F9 evidence gate.

```text
thread_cut_reason=clean_phase_boundary_before_MR_F10
conversation_history_is_not_canonical=true
repository_and_gpt_room_are_canonical=true
later_phase_start_does_not_close_earlier_work=true
```

## 2. Successor GPT mandatory startup order

```text
1. project_bootstrap
2. tmp/gpt_room/ENVIRONMENT_GUARDS.md
3. tmp/gpt_room/START.md
4. tmp/gpt_room/OBSERVATION_CONTROL.md
5. tmp/gpt_room/CURRENT.json
6. tmp/gpt_room/08_STATUS.md
7. tmp/gpt_room/DECISIONS.md
8. this handoff
9. docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_FAMILY_ROADMAP_2026-07-11.md
10. docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_REMAINING_WORK_REGISTER_2026-07-14.md
11. docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_REPLACEMENT_24H_COLLECTION_START_RECEIPT_2026-07-18.md
12. docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_P1_RUNTIME_HORIZON_READ_MODEL_QUALIFICATION_2026-07-18.md
13. docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_P2_TRUST_FALLBACK_UNKNOWN_PREMATURITY_QUALIFICATION_2026-07-18.md
14. docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_P3_REVIEW_PROPOSAL_PREMATURITY_QUALIFICATION_2026-07-18.md
```

Before any patch, re-read D-hot state and lease for the active replacement collection. Do not trust the latest counters in this document as live truth.

## 3. Repository position

```text
branch=docs/phase2-handoff-sync
reference_head=54e374ddddbde41e8b2edc59406a013c2c5b9a97
working_tree_at_handoff=clean
P1_commit=8bdbc2bc8d9a446060e37d99e795b3136dbf5cbd
sparse_candle_fix_commit=fead05b6c24e458d54a5758f908b93d413de99f6
incident_receipt_commit=a784526cd913f60c2afbd655a535d7ac52f9983d
replacement_schedule_commit=1f6c1101b0657b9b44f3b3947cbd903eb4cb7704
P2_commit=2af49cd5382e91215d4f69afb3764c31b30ae15f
P3_commit=54e374ddddbde41e8b2edc59406a013c2c5b9a97
```

## 4. Active MR-F9 replacement collection

```text
collection_id=mr-f9-24h-5be7ba757eac727bab10
plan_sha256=beb94ca14825c848d0bc97cd6953c55b99a080c53fa1bdf4eb6f44238cfed617
runtime_pid=20176
lease_id=4283ab4f0e27b0337072c623bcf2b40f
repository_commit_under_test=a784526cd913f60c2afbd655a535d7ac52f9983d
planned_start_utc=2026-07-18T04:14:00Z
planned_start_jst=2026-07-18T13:14:00+09:00
checkpoint_6h_utc=2026-07-18T10:14:00Z
checkpoint_6h_jst=2026-07-18T19:14:00+09:00
checkpoint_12h_utc=2026-07-18T16:14:00Z
checkpoint_12h_jst=2026-07-19T01:14:00+09:00
checkpoint_18h_utc=2026-07-18T22:14:00Z
checkpoint_18h_jst=2026-07-19T07:14:00+09:00
planned_end_utc=2026-07-19T04:14:00Z
planned_end_jst=2026-07-19T13:14:00+09:00
final_outcome_maturity_not_before_utc=2026-07-20T04:14:00Z
final_outcome_maturity_not_before_jst=2026-07-20T13:14:00+09:00
```

Latest state observed while preparing this handoff:

```text
observed_state_updated_at=2026-07-18T06:17:00Z
status=RUNNING
active=true
iteration_count=124
written_origin_count=0
readiness_skip_count=124
error_count=0
last_error=
last_skip_reason=future_origin_contiguous_sixty_candles_unavailable
```

The zero-write state is not currently an error. Valid absent-candle gaps prevent a contiguous 60-candle window; the accepted fix converts this known condition to `READINESS_SKIP` rather than terminal failure.

## 5. Live observation safety rules

```text
Terminal_A_must_remain_open=true
Ctrl_C_forbidden=true
second_collection_producer_forbidden=true
lease_recovery_forbidden_while_live=true
manual_state_rewrite_forbidden=true
old_failed_collection_restart_forbidden=true
Collector_restart_forbidden_without_explicit_decision=true
scheduler_enabled=false
detached_process_started=false
broker_private_api_allowed=false
order_submission_allowed=false
auto_promotion_allowed=false
live_parameter_apply_allowed=false
```

The foreground CLI is intentionally quiet during the loop. Health is proven by increasing `iteration_count`, advancing `updated_at`, live lease heartbeat, `status=RUNNING`, `active=true`, and `error_count=0`.

## 6. What MR-F9 already qualified

```text
P1 runtime artifact -> family-neutral read model:
  complete
  8 horizons / 8 digest matches
  no prediction, classification, confidence recalculation, source merge, mount, or D-hot write

P2 trust / fallback / UNKNOWN prematurity:
  accepted
  fallback reason and source ref required
  UNKNOWN and unavailable remain unresolved/unpromoted
  digest tamper fails closed
  24 focused tests passed

P3 review / proposal prematurity:
  accepted
  premature evidence => insufficient_evidence
  review => BLOCKED_INSUFFICIENT_EVIDENCE
  blocked review cannot receive decision link
  no runtime activation, promotion, or live apply
  15 focused tests passed
```

## 7. MR-F9 obligations that remain open

```text
RW-MR-003:
  replacement 24h collection completion
  longest-horizon maturity
  mature multi-origin outcome resolution
  calibration and condition summaries
  churn and transition-delay analysis

RW-MR-003A:
  actual full-inference vs fallback rates by horizon
  raw probability/score continuity across real origins
  fixed-confidence persistence diagnostic
  stale recurrence and long-horizon UNKNOWN diagnostic
  independent horizon execution proof from mature evidence

RW-MR-003B:
  minimum 30 observed slots and 20 percent coverage
  balanced accuracy and macro F1
  Brier score, log loss, ECE
  winner/tie/insufficient proposal from mature evidence
  human review trail

UI follow-up:
  collection lane is not yet directly page-wired
  current D-hot MarketRegime prediction push is absent
  artifact selector fallback is not directly page-wired
```

No successor may mark MR-F9 complete merely because MR-F10 starts.

## 8. MR-F10 motivation

MR-F10 creates the stable family-neutral context boundary that later prediction families consume without importing MarketRegime implementation details.

The architectural goal is dependency inversion:

```text
MarketRegime implementation details
  -> MarketRegime-owned projection
  -> immutable versioned family-neutral context
  -> later-family consumer interfaces
```

This prevents MarketRegime from becoming a parent engine or god object while allowing TrendBias and later families to consume regime context safely.

## 9. MR-F10 required contract

The first accepted schema must expose at least:

```text
current_regime
current_state_reliability
state_age
state_stability
change_point_probability
future_regime_distribution_by_horizon
transition_risk
volatility_context
liquidity_context
source_quality_context
invalidation_hints
trace_refs
```

Required semantics:

```text
versioned=true
immutable=true
family_neutral=true
UNKNOWN_preserved=true
abstention_preserved=true
source_freshness_preserved=true
trace_identity_preserved=true
no_raw_market_payload=true
no_MarketRegime_internal_type_leakage=true
no_trade_permission_surface=true
no_UI_inference=true
no_confidence_recalculation=true
```

## 10. MR-F10 first slice

```text
slice_id=MR_F10_OFFLINE_STABLE_CONTEXT_CONTRACT_DESIGN
scope:
  define schema and validators
  define MarketRegime projection boundary
  define UNKNOWN/abstention/source-quality semantics
  define immutable trace references
  add TrendBias consumer fixture only
  add focused contract tests

out_of_scope:
  D-hot writer
  live producer integration
  UI page wiring
  WebSocket publishing
  broker or order path
  runtime parameter changes
  MR-F9 metric completion
```

Recommended first reads for implementation ownership:

```text
btcts_next/src/btcts/prediction/common/family_read_model.py
btcts_next/src/btcts/prediction/market_regime/runtime_horizon_read_model.py
btcts_next/src/btcts/prediction/market_regime/contracts.py
btcts_next/src/btcts/prediction/market_regime/future_execution_evidence.py
btcts_next/src/btcts/prediction/market_regime/future_shadow_outcome.py
```

The successor must verify these paths against repository truth before relying on them.

## 11. MR-F10 acceptance direction

```text
stable_context_schema_versioned=true
MarketRegime_projection_tested=true
TrendBias_consumer_fixture_tested=true
implementation_leakage_absent=true
UNKNOWN_and_abstention_tested=true
trace_continuity_tested=true
no_trade_permission_tested=true
no_D_hot_write_tested=true
no_runtime_application=true
```

MR-F10 acceptance is not the MarketRegime family closeout. After MR-F10, RW-MR-005 integration/hardening/closeout remains mandatory, followed by explicit `MARKET_REGIME_READY_FOR_NEXT_FAMILY` acceptance.

## 12. Immediate successor decision

```text
current_phase=MR-F9 monitoring + MR-F10 offline design
current_gate=MR_F9_PRE_F10_HANDOFF_READY
next_gate=MR_F10_OFFLINE_STABLE_CONTEXT_CONTRACT_DESIGN
first_action=read_only_live_collection_health_check
second_action=read_MR_F10_contract_owners
third_action=create_small_offline_schema_slice
MR_F10_runtime_application_allowed=false
trend_bias_family_implementation_allowed=false
```
