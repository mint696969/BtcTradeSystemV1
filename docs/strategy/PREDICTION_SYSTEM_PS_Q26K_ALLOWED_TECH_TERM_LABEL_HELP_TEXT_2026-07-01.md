# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q26K_ALLOWED_TECH_TERM_LABEL_HELP_TEXT_2026-07-01.md
# desc: PS-Q26K allowed technical term label/help text. Display-only; preserves allowlist and Q18AP legacy searchable compatibility.
# PS-Q26K allowed technical term label/help text

Updated: 2026-07-01 JST
Base: PS-Q26J WarRoom review-candidate polish
Mode: display-only / allowed technical term helper wording / preserve allowlist / preserve legacy searchable compatibility / no trading guidance / no writes / no scheduler / no producer enablement

```text
ps_q26k_allowed_tech_term_label_help_text=true
base_reentry=PS_Q26J_WARROOM_REVIEW_CANDIDATE_POLISH_DONE
allowed_technical_terms_preserved=true
japanese_helper_wording_added=true
warroom_page_helper_rows_added=true
q18aj_helper_wording_added=true
q18ak_helper_wording_added=true
legacy_searchable_compatibility_preserved=true
q18ap_compatibility_preserved=true
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

Q26K keeps allowlisted technical terms visible but adds consistent Japanese helper wording so operator-facing rows explain what each term means.

## Preserved allowlist

```text
heartbeat = 画面更新確認時刻
fallback = 安全側の表示理由
runtime binding = 実データprops接続
AutoTrade = 自動売買トリガー
broker = broker/private API 接続
artifact = 生成済みファイル/成果物
fragment = 枠内だけの表示更新
```

## Safety boundary

This slice is display-only. It does not add trading guidance, trade signals, producer/scheduler behavior, artifact writes, AutoTrade, broker/private API, ledger, mode, or parameter action.
