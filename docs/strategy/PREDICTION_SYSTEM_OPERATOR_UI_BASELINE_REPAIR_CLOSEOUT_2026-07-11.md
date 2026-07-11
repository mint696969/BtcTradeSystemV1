# path: ./docs/strategy/PREDICTION_SYSTEM_OPERATOR_UI_BASELINE_REPAIR_CLOSEOUT_2026-07-11.md
# desc: Records the operator UI stale-contract baseline repair, full-suite evidence, and recurrence-prevention policy.

# Prediction System Operator UI Baseline Repair Closeout

Updated: 2026-07-11 JST
Checkpoint: OPERATOR_UI_BASELINE_REPAIR_ACCEPTED

<!-- PS_OPERATOR_UI_BASELINE_REPAIR_CLOSEOUT_2026_07_11 -->

```text
operator_ui_full_suite_clean=true
operator_ui_test_count=1164
prediction_full_suite_clean=true
prediction_test_count=272
collection_errors=0
ignored_tests=0
skip_or_xfail_added=false
production_runtime_code_changed=false
historical_contracts_preserved=true
current_guards_synchronized=true
```

## 1. Scope

This slice repairs the stale operator UI baseline exposed after MR-VS5.

The starting state was:

```text
operator_ui_all collection blocker=1
operator_ui_without_q29c problems=31
prediction_all problems=0
```

The repair updates tests and current contract documents only. It does not change production runtime behavior.

## 2. Repaired contract groups

```text
WarRoom v2 route:
  fixed English label -> localized route label
  legacy page key -> warroom_v2 redirect

Legacy WarRoom ownership:
  broad v2 import prohibition -> receiver-only v2.push_widgets ownership
  v2 page, classifier, broker, and AutoTrade ownership remain prohibited

Q29C:
  historical preview shell guard -> current RT visible mount guard

MarketRegime classifier:
  ps_q27z.v1 runtime expectation -> ps_q27z.v3
  missing horizon -> UNKNOWN / 15% / STALE / MISSING fail-closed
  historical v1 document markers preserved

Default launch:
  bitFlyer direct endpoint -> D-hot unified market state default
  extra exchange websocket remains disabled by default

Market state reader:
  single-part private reader -> bounded sharded JSONL tail reader

WarRoom refresh and mount:
  single cockpit fragment -> section fragment refresh
  chart iframe remains outside fragment refresh
  old WP direct mount assertions -> modular render_rt_* ownership
  runtime environment ownership -> runtime_env.py

Module separation:
  brittle line-count threshold -> renderer ownership and safety-boundary guards
```

## 3. Data-availability behavior

Missing horizon labels are not treated as an implementation failure.

The current classifier contract is:

```text
label_selection_reason=forecast_horizon_label_missing
selected_label=""
selected_label_source=none
regime=UNKNOWN
confidence_percent=15
freshness=STALE
evidence_quality=MISSING
```

No other horizon label is silently reused.

## 4. Safety boundary

The repaired guards continue to prohibit:

```text
prediction invocation from UI render path
classifier invocation from UI render path
broker/private API action
order submission
AutoTrade enablement
ledger append
browser page reload
websocket send from observation-only UI
```

Receiver-only observation mounts and artifact reads remain allowed.

## 5. Recurrence-prevention policy

Historical documents remain historical evidence. They are not automatically treated as current runtime guards.

Current contract changes must update, in the same slice:

```text
production implementation
current contract document
current automated guard
full operator UI suite
full prediction suite when prediction contracts are affected
```

Current guards should prefer:

```text
responsibility and ownership boundaries
machine-readable safety flags
public API behavior
versioned runtime behavior
fail-closed behavior
```

Current guards should avoid relying solely on:

```text
fixed display wording
private helper implementation names
obsolete route labels
historical version constants
arbitrary source-line limits
```

## 5.1 Reusable policy

The reusable repository-wide policy extracted from this repair is:

`docs/strategy/PREDICTION_SYSTEM_CONTRACT_CHANGE_AND_TEST_GUARD_POLICY_2026-07-11.md`

This closeout remains the incident evidence; the policy document is the current reusable rule for future contract changes.

## 6. Verification evidence

```text
focused route and ownership slice=62 passed
Q29C current RT mount=5 passed
route ownership plus Q29C=67 passed
Q29A Q29B and classifier slice=40 passed
individual contract slice=19 passed
RT structure slice=17 passed
operator UI full suite=1164 passed
prediction full suite=272 passed
git diff --check=passed
```

All full-suite runs were executed without test exclusions.

## 7. Change boundary

```text
operator UI tests changed=29
current strategy documents changed=2
closeout document added=1
production runtime code changed=0
```

No `skip`, `xfail`, or collection exclusion was added to obtain a passing result.

## 8. Closeout decision

```text
operator_ui_collection_blocker_resolved=true
operator_ui_existing_31_problems_resolved=true
operator_ui_baseline_clean=true
prediction_baseline_clean=true
historical_current_contract_boundary_documented=true
operator_ui_baseline_repair_close_guard_accepted=true
```
