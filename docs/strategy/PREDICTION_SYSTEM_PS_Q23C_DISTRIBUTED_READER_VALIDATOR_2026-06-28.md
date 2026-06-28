# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q23C_DISTRIBUTED_READER_VALIDATOR_2026-06-28.md
# desc: PS-Q23C read-only validator for distributed prediction artifacts with legacy fallback.
# PS-Q23C distributed reader validator

Updated: 2026-06-28 JST
Base policy: PS-Q23 / PS-Q23A / PS-Q23B
Mode: read-only reader validator / no runtime writes

```text
ps_q23c_distributed_reader_validator=true
prefers_latest_manifest=true
reads_distributed_sidecars=true
fallback_to_legacy_latest=true
freshness_arbitration_against_legacy_latest=true
source_artifact_mode=distributed_or_legacy_fallback
writes_d_hot_runtime_artifacts=false
broker_autotrade=false
```

## Purpose

PS-Q23C validates the read path for the distributed artifact layout created by PS-Q23B.

Preferred path:

```text
prediction/latest_manifest.json
  -> prediction/runs/.../manifest.json
  -> prediction/runs/.../summary.json
  -> prediction/runs/.../forecast_batch_summary.json
  -> prediction/runs/.../forecast_records.jsonl
  -> prediction/runs/.../safety.json
  -> prediction/runs/.../checksums.json
```

Fallback path:

```text
prediction/latest_prediction_system_result.json
```

The validator does not write or repair any runtime artifact.

## Validation contract

```text
latest_manifest exists and parses
run_dir is a safe relative path
all required sidecars exist
summary record_count matches forecast_records.jsonl line count
forecast_batch_summary record_count matches forecast_records.jsonl line count
manifest record_count matches latest_manifest record_count when present
safety flags remain non-executing
legacy latest fallback remains available
distributed sidecars are not older than legacy latest when both are available
```

## Output contract

The validator reports:

```text
source_artifact_mode = distributed | legacy_fallback | blocked
distributed_reader_ready = true | false
legacy_fallback_ready = true | false
record_count
generated_at
summary_path
forecast_records_path
blockers
warnings
```

## Safety

```text
latest_prediction_artifact_written=false
status_artifact_written=false
latest_manifest_written=false
run_sidecars_written=false
runtime_artifact_write_enabled=false
broker_private_api_allowed=false
autotrade_trigger_allowed=false
approval_or_ledger_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
would_send_to_broker=false
```

## Next step

After PS-Q23C is green, PS-Q23D can introduce manifest-first reader preference into selected read-model/diagnostic paths while retaining fallback to the legacy latest artifact.
