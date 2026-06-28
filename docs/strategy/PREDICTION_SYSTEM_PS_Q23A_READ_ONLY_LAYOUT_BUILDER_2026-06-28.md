# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q23A_READ_ONLY_LAYOUT_BUILDER_2026-06-28.md
# desc: PS-Q23A read-only builder/validator for distributed prediction artifact layout.
# PS-Q23A read-only distributed artifact layout builder

Updated: 2026-06-28 JST
Base policy: PS-Q23 distributed artifact layout policy
Mode: read-only diagnostic / no D-hot writes

```text
ps_q23a_read_only_layout_builder=true
reads_legacy_latest=true
builds_candidate_manifest=true
builds_candidate_sidecar_plan=true
writes_d_hot_runtime_artifacts=false
backward_compat_latest_retained=true
broker_autotrade=false
```

## Purpose

PS-Q23A inspects the current legacy artifact:

```text
D:\btc_ts_hot\prediction\latest_prediction_system_result.json
```

It derives a candidate distributed layout without writing it:

```text
prediction/latest_manifest.json
prediction/runs/YYYY-MM-DD/HHMMSS_<run_id>/manifest.json
prediction/runs/YYYY-MM-DD/HHMMSS_<run_id>/summary.json
prediction/runs/YYYY-MM-DD/HHMMSS_<run_id>/forecast_batch_summary.json
prediction/runs/YYYY-MM-DD/HHMMSS_<run_id>/forecast_records.jsonl
prediction/runs/YYYY-MM-DD/HHMMSS_<run_id>/warnings.json
prediction/runs/YYYY-MM-DD/HHMMSS_<run_id>/lineage.json
prediction/runs/YYYY-MM-DD/HHMMSS_<run_id>/timings.json
prediction/runs/YYYY-MM-DD/HHMMSS_<run_id>/safety.json
prediction/runs/YYYY-MM-DD/HHMMSS_<run_id>/checksums.json
```

The tool does not create those files. It reports the plan and estimated sizes only.

## Validation goals

```text
legacy latest exists and parses
forecast_batch is present
record_count can be derived
run_id can be derived from prediction_run_id or generated_at
candidate run directory is deterministic
candidate latest_manifest is small
records are planned as JSONL, not embedded in summary
summary excludes full records
safety flags remain non-executing
```

## Safety

```text
latest_prediction_artifact_written=false
status_artifact_written=false
latest_manifest_written=false
run_sidecars_written=false
broker_private_api_allowed=false
autotrade_trigger_allowed=false
approval_or_ledger_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
would_send_to_broker=false
```

## Next step

If PS-Q23A confirms the layout is feasible, PS-Q23B can implement gated dual-write sidecars while preserving the legacy latest artifact.
