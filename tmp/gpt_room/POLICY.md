# path: ./tmp/gpt_room/POLICY.md
# desc: Binding project operating policy for repository work, safety, observation continuity, and gpt_room durability.

# POLICY

Updated: 2026-07-11 JST
Status: current and binding

## 1. Highest-priority architecture rule

```text
responsibility_separation_first=true
folder_structure_reflects_responsibility_boundaries=true
single_file_overgrowth_forbidden=true
data_execution_config_ui_inference_io_separated=true
split_before_append_when_responsibility_diverges=true
```

Responsibility separation is a primary design constraint, not optional cleanup.

- A module, file, class, process, artifact, and directory must have a clear owner and bounded responsibility.
- Folder structure must make responsibility boundaries visible to a human operator.
- Data capture, storage, transformation, inference, configuration, execution, presentation, transport, and diagnostics must not be collapsed into one file or one layer.
- Do not keep appending unrelated behavior to a convenient existing file.
- When a file begins serving multiple responsibilities, split it along the natural boundary before adding more behavior.
- Prefer small cohesive modules over giant files, giant state objects, giant JSON records, and monolithic runners.
- Avoid both extremes: do not create meaningless one-function fragmentation, but do not accept oversized multi-responsibility files for convenience.
- The test structure should follow production responsibility boundaries.
- Data artifacts must be partitioned by role, source, timeframe, lifecycle, or owner where that improves replay, retention, and inspection.
- Runtime executables should orchestrate; they should not absorb domain logic, storage logic, UI logic, and safety policy into one script.

### Size guard

```text
preferred_file_size<=500_lines
review_split_boundary_at=500_lines
strong_warning_at=700_lines
```

Line counts are warning signals, not the sole design rule. A smaller file with mixed responsibilities is still wrong; a longer cohesive declarative table may be acceptable. The deciding criterion is responsibility clarity and operational maintainability.

## 2. Source of truth

- Repository files are the source of truth for code, architecture, formal specifications, tests, and current contracts.
- Conversation is working memory, not canonical memory.
- `tmp/gpt_room` stores only minimal persistent project memory.
- Formal specifications belong under repository `docs/`, not duplicated in gpt_room.
- Human controls profile switching. Never switch profiles automatically.

## 3. Work style

- Read target files before changing them.
- Work in small, verifiable responsibility-bounded slices.
- Prefer structural fixes over brittle wording, private-helper, formatting, or arbitrary line-count guards.
- Do not ask the user to edit files manually.
- Create idempotent runners under `tmp/work/<slice>/`.
- Runners print `[APPLIED]` or `[ALREADY APPLIED]`.
- On failure, inspect evidence and create a minimal `fix_<slice>.py`.
- Run focused guards first, then affected full suites at phase boundaries.
- Use `git diff --check` and `git status --short`.
- Commit only expected files after guards pass.
- Synchronize gpt_room when a checkpoint or operating policy changes.

## 4. Contract-change discipline

- Production behavior, current specification, current guards, affected tests, and handoff state change in the same slice.
- Historical contracts remain audit evidence; they are not automatic current guards.
- Do not use skip, xfail, exclusions, test weakening, or safety weakening merely to pass.
- Current guards should test public behavior, responsibility boundaries, safety invariants, schema, identity, traceability, and fallback behavior.

## 5. Project strategy

- Human and GPT are development partners.
- This system is microstructure, order-book, liquidity, and trade-flow oriented.
- Begin from high practical information density, then reduce only with evidence that market-state quality is preserved.
- Replay-grade data, timestamp integrity, sequence continuity, and source lineage matter.
- Current UI is a consumer, not the upstream architectural source of truth.
- Preserve future tuning points and replaceable policies; avoid architectural prison around temporary tactics.

## 6. Data-root roles

```text
hot_latest_live=D:\btc_ts_hot
cold_archive=E:\btc_ts
```

Use D-hot for latest runtime artifacts, Collector/UI current state, logs, and current prediction evidence. Use E cold for archive, replay, copy validation, and long-term retention.

## 7. Safety defaults

```text
broker_send=false
order_submit=false
autotrade_trigger=false
prediction_from_ui=false
classifier_from_ui=false
confidence_recalculation_in_ui=false
parameter_auto_promotion=false
live_parameter_apply=false
```

MarketRegime and other prediction families provide context and forecasts, not execution authorization.

## 8. gpt_room discipline

- `START.md` is the current human-readable entrypoint.
- `ENVIRONMENT_GUARDS.md` contains recurring cross-thread environment hazards and must be read at startup before patch generation.
- `CURRENT.json` is the current machine-readable state.
- `POLICY.md` is stable policy.
- `DECISIONS.md` contains only currently binding decisions.
- `reference/` holds generated indexes and reusable supporting material.
- `history/` holds completed, superseded, and archived material.
- Do not place dated one-off handoffs, worklogs, patch drafts, or backups in the active root.
- Do not scan history before current files.
- Do not recreate multiple competing current-state files.
<!-- MR_F9_OBSERVATION_GOVERNANCE_2026_07_17 -->
## Long-running observation continuity

For every active long-running observation, read:

```text
docs/strategy/PREDICTION_SYSTEM_LONG_RUNNING_OBSERVATION_AND_HOLD_RELEASE_POLICY_2026-07-17.md
tmp/gpt_room/OBSERVATION_CONTROL.md
```

Do not infer acceptance, restart, or hold release from conversation history or elapsed time. Follow the persisted checkpoint decision, next-check time, observation identity, and held-work register.
<!-- GPT_ROOM_GIT_DURABILITY_POLICY_2026_07_17 -->
## 9. gpt_room Git durability

`tmp/gpt_room` remains the active Action-compatible room root. Do not move or rename it without an explicit profile/backend migration.

The canonical current-memory files listed in `config/gpt_room_tracked_files.json` are Git-tracked despite the surrounding `tmp/` workspace being ignored.

Mandatory rules:

- Treat the manifest as the only allowlist for tracked gpt_room files.
- Keep generated indexes, history, backups, self-tests, logs, caches, and `tmp/work` untracked.
- After every checkpoint, closeout, or operating-policy change, update the relevant canonical room files in the same slice.
- Run `python scripts/check_gpt_room_persistence.py` before commit.
- Do not call a checkpoint durable while tracked room changes remain uncommitted.
- Disaster recovery requires commit plus push to a remote or another independent backup medium; a local commit alone is insufficient.
- After clone/restore, verify that the tracked files appear at the same `tmp/gpt_room/...` paths before starting repository work.
