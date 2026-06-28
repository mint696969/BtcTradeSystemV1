# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q23_ARTIFACT_LAYOUT_POLICY_2026-06-28.md
# desc: PS-Q23 no-write design for distributed prediction artifacts and monolithic latest mitigation.
# PS-Q23 prediction artifact layout policy

Updated: 2026-06-28 JST
Mode: no-write design / migration policy only

```text
ps_q23_artifact_layout_policy=true
monolithic_latest_mitigation=true
distributed_run_artifacts=true
latest_manifest_pointer=true
backward_compat_latest_retained=true
runtime_artifact_write_changed=false
broker_autotrade=false
```

## Problem

`D:\btc_ts_hot\prediction\latest_prediction_system_result.json` has become a multi-MB artifact and is still growing. A single large JSON file is hard for humans, GPT, UI read-models, diagnostics, tests, and recovery tools to handle. It also increases blast radius: one corrupt or partially written file can make many views unusable.

The repository currently has many direct references to `prediction/latest_prediction_system_result.json`, so a hard cutover is unsafe. PS-Q23 therefore chooses a compatibility-first migration.

## Design principles

```text
1 artifact = 1 responsibility
1 run = 1 immutable run_id directory
latest = pointer + thin summary, not the full body
status = small operator/GPT-readable state
records = JSONL partitions
trace/detail = sidecars
lineage/timings/warnings = separate small files
manifest = the canonical index for a run
compatibility latest remains until all readers migrate
```

## Target D-hot layout

```text
D:\btc_ts_hot\prediction\
  latest_prediction_system_result.json              # legacy compatibility, initially retained
  latest_manifest.json                              # thin pointer to current run
  status\
    non_ui_scheduled_producer_status.json           # small operational status
  runs\
    2026-06-28\
      061525_<run_id>\
        manifest.json                               # canonical run index
        summary.json                                # GPT/UI friendly summary
        forecast_batch_summary.json                 # counts, generated_at, versions
        forecast_records.jsonl                      # one record per line
        feature_summary.json                        # compact feature evidence
        input_refs.json                             # pointers to data inputs
        warnings.json                               # warning categories and samples
        lineage.json                                # producer/code/data lineage
        timings.json                                # duration/timing metrics
        safety.json                                 # non-executing/broker/autotrade flags
        checksums.json                              # optional hashes/sizes
  logs\
    q22x_silent_scheduler_launcher\YYYYMMDD\*.log
```

## File responsibility contract

| File | Responsibility | Size expectation |
| --- | --- | --- |
| `latest_manifest.json` | Points to the latest run and key sidecars | small, KB-scale |
| `status/non_ui_scheduled_producer_status.json` | Operator/GPT status and readiness | small, KB-scale |
| `runs/.../manifest.json` | Canonical index for one immutable run | small, KB-scale |
| `runs/.../summary.json` | UI/GPT quick read; no huge records | small to medium |
| `runs/.../forecast_records.jsonl` | Full forecast records | can grow, line-addressable |
| `runs/.../feature_summary.json` | Compact evidence summary | bounded |
| `runs/.../input_refs.json` | Input artifact references | bounded |
| `runs/.../warnings.json` | Warning rollups and samples | bounded |
| `runs/.../lineage.json` | Version/data lineage | bounded |
| `runs/.../timings.json` | Runtime durations | bounded |
| `latest_prediction_system_result.json` | Legacy compatibility only during migration | should stop growing long term |

## Migration stages

### Stage 0: policy only

No runtime writes change. Document the layout, add guards, and keep Q22S/Q21I behavior unchanged.

### Stage 1: dual-write sidecars

Q21I/Q22S continue writing the legacy latest file, but also write:

```text
prediction/latest_manifest.json
prediction/runs/YYYY-MM-DD/HHMMSS_<run_id>/manifest.json
prediction/runs/YYYY-MM-DD/HHMMSS_<run_id>/summary.json
prediction/runs/YYYY-MM-DD/HHMMSS_<run_id>/forecast_records.jsonl
...
```

Readers continue using legacy latest by default.

### Stage 2: reader preference switch

WarRoom/read-model tools first try `latest_manifest.json` and distributed sidecars. They fall back to legacy latest if manifest is missing or invalid.

### Stage 3: shrink legacy latest

After readers are migrated, legacy latest becomes a compatibility envelope:

```json
{
  "generated_at": "...",
  "run_id": "...",
  "latest_manifest_path": "prediction/latest_manifest.json",
  "summary_path": "prediction/runs/.../summary.json",
  "forecast_records_path": "prediction/runs/.../forecast_records.jsonl",
  "compatibility_note": "full records are in distributed sidecars"
}
```

### Stage 4: retention and compaction

Keep hot recent run directories in D-hot. Move/archive older run directories to E-cold under explicit retention policy. Never append unbounded history into one JSON file.

## Size policy

```text
status files: target < 100 KB
manifest files: target < 100 KB
summary files: target < 1 MB
JSONL record partitions: target < 50 MB each, split by family/horizon if needed
logs: date-partitioned
legacy latest: current compatibility allowed, long-term target < 1 MB
```

Hard failure is not required on size warnings at first, but diagnostics should emit warnings when a file crosses its size band.

## Compatibility rule

Existing paths remain valid during migration:

```text
prediction/latest_prediction_system_result.json
prediction/status/non_ui_scheduled_producer_status.json
```

Any reader migration must follow:

```text
try latest_manifest distributed layout
fallback to legacy latest
never silently return empty on oversized artifacts
report source_artifact_mode = distributed | legacy | blocked
```

## Atomicity rule

For each run:

```text
1. write sidecars into a temporary run directory
2. write run manifest last inside that run directory
3. atomically replace latest_manifest.json only after run manifest is complete
4. update legacy latest compatibility artifact according to migration stage
5. update status last
```

This ensures `latest_manifest.json` never points to a half-written run.

## Safety boundaries

PS-Q23 is storage layout only. It does not change trading boundaries.

```text
broker_private_api_allowed=false
autotrade_trigger_allowed=false
approval_or_ledger_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
would_send_to_broker=false
```

## Next implementation slice

PS-Q23A should add a read-only layout builder/validator that can derive a candidate manifest from the current legacy latest without writing D-hot runtime artifacts.
