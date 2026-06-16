# path: ./gpt_room/runbook/PROJECT_STATE.md
# desc: Runbook for restoring project context across GPT threads.
# Project State Runbook

## Start Here

Use phase2 as the current development baseline.

Verified checkpoint:

- branch: phase2
- HEAD: 0e615c31
- remote sync: phase2...origin/phase2 = 0 0
- tests: 247 passed

## Important Recent PRs

- PR #1: Complete AutoTrade parameter bundle readiness chain
- PR #2: Fix phase2 pytest discovery hygiene

## Current Roadmap Position

The project is past the AutoTrade parameter bundle readiness wiring checkpoint.

Next work should focus on:

1. Pre-live operational validation
2. Paper/readiness verification
3. Operator UI AutoTrade closeout review
4. Optional GitHub Actions CI setup

## Guardrails

- Do not assume live broker execution is enabled.
- Treat AutoTrade changes as readiness, audit, and visibility infrastructure.
- Verify broker-send boundaries before any live execution work.
- In this thread, Repo Action read/write status has not been confirmed; PowerShell logs are the current source of truth.
