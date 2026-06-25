# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q19J_WARROOM_PREDICTION_TEXT_CATALOG_SPLIT_2026-06-25.md
# desc: PS-Q19J design note for splitting WarRoom prediction bilingual text catalog from the panel.
# PS-Q19J WarRoom prediction text catalog split

Updated: 2026-06-25 JST
Branch: docs/phase2-handoff-sync
Base clean head: b50ebc53

## Purpose

PS-Q19J addresses language-file growth before adding more UI explanation work.

```text
ps_q19j_warroom_prediction_text_catalog_split=true
prediction_warroom_text_catalog_directory_added=true
latest_prediction_display_text_catalog_added=true
panel_imports_split_text_catalog=true
global_ui_text_not_expanded=true
common_texts_not_expanded=true
bilingual_behavior_preserved=true
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
scheduler_enabled=false
producer_enabled=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Design

WarRoom prediction-specific language resources now live under:

```text
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/texts/latest_prediction_display_texts.py
```

The panel remains responsible for rendering and small formatting helpers. The catalog module is text-only and has no Streamlit import, no runtime IO, and no execution behavior.

## Safety boundary

```text
read_only_ui_text_refactor=true
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
scheduler_enabled=false
producer_enabled=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
ledger_append_allowed=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
would_send_to_broker=false
```

## Next recommended step

Visually confirm WarRoom ja/en switch after this split, then resume the deferred non-UI periodic producer and source-quality gap audit.
