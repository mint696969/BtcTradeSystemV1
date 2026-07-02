# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29H_WARROOM_V2_SCENARIO_PLACEHOLDER_COMPOSITION_2026-07-02.md
# desc: PS-Q29H WarRoom v2 Japanese scenario placeholder composition policy.

# PS-Q29H WarRoom v2 scenario placeholder composition

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29G_WARROOM_V2_MATRIX_VISUAL_SCROLL_POLISH_DONE
Slice: PS-Q29H_WARROOM_V2_SCENARIO_PLACEHOLDER_COMPOSITION

## Decision

Add a placeholder Japanese scenario composition contract below the WarRoom v2 card matrix.

The scenario area reads the matrix shape, not live data:

```text
row_axis=prediction_item
column_axis=horizon
horizons=現在,5分後,15分後,30分後,60分後,6時間後,12時間後,24時間後
scenario_area_below_cards=true
scenario_source=placeholder_matrix_contract
```

It summarizes the intended future reading flow: integrate item rows such as 地合い, 方向感, 反転候補, ボラ警戒, 流動性, ブレイク/だまし, 市場間確認, and 人間テクニカル across the current-to-24h horizon axis.

## Non-goals

```text
not_connecting_dhot=true
not_invoking_classifier=true
not_enabling_websocket=true
not_enabling_sse=true
not_enabling_scheduler_or_producer=true
not_touching_autotrade_broker_ledger_mode_parameter=true
not_changing_app_route=true
not_changing_warroom_v2_page=true
not_changing_legacy_warroom=true
```
