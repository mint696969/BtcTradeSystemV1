# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q19O_MACRO_SESSION_CONTEXT_INPUT_REPAIR_OR_DECISION_2026-06-25.md
# desc: PS-Q19O design note for explicit neutral macro/session context defaults.
# PS-Q19O Macro/session context input repair or decision

Updated: 2026-06-25 JST
Branch: docs/phase2-handoff-sync
Base clean head: 33f6a12a

## Decision

PS-Q19O chooses an explicit neutral/context-only default for macro/session context rather than adding external macro/calendar collection now.

This is intentional: the current goal is to stabilize WarRoom realtime prediction observation without expanding Collector scope, external API scope, or runtime write behavior.

```text
ps_q19o_macro_session_context_input_repair_or_decision=true
macro_session_decision=explicit_neutral_context_only_default
macro_context_neutral_default_supplied=true
session_calendar_context_neutral_default_supplied=true
macro_context_source_quality_status_mapped=true
session_calendar_context_source_quality_status_mapped=true
neutral_context_provider_family_mapped=true
external_macro_api_added=false
external_session_calendar_api_added=false
collector_behavior_changed=false
hot_file_read_scope_changed=false
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
scheduler_enabled=false
producer_enabled=false
warroom_ui_trigger_enabled=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Change

- `source_quality.py` maps `macro_context` and `session_calendar_context` to `prediction_neutral_context_default` provider family.
- Q10D builder adds `SourceQualityStatus` entries for `macro_context` and `session_calendar_context` from an in-memory neutral default timestamp.

These entries mean: no macro/session incident is currently supplied by a real external source, so the Prediction System treats the context as explicitly neutral/context-only instead of missing.

## Safety boundary

```text
read_only=true
non_executing=true
context_only=true
external_macro_api_added=false
external_session_calendar_api_added=false
collector_behavior_changed=false
hot_file_read_scope_changed=false
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
scheduler_enabled=false
producer_enabled=false
warroom_ui_trigger_enabled=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
ledger_append_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Expected result

After PS-Q19O and one PS-Q19K producer cycle, PS-Q19K gap audit should show `missing_macro_context=0`, `missing_session_calendar_context=0`, and context-profile minimum-source caps should reduce or disappear. Remaining warnings should be market/technical interpretation warnings, not missing input coverage warnings.
