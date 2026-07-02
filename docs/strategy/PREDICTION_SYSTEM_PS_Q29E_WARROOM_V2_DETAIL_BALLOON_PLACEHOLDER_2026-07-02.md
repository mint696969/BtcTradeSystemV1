# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29E_WARROOM_V2_DETAIL_BALLOON_PLACEHOLDER_2026-07-02.md
# desc: PS-Q29E WarRoom v2 prediction-card detail balloon placeholder policy.

# PS-Q29E WarRoom v2 detail balloon placeholder

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29D_WARROOM_V2_RENDERER_SPLIT_DONE
Slice: PS-Q29E_WARROOM_V2_DETAIL_BALLOON_PLACEHOLDER

## Decision

Add a dedicated placeholder detail-balloon renderer for WarRoom v2 prediction cards.

The renderer is display-only. It consumes placeholder read-model fields only: reasons, sources, warnings, invalidation conditions, topic, and connection flags. It does not read D-hot, invoke classifiers, handle push transport, or perform execution behavior.

## Added boundary

```text
prediction_warroom/panels/warroom_v2/card_detail_balloon.py
  prediction-card detail balloon placeholder renderer only

prediction_warroom/panels/warroom_v2/prediction_cards.py
  grid renderer delegates detail content to card_detail_balloon.py

prediction_warroom/v2/placeholder_read_models.py
  placeholder reason/source/warning/invalidation lines for prediction cards
```

## Non-goals

```text
not_connecting_dhot=true
not_invoking_classifier=true
not_enabling_websocket=true
not_enabling_sse=true
not_enabling_scheduler_or_producer=true
not_touching_autotrade_broker_ledger_mode_parameter=true
not_changing_app_route=true
not_changing_legacy_warroom=true
```
