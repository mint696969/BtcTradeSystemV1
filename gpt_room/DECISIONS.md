# path: ./gpt_room/DECISIONS.md
# desc: Persistent decision log for BTC-TS GPT handoff state.
# Decisions

## 2026-06-16: phase2 is current baseline

- phase2 is the active development baseline after PR #1 and PR #2.
- Verified HEAD: 0e615c31
- Verified tests: 247 passed

## 2026-06-16: AutoTrade parameter bundle readiness is merged

- Parameter bundle runtime, readiness, UI visibility, mode recheck, and mode-state audit chain are merged into phase2.
- This work is readiness/audit/visibility infrastructure.
- This does not mean live broker execution is enabled.

## 2026-06-16: pytest discovery hygiene is fixed

- Root pytest.ini was added.
- Default pytest discovery is restricted to btcts_next/src/btcts.
- Scratch/runtime directories are excluded from default collection.

## 2026-06-16: continuation policy

- Use gpt_room files as the cross-thread handoff source.
- Use PowerShell logs as source of truth when Repo Action read/write is not confirmed in this thread.
- Before live execution work, verify broker-send boundaries explicitly.
