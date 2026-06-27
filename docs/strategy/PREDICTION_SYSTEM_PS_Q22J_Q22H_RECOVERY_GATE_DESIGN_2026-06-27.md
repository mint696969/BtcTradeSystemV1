# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q22J_Q22H_RECOVERY_GATE_DESIGN_2026-06-27.md
# desc: PS-Q22J designs a no-write recovery gate so Q22H can restore Q22E status observation after Q21ZC without Q22G/Q22F circular dependency.
# PS-Q22J Q22H recovery gate design

Updated: 2026-06-27 JST
Base head: f386d697

```text
ps_q22j_q22h_recovery_gate_design=true
read_only_no_write=true
current_q22h_requires_q22g_ready=true
q22g_requires_q22f_status_only_observation=true
q21zc_refresh_can_remove_q22e_status_marker=true
cycle_break_design_required=true
future_q22h_recovery_mode_should_allow_q22e_status_writer_when_q21x_ready=true
scheduler_enablement_allowed_now=false
recurring_enablement_allowed_now=false
```

Purpose:

After Q22I commit, Q21ZC freshness restore safely refreshed latest/status but changed the status producer version back to the manual-refresh path. That removed the Q22E status-only observation. Q22H could not restore it directly because Q22H requires Q22G ready, and Q22G requires Q22F/Q22E status-only observation. We recovered manually by running Q22E status-only first, then Q22H exact.

Q22J is a no-write design slice for the structural fix: future Q22H should have an explicit recovery gate that can restore Q22E status observation from a Q21ZC-refreshed success status without first requiring Q22G/Q22F readiness.

Design rule:

```text
Normal Q22H path may keep Q22G ready requirement.
Recovery Q22H path may bypass Q22G only when:
  repo clean
  Q21X ready
  latest/status success observed
  status producer_state is manual_refresh_exported_status_written
  last_success_generated_at and last_prediction_run_id are present
  Q22E writer is available
  both exact tokens are supplied
Then call Q22E success-preserving status writer once.
Never write latest prediction.
Never enable scheduler or add triggers.
Never call broker/AutoTrade.
Verify Q21X and Q22I after the status-only recovery write.
```
