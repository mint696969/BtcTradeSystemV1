# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q26Q_WARROOM_FOCUS_SECTION_RENDERER_2026-07-01.md
# desc: PS-Q26Q externalizes WarRoom focus folded-section rendering. Layout-only display-only UI wiring cleanup.
# PS-Q26Q WarRoom focus section renderer

Updated: 2026-07-01 JST
Base: PS-Q26P WarRoom secondary detail folding
Mode: WarRoom UI wiring cleanup / externalized focus section renderer / display-only / no runtime writes / no scheduler or producer enablement / no trading guidance

```text
ps_q26q_warroom_focus_section_renderer=true
base_reentry=PS_Q26P_WARROOM_SECONDARY_DETAIL_FOLDING_DONE
selected_lane=WARROOM_UI_VISUAL_TUNING_STRUCTURAL_CLEANUP
production_ui_code_changed=true
changed_file=btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py
externalized_section_renderer_file=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_focus_sections.py
warroom_page_change_boundary=import_and_focus_section_renderer_calls_only
section_renderer_externalized=true
uses_externalized_layout_policy_module=true
section_count=7
keeps_existing_panels_available=true
layout_only_change=true
read_only=true
display_only=true
non_executing=true
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
scheduler_enabled=false
producer_enabled=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
ledger_append=false
mode_apply=false
parameter_apply=false
would_send_to_broker=false
```

## Purpose

Q26O/Q26P moved expanded/collapsed defaults into `warroom_focus_layout_policy.py`. PS-Q26Q keeps going in the same direction by moving the folded-section render wrapper into `warroom_focus_sections.py`.

`warroom_page.py` now calls:

```text
render_warroom_focus_section("section_id")
```

instead of directly pairing labels with expanded defaults. This keeps the large page closer to composition/wiring and leaves layout behavior in small externalized modules.

## Safety boundary

This is a layout-only wiring cleanup. It does not read or write artifacts, trigger refreshes, enable producer/scheduler, change predictions, append ledger entries, call AutoTrade/broker APIs, or apply mode/parameter changes.
