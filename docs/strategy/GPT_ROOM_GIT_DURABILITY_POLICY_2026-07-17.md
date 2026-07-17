# path: ./docs/strategy/GPT_ROOM_GIT_DURABILITY_POLICY_2026-07-17.md
# desc: Defines selective Git durability for the Action-compatible tmp/gpt_room project memory.

# gpt_room Git Durability Policy

Updated: 2026-07-17 JST
Status: binding

## Decision

Keep the active room at `tmp/gpt_room`. Do not move it merely to obtain Git tracking because the Action schema, profile resolution, bootstrap, room operations, and existing repository references depend on that location.

Selectively track only the canonical current-memory files declared in `config/gpt_room_tracked_files.json`. The rest of `tmp/` remains ignored.

## Durability boundary

```text
conversation=working_memory_only
tmp/gpt_room/canonical_allowlist=git_tracked_project_memory
tmp/gpt_room/generated_history_backup_selftest=ignored_workspace
tmp/work=ignored_patch_workspace
local_commit=local_recovery_only
remote_push_or_independent_backup=disaster_recovery
```

## Required workflow

1. Update canonical room state in the same slice as the checkpoint, closeout, or policy decision.
2. Run `python scripts/check_gpt_room_persistence.py`.
3. Inspect `git status --short` and commit every expected tracked room change.
4. Push to a remote or copy the repository to an independent backup medium.
5. After disaster recovery, verify the canonical files at their original `tmp/gpt_room/...` paths before starting work.

## Excluded material

Do not track generated indexes, semantic indexes, history, backups, `_selftest`, logs, caches, scratch runners, or arbitrary additional room files. Additions to the tracked set require an explicit manifest and policy change with guard coverage.

## Compatibility

This policy changes Git visibility only. It does not change the active profile, Action schema, `tmp_root`, `room_root`, bootstrap behavior, D-hot runtime, or long-running observation process.
