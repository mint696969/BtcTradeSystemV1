# path: ./tmp/gpt_room/DECISIONS.md
# desc: Persistent accepted MarketRegime decisions through MR-F8 closeout and MR-F9 handoff.

# MarketRegime Decisions

Updated: 2026-07-16 JST
Reference implementation HEAD: `e30a19a1`

## MR-F8 acceptance

- MR-F8 comparison architecture and fail-closed governance are accepted.
- Active candidate: `market_regime.future.transparent_baseline.params.v1`.
- Shadow candidate: `market_regime.future.transparent_baseline.params.conservative.v1`.
- Accepted decision: `insufficient_evidence`.
- No candidate was selected or promoted.
- Active remains the rollback candidate.
- Same-window and same-source comparison was verified for seven horizons and fourteen outcome rows.
- Missing probability, multi-origin churn, transition-delay, and full-horizon evidence was not inferred.
- MR-F8 has no remaining implementation task; evidence maturity is owned by named MR-F9 work.

## Promotion decision

- Development activity alone never promotes a model or parameter set.
- At least 30 observed slots and 20 percent coverage per candidate are required by the current policy.
- Shadow materiality requires at least 0.02 accuracy gain, with Brier regression at most 0.01, ECE regression at most 0.02, and UNKNOWN-rate increase at most 0.05.
- Meeting thresholds creates a review proposal only.
- Human approval, explicit rollback, and a separately guarded activation change remain mandatory.
- Auto-promotion and live parameter application remain forbidden.

## Prediction-execution trust decision

- The operator UI remains display-only. UI inference and confidence recalculation are forbidden.
- UI label variation is not evidence of correct upstream prediction.
- Each enabled horizon must expose its own trace identity, raw score or probability distribution, model and parameter identity, source snapshot, freshness, abstention decision, and fallback status.
- Repeated identical confidence values and persistent long-horizon UNKNOWN must be diagnosed upstream.
- Agreement across horizons is acceptable only when independent execution is traceable.
- MR-F9 acceptance requires proof of independent horizon-specific inference, not artificially different card values.

## Evidence policy

- Legacy evidence may be used only for fields it actually preserves.
- Missing probability distributions, source contributions, outcomes, or historical states must not be reconstructed by inference.
- Canonical ledger observations must obey target expiry and tolerance boundaries.
- Unresolved evidence remains explicitly unresolved.

## Safety decisions

```text
runtime_calibration_fit=false
runtime_card_confidence_replacement=false
scheduler=false
broker_private_api=false
autotrade=false
order_submission=false
parameter_auto_promotion=false
live_parameter_apply=false
D_hot_modified_by_closeout=false
UI_inference=false
```
## MR-F9 implementation checkpoint decision

- MR-F9 execution-evidence, maturation, diagnostic, human-review, paired execution, explicit fact, one-shot JSON, and immutable observation-request contracts are accepted as an implementation foundation through `5ef4c03c`.
- This is not MR-F9 closeout. `RW-MR-003`, `RW-MR-003A`, and `RW-MR-003B` remain open.
- Contract implementation does not prove mature multi-origin OOS evidence.
- Raw output may be used for Brier, log loss, or ECE only when upstream semantics explicitly identify a probability distribution.
- Missing observations, probability distributions, historical states, churn, or transition delay may not be inferred.
- The current candidate decision remains `insufficient_evidence`; selected candidate remains null; active remains rollback.
- Review approval artifacts never authorize runtime activation. A separately guarded change remains mandatory after any future approval.
- The next slice is bounded D-hot evidence discovery and analysis, not scheduler registration or automatic persistence.

## MR-F9 read-only execution path decision

- MR-F9 read-only execution tooling is accepted through `5ef4c03c`.
- The accepted path is MR-F8 runtime preflight -> immutable observation request -> explicit per-trace observation facts -> paired runtime execution bridge -> one-shot JSON result.
- The observation request intentionally leaves inference mode, raw-output semantics, freshness, source age, and fallback details unset.
- These fields must come from a trusted execution source and may not be inferred from forecast labels, display confidence, classifier diagnostics, or preflight structure.
- No scheduler, automatic writer, D-hot persistence, promotion, live apply, broker, AutoTrade, or order path was opened.
- This path does not constitute operational evidence maturity or MR-F9 closeout.

## MR-F9 UI semantics and final-thread decision

```text
next_slice=MR-F9.17
next_slice_name=runtime_forecast_source_truth_and_ui_semantics_audit
provisional_remaining_slices=13-14
short_horizon_65=stale_current_l4_fallback_with_65_cap
long_horizon_15=stale_long_horizon_unknown_with_fixed_15
independent_horizon_execution_proven=false
ui_display_semantics_repair_complete=false
shadow_promoted=false
mr_f9_complete=false
```

Canonical next-thread handoff: `docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F9_FINAL_THREAD_HANDOFF_2026-07-16.md`

## MR-F9 final-thread handoff commit decision

- The canonical final-thread handoff document was committed at `e30a19a1`.
- The handoff document intentionally records `dff165b9` as its pre-handoff reference baseline.
- Room reference state now points to the actual handoff commit.
- MR-F9.17 has not started. The working tree must remain clean at transfer.
<!-- MR_F9_OBSERVATION_GOVERNANCE_2026_07_17 -->
## Long-running observation governance

```text
canonical_policy=docs/strategy/PREDICTION_SYSTEM_LONG_RUNNING_OBSERVATION_AND_HOLD_RELEASE_POLICY_2026-07-17.md
canonical_live_state=tmp/gpt_room/OBSERVATION_CONTROL.md
elapsed_time_does_not_equal_acceptance=true
periodic_decision_receipts_required=true
collection_complete_separate_from_outcome_maturity=true
hold_release_requires_named_receipt=true
observation_semantic_runtime_change_requires_restart=true
poor_model_quality_is_not_automatic_evidence_invalidity=true
insufficient_evidence_is_valid_result=true
```

The first MR-F9 bounded 24-hour run is a production-path and evidence-pipeline qualification window, not automatic MarketRegime acceptance. Observation-affecting work may be implemented and tested offline but must not be applied to the running process until explicitly released or superseded.
<!-- MR_F9_19M_OPERATOR_COLLECTION_CLI_CLOSEOUT_2026_07_17 -->
## MR-F9.19M accepted boundary

```text
prepare_status_stop_only=true
start_not_implemented_fail_closed=true
D_hot_writer_not_invoked=true
scheduler_not_enabled=true
detached_process_not_started=true
broker_order_surface_absent=true
next_slice=MR-F9.19N_PRODUCTION_START_WIRING
```
<!-- MR_F9_19N_PRODUCTION_START_WIRING_CLOSEOUT_2026_07_17 -->
## MR-F9.19N accepted boundary

```text
exact_human_authorization_required=true
authorization_TTL_revalidated=true
root_binding_required=true
lease_preacquired=true
manifest_recovery_before_loop=true
planned_start_anchor_preserved=true
foreground_only=true
D_hot_start_not_executed=true
next_slice=MR-F9.19O
```
<!-- MR_F9_19O_PRODUCTION_PATH_REPO_TMP_QUALIFICATION_CLOSEOUT_2026_07_17 -->
## MR-F9.19O accepted boundary

```text
production_CLI_start_path_qualified_in_repo_tmp=true
normal_default_root_D_hot_unchanged=true
test_only_root_clock_sleep_injection=true
first_write_duplicate_stop_resume_recovery_lease_conflict_qualified=true
D_hot_start_not_executed=true
next_slice=MR-F9.19P
```
<!-- MR_F9_19P_D_HOT_READ_ONLY_PRESTART_GATE_CLOSEOUT_2026_07_17 -->
## MR-F9.19P accepted boundary

```text
D_hot_read_only_prestart_gate_accepted=true
existing_one_shot_is_outside_new_collection_window=true
existing_collection_control_or_lease=false
19P_candidate_authorization_reusable=false
fresh_plan_and_authorization_required_at_start=true
explicit_human_authorization_required=true
foreground_only=true
collection_24h_started=false
```
<!-- MR_F9_TERMINAL_LEASE_RELEASE_HARDENING_CLOSEOUT_2026_07_17 -->
## Terminal lease ownership decision

```text
terminal_collection_must_not_retain_lease=true
FAILED_CONTRACT_is_terminal=true
start_wrapper_must_release_on_loop_exception=true
failed_attempt_evidence_must_be_preserved=true
failed_attempt_control_directory_must_not_be_reused=true
retry_requires_new_collection_id=true
```
<!-- MR_F9_LIVE_24H_OBSERVATION_HANDOFF_2026_07_17 -->
## Live observation parallel-work decision

```text
running_process_identity_frozen=true
foreground_terminal_must_remain_open=true
parallel_read_only_work_allowed=true
MR_F10_offline_schema_and_interface_design_allowed=true
MR_F10_changes_must_not_be_loaded_by_running_process=true
observation_affecting_runtime_changes_held=true
trend_bias_still_blocked=true
```
