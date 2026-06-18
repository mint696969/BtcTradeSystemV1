# path: ./docs/architecture/OPERATOR_UI_DECISION_POLICY_GATE_READ_ONLY_RENDERING_PLAN_2026-06-18.md
# desc: Design/status-only rendering plan for future Operator/UI visibility of the decision ledger policy gate. No Streamlit rendering, command buttons, runtime wiring, decision append, mode apply, grant execution, writes, or broker behavior.

# Operator/UI Decision Policy Gate Read-Only Rendering Plan

Updated: 2026-06-18 JST  
Profile: BtcTradeSystem  
Branch context: docs/phase2-handoff-sync  
Status: design-only / non-rendering / non-executing

## 1. Purpose

S143 introduced `AutoTradeDecisionLedgerIntegrationPolicyGate` as a read-only policy/status gate. S144 introduced a reusable Operator/UI display packet. S145 cataloged that display packet. S146 added a dashboard registry visibility packet.

S147 defines the future rendering plan only:

```text
A future Operator/UI section may show decision-ledger policy gate visibility,
but only as read-only status,
without command buttons,
without runtime wiring,
and without authorizing decision append.
```

This document does not implement rendering and does not modify runtime code.

## 2. Inputs allowed for future rendering

Future rendering may consume only already-built packets:

```text
AutoTradeDecisionLedgerIntegrationPolicyGate.to_dict()
build_autotrade_decision_ledger_policy_gate_display_packet(...)
build_decision_policy_gate_dashboard_registry_visibility_packet(...)
```

The future rendering section must not build live Shadow decisions, run snapshot pipelines, or resolve runtime write paths.

## 3. Proposed section order

A future read-only section may use this order:

```text
1. Header: Decision Ledger Policy Gate
2. Safety state: blocked/display-only/non-executing
3. Operator policy acknowledgement state
4. Explicit operator approval state
5. Decision append allowance: false
6. live_shadow.py behavior change allowance: false
7. persist=True allowance: false
8. Required approvals
9. Required guards
10. Non-permissions
11. Blockers/warnings
12. Registry visibility: health / future-widget pages
13. Source metadata: source_key / source_type / display_packet_builder
```

## 4. Safe labels

The UI labels should be explicit and defensive:

```text
DISPLAY ONLY
READ ONLY
NON EXECUTING
DECISION APPEND NOT AUTHORIZED
PERSIST TRUE NOT AUTHORIZED
LIVE SHADOW CHANGE NOT AUTHORIZED
BROKER EXECUTION NOT AUTHORIZED
NO COMMAND BUTTONS
```

These are labels only. They are not controls.

## 5. Fields safe to display

Safe display fields from the display packet:

```text
gate_available
display_state
gate_state
gate_id
generated_at
requested_scope
source_preflight_id
source_context_id
preflight_state
context_state
operator_policy_acknowledged
explicit_operator_approval
decision_ledger_integration_allowed
decision_append_allowed
live_shadow_behavior_change_allowed
persist_true_allowed
required_approvals
required_guards
non_permissions
blockers
warnings
compact_line
snapshot_lines
```

Safe display fields from registry visibility packet:

```text
registry_available
source_entry_available
source_entry.source_key
source_entry.source_type
source_entry.display_packet_module
source_entry.display_packet_builder
visible_pages
visible_page_count
health_page_visible
future_widget_page_visible
display_source_keys_for_page
```

## 6. Required future rendering constraints

Future rendering code, if explicitly implemented later, must preserve:

```text
read_only_contract=True
non_executing=True
not_runtime_wiring=True
not_ui_rendering=False only inside the actual rendering module, never in source packets
no_command_buttons=True
decision_append_allowed=False
decision_ledger_integration_allowed=False
live_shadow_behavior_change_allowed=False
persist_true_allowed=False
would_append_shadow_decision=False
would_apply_mode=False
would_execute_prearmed_grant=False
would_write_runtime_artifact=False
would_write_preview_status_artifact=False
would_send_to_broker=False
broker_execution_requested=False
mode_apply_requested=False
command_ledger_append_requested=False
approval_append_requested=False
```

The rendering module must never flip packet flags to authorize action.

## 7. Explicit non-permissions

S147 does not permit:

```text
Streamlit rendering implementation
UI command buttons
forms or toggles that request approval
runtime wiring
append_decision_jsonl usage
Shadow decision append
persist=True path
live_shadow.py behavior modification
run_shadow_decision_from_snapshot modification
run_latest_market_state_shadow_decision modification
build_action_candidate modification
mode apply
Pre-Armed grant execution
broker execution
real orders
private API calls
external API calls
collector import
runtime path creation
artifact write
approval append
command ledger append
watchdog/autonomous execution loop
market manipulation/spoofing/abusive order behavior
```

## 8. Future guard requirements

Any future rendering slice must guard:

```text
no command button tokens
no append_decision_jsonl token
no persist=True token
no live_shadow import
no broker/private API/external API/collector import
source packets remain read-only/non-executing
rendering can only display already-built packets
rendering cannot call build_decision_ledger_integration_policy_gate with operator approval flags
rendering cannot call any shadow decision runner
```

## 9. Operator meaning

For the operator, the future display should answer:

```text
Is the policy gate visible? Yes/no.
Is decision append authorized? No.
Is live_shadow.py behavior change authorized? No.
Is persist=True permitted? No.
Which approvals would be required later?
Which guards would be required later?
Which pages can discover this display packet?
```

## 10. Decision

S147 chooses a design/status-only rendering plan. The next safe implementation slice, if continued, should still avoid actual command controls and should only implement a static read-only rendering stub after explicit guard coverage.
