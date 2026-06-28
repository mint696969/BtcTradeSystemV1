# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q22W_RECURRING_FAILURE_PRESERVE_SUCCESS_2026-06-28.md
# desc: PS-Q22W recurring tick failure handling: preserve previous success, keep Q22V retry-ready, and expose Q21I failure summary.
# PS-Q22W recurring failure preserve success

Updated: 2026-06-28 JST
Base: Q22U scheduler enabled once, paused after recurring failure

```text
ps_q22w_recurring_failure_preserve_success=true
q22s_failure_preserves_previous_success=true
q22s_failure_records_q21i_summary=true
q22v_accepts_retryable_q22s_failure_status=true
scheduler_mutation_executed=false
latest_prediction_artifact_written=false
status_artifact_written_by_patch=false
broker_autotrade=false
```

## Why

The first scheduled Mountain2 tick succeeded and advanced latest/status. A later recurring tick failed in the Q21I bounded refresh stage and wrote a Q22S failure status that dropped `last_success_generated_at` to null. That made post-enable readiness unrecoverable without manual status repair.

PS-Q22W fixes the recurring failure semantics:

```text
1. Q22S captures pre-tick status before Q21I.
2. If Q21I is incomplete, Q22S writes failure status based on the pre-tick status.
3. Previous last_success_generated_at / last_prediction_run_id / target size are preserved.
4. Q22S records a compact q21i_result_summary for diagnosis.
5. Q22V accepts retryable Q22S failure status when prior success is preserved and failure_count < 3.
```

No scheduler mutation, broker, AutoTrade, ledger, parameter apply, latest write, or status write is performed by this patch.
