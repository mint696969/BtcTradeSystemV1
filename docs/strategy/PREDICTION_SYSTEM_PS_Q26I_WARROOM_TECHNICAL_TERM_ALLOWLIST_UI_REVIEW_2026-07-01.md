# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q26I_WARROOM_TECHNICAL_TERM_ALLOWLIST_UI_REVIEW_2026-07-01.md
# desc: PS-Q26I WarRoom technical term allowlist and UI review audit. Audit-only; no production UI code changes, no trading guidance, no runtime enablement.
# PS-Q26I WarRoom technical term allowlist / UI review audit

Updated: 2026-07-01 JST
Base: PS-Q26H WarRoom top reading caption Japanese localization
Mode: audit-only / technical-term allowlist / UI review classification / no production UI changes / no trading guidance / no writes / no scheduler / no producer enablement

```text
ps_q26i_warroom_technical_term_allowlist_ui_review=true
base_reentry=PS_Q26H_WARROOM_TOP_READING_CAPTION_JAPANESE_LOCALIZATION_DONE
audit_only=true
technical_term_allowlist_recorded=true
ui_review_classification_recorded=true
production_ui_code_changed=false
legacy_searchable_compatibility_preserved=true
allowlist_hit_count_recorded=true
review_candidate_count_recorded=true
legacy_compat_count_recorded=true
trade_guidance_added=false
trade_signal_added=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
ledger_append=false
mode_apply=false
parameter_apply=false
scheduler_enabled=false
producer_enabled=false
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
would_send_to_broker=false
```

## Purpose

Q26I classifies remaining mixed technical terms after Q26A-Q26H. It does not modify production UI code. The audit prevents false positives by separating terms that should remain visible from text that should be localized later.

## Classification

```text
allowlist:
- heartbeat
- fallback
- runtime binding
- AutoTrade
- broker
- scheduler
- producer
- artifact
- fragment
- Streamlit
- latest prediction

legacy_compat:
- PS_Q18AP_SEARCHABLE_REFRESH_HEARTBEAT
- PS_Q18AP_SEARCHABLE_FRESHNESS_STATUS
- legacy searchable plain text functions

review_candidate:
- raw false fragments such as real_render=false / autotrade=false / broker=false / writes=false
- broad_page_reload when visible to operator
- display-only/current-state when shown without Japanese explanation
```

## Recommended next slice

```text
PS_Q26J_WARROOM_UI_REVIEW_REMAINING_REVIEW_CANDIDATE_POLISH_DISPLAY_ONLY
```

Q26J should reduce review-candidate items that are operator-visible while preserving allowlisted technical terms and Q18AP legacy searchable compatibility.

## Safety boundary

This slice is audit-only. It does not add trading guidance, trade signals, producer/scheduler behavior, artifact writes, AutoTrade, broker/private API, ledger, mode, or parameter action.
